from typing import Any, Mapping
import asyncio
import datetime as dt
from decimal import Decimal
from importlib import resources
import json

from graphql import (
    GraphQLField,
    GraphQLObjectType,
    GraphQLInterfaceType,
    GraphQLResolveInfo,
)
from ariadne import (
    load_schema_from_path,
    make_executable_schema,
    SchemaDirectiveVisitor,
    FallbackResolversSetter,
    ScalarType,
    UnionType,
)
from ariadne.graphql import GraphQLError
from ariadne.asgi import GraphQL
from ariadne.asgi.handlers import GraphQLHTTPHandler, GraphQLTransportWSHandler
from ariadne.types import Extension, SchemaBindable

from .auth_utils import (
    get_token_from_header,
    get_user_from_token,
    JWTAuthBackend,
    AuthCredentials,
)


# Directives


class NoAuthenticationDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
        self,
        field: GraphQLField,
        object_type: GraphQLObjectType | GraphQLInterfaceType,
    ) -> GraphQLField:
        field.__require_authentication__ = False
        return field

    def visit_object(self, object_: GraphQLObjectType) -> GraphQLObjectType:
        object_.__require_authentication__ = False
        return object_


class NeedPermissionDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
        self,
        field: GraphQLField,
        object_type: GraphQLObjectType | GraphQLInterfaceType,
    ) -> GraphQLField:
        if (
            self.args["strict"]
            or object_type.name == "Mutation"
            or object_type.name == "Subscription"
        ):
            field.__require_scope__ = self.args["scope"]
        else:
            field.__hide_noscope__ = self.args["scope"]
        return field

    def visit_object(self, object_: GraphQLObjectType) -> GraphQLObjectType:
        if self.args["strict"]:
            object_.__require_scope__ = self.args["scope"]
        else:
            object_.__hide_noscope__ = self.args["scope"]
        return object_


class EditableDirective(SchemaDirectiveVisitor):
    def visit_object(self, object_: GraphQLObjectType) -> GraphQLObjectType:
        object_.__editable__ = self.args["scope"]
        return object_


class DBModelDirective(SchemaDirectiveVisitor):
    def visit_object(self, object_: GraphQLObjectType) -> GraphQLObjectType:
        object_.__modelname__ = self.args["model_name"]
        return object_


class AllFilterDirective(SchemaDirectiveVisitor):
    def visit_object(self, object_: GraphQLObjectType) -> GraphQLObjectType:
        object_.__all_filter__ = True
        return object_


class FilterDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
        self,
        field: GraphQLField,
        object_type: GraphQLObjectType | GraphQLInterfaceType,
    ) -> GraphQLField:
        field.__filter__ = True
        return field


class NoFilterDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
        self,
        field: GraphQLField,
        object_type: GraphQLObjectType | GraphQLInterfaceType,
    ) -> GraphQLField:
        field.__filter__ = False
        return field


class FieldDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
        self, field: GraphQLField, object_type: GraphQLObjectType | GraphQLInterfaceType
    ) -> GraphQLField:
        caption = self.args["caption"]
        if caption:
            field.__caption__ = caption
        return field


# Middleware


class HideResult(BaseException):
    pass


def check_permission(info: GraphQLResolveInfo):
    if info.field_name not in ("__schema", "__typename"):
        request = info.context["request"]
        field = info.parent_type.fields[info.field_name]

        # Check for Authentication
        if hasattr(field, "__require_authentication__"):
            needs_auth = field.__require_authentication__
        elif hasattr(info.parent_type, "__require_authentication__"):
            needs_auth = info.parent_type.__require_authentication__
        else:
            needs_auth = True

        if needs_auth and not request.user.is_authenticated:
            raise GraphQLError(message="Requires Authentication")

        # check for Strict Permission
        if hasattr(field, "__require_scope__"):
            needs_scope = field.__require_scope__
        elif hasattr(info.parent_type, "__require_scope__"):
            needs_scope = info.parent_type.__require_scope__
        else:
            needs_scope = None

        if needs_scope is not None and needs_scope not in request.auth.scopes:
            raise GraphQLError(message=f"Requires Scope: {needs_scope}")

        # check for Loose Permission
        if hasattr(field, "__hide_noscope__"):
            hide_noscope = field.__hide_noscope__
        elif hasattr(info.parent_type, "__hide_noscope__"):
            hide_noscope = info.parent_type.__hide_noscope__
        else:
            hide_noscope = None

        if hide_noscope is not None and hide_noscope not in request.auth.scopes:
            raise HideResult()


async def check_permission_middleware(resolver, obj, info: GraphQLResolveInfo, **args):
    try:
        check_permission(info)
    except HideResult:
        return None

    # Return resolver
    if asyncio.iscoroutinefunction(resolver):
        return await resolver(obj, info, **args)
    else:
        return resolver(obj, info, **args)


class CollectErrorsExtension(Extension):
    def has_errors(self, errors, context) -> None:
        context["request"].state.errors = errors


# Custom Scalars


model_types = UnionType("ModelTypes")


@model_types.type_resolver
def resolve_model_types(obj, *_):
    return obj.__typename


date_scalar = ScalarType("Date")


@date_scalar.serializer
def serialize_date(value: dt.date | dt.datetime):
    if isinstance(value, dt.datetime):
        value = value.date()
    return value.isoformat()


@date_scalar.value_parser
def parse_date(value: str):
    return dt.date.fromisoformat(value)


datetime_scalar = ScalarType("DateTime")


@datetime_scalar.serializer
def serialize_datetime(value: dt.datetime):
    if type(value) is dt.date:
        raise GraphQLError("Cannot convert Date Type into DateTime")
    return value.isoformat()


@datetime_scalar.value_parser
def parse_datetime(value: str):
    return dt.datetime.fromisoformat(value)


json_scalar = ScalarType("Json")


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (dt.date, dt.datetime)):
            return obj.isoformat()
        return super(CustomEncoder, self).default(obj)


@json_scalar.serializer
def serialize_json(value: dict):
    return json.dumps(value, cls=CustomEncoder)


@json_scalar.value_parser
def parse_json(value: str):
    return json.loads(value)


# Fallback Resolver


def strict_default_field_resolver(source: Any, info: GraphQLResolveInfo, **args: Any) -> Any:
    """Strict Default field resolver.
    Same as default but raise Error when atrribute doesn't exist instead of returning None
    """
    field_name = info.field_name
    try:
        value = getattr(source, field_name)
    except AttributeError:
        try:
            value = source[field_name]
        except (KeyError, TypeError):
            raise GraphQLError(
                f"Attribute '{field_name} does not exist on {info.parent_type.name} object"
            )

    if callable(value):
        return value(info, **args)
    return value


class StrictFallbackResolverSetter(FallbackResolversSetter):
    def add_resolver_to_field(self, _: str, field_object: GraphQLField) -> None:
        if field_object.resolve is None:
            field_object.resolve = strict_default_field_resolver


def on_websocket_connect(websocket, payload: Any):
    """Alternative to Header authentication if cookie auth cannot be used"""
    if not isinstance(payload, Mapping) or "Authorization" not in payload:
        return
    token = get_token_from_header(payload["Authorization"])

    for middleware in websocket.scope["app"].user_middleware:
        auth_backend = middleware.options.get("backend")
        if isinstance(auth_backend, JWTAuthBackend):
            user = get_user_from_token(token, auth_backend.secret)
            websocket.scope["user"] = user
            websocket.scope["auth"] = AuthCredentials(user.scopes)
            break


# Exported


def create_graphql(schema_path, bindables: list[SchemaBindable], debug: bool):
    fallback_resolvers = StrictFallbackResolverSetter()
    type_defs = load_schema_from_path(schema_path)
    with resources.path("st_microservice", "base.graphql") as common_filename:
        type_defs_common = load_schema_from_path(common_filename)

    schema = make_executable_schema(
        [type_defs, type_defs_common],
        bindables,
        model_types,
        date_scalar,
        datetime_scalar,
        json_scalar,
        fallback_resolvers,
        directives={
            "no_authentication": NoAuthenticationDirective,
            "need_permission": NeedPermissionDirective,
            "editable": EditableDirective,
            "db_model": DBModelDirective,
            "all_filter": AllFilterDirective,
            "filter": FilterDirective,
            "no_filter": NoFilterDirective,
            "field": FieldDirective,
        },
    )

    return GraphQL(
        schema,
        debug=debug,
        http_handler=GraphQLHTTPHandler(
            middleware=[check_permission_middleware],
            extensions=[CollectErrorsExtension],
        ),
        websocket_handler=GraphQLTransportWSHandler(on_connect=on_websocket_connect),
    )
