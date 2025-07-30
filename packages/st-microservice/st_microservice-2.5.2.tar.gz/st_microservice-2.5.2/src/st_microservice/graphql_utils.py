from collections.abc import Sequence
from dataclasses import asdict
from typing import TypedDict, Callable
import sys
import asyncio
import csv
from io import StringIO
import decimal
from enum import Enum
from datetime import date, datetime
from urllib.request import urlopen

from ariadne import QueryType, MutationType, SubscriptionType
from asyncpg.exceptions import UniqueViolationError
from graphql import (
    GraphQLError,
    GraphQLResolveInfo,
    GraphQLObjectType,
    GraphQLEnumType,
    get_named_type,
    is_scalar_type,
    is_wrapping_type,
)
from pyparsing import ParseException

from .database import DBInterface
from .filter_parser import (
    number_filter_parser,
    date_filter_parser,
    datetime_filter_parser,
    boolean_filter_parser,
)
from .graphql_app import check_permission, HideResult
from . import models_functions as f
from .models_functions import set_dataclass_attribute
from .models_functions.functions import handle_json_fields
from .models_utils import BaseModel, ValueEnum
from .querybuilder import (
    Select,
    Column,
    Cast,
    Exists,
    Unnest,
    Like,
    PositionalParameter,
    Term,
    Descending,
)
from .request_utils import get_db, get_user


class FieldFilter(TypedDict):
    field_name: str
    value: str


class FileUpload(TypedDict):
    data_url: str | None
    filename: str


class ColumnOrder(TypedDict):
    name: str
    descending: bool


class TableControls(TypedDict):
    filters: list[FieldFilter]
    limit: int | None
    offset: int | None
    descending: bool
    order_by: list[Column | Descending] | None


def process_controls(model: type[BaseModel], controls: dict) -> TableControls:
    res: TableControls = {
        "filters": controls.get("filters", []),
        "limit": controls.get("limit"),
        "offset": controls.get("offset"),
        "descending": controls.get("descending", False),
        "order_by": None,
    }
    order_by_raw: list[ColumnOrder] | None = controls.get("order_by")
    if order_by_raw is not None:
        new_order_by = []
        for col_order in order_by_raw:
            try:
                new_col = getattr(model, col_order["name"])
                if not isinstance(new_col, Column):
                    raise AttributeError
            except AttributeError:
                raise GraphQLError(
                    f"Model {model.__name__} does not have column {col_order['name']}"
                )
            new_order_by.append(Descending(new_col) if col_order["descending"] else new_col)
        res["order_by"] = new_order_by
    return res


def data_url_to_bytes(file: FileUpload) -> bytes:
    with urlopen(file["data_url"]) as response:
        return response.read()


def get_csv_line_reader(file_upload: FileUpload):
    file = StringIO(data_url_to_bytes(file_upload).decode("utf-8"))
    return csv.reader(file)


def get_csv_dict_reader(file_upload: FileUpload) -> csv.DictReader:
    file = StringIO(data_url_to_bytes(file_upload).decode("utf-8"))
    return csv.DictReader(file)


# Resolver Tools


async def get_or_gql_error[T: BaseModel](db: DBInterface, model: type[T], **primary_keys) -> T:
    """Primary keys need to be real values"""
    row = await f.get(db, model, **primary_keys)
    if row is None:
        raise GraphQLError(
            f"Could not get {model.__name__} with keys {', '.join(f'{pk[0]}={pk[1]}' for pk in primary_keys.items())}"
        )
    return row


def separate_filters(filters: list[FieldFilter], field_names_to_separate: list[str]):
    """When some filters are automatically handled, and others you need to write custom SQLAlchemy queries"""
    newfilters = []
    separated = []
    for filt in filters:
        if filt["field_name"] in field_names_to_separate:
            separated.append(filt)
        else:
            newfilters.append(filt)
    return newfilters, separated


def _unwrap_gql_type(type_):
    temp_type = type_
    while is_wrapping_type(temp_type):
        temp_type = temp_type.of_type
    return temp_type


def _get_gql_type(info: GraphQLResolveInfo, type_name: str) -> GraphQLObjectType:
    """Raises Exception if not found"""
    gqltype = info.schema.get_type(type_name)
    if gqltype is None or not isinstance(gqltype, GraphQLObjectType):
        raise GraphQLError(f"Could not find GraphQL Object type {type_name}")
    return gqltype


def _get_model_from_gql_type(
    gqltype: GraphQLObjectType, models_dict: dict[str, type[BaseModel]]
) -> type[BaseModel] | None:
    model_name = getattr(gqltype, "__modelname__", gqltype.name)
    return models_dict.get(model_name)


def _editable_allowed(info: GraphQLResolveInfo, gqltype: GraphQLObjectType) -> bool:
    required_scope = getattr(gqltype, "__editable__", None)
    if required_scope is None:
        return False
    return required_scope in get_user(info).scopes


# Complete Resolvers


def setup_query(query_type: QueryType, model_list: list[type[BaseModel]]):
    models_dict = {model.__name__: model for model in model_list}

    def resolve_type_inspector(_, info: GraphQLResolveInfo, type_name: str):
        gqltype = _get_gql_type(info, type_name)
        model = _get_model_from_gql_type(gqltype, models_dict)

        # Primary Keys. Raise error when using directive and model not found, else ignore
        if model is not None:
            primary_keys = model.__metadata__.primary_keys
            editable = _editable_allowed(info, gqltype)
        else:
            if hasattr(gqltype, "__modelname__"):
                raise GraphQLError(f"Could not find model with name {gqltype.__modelname__}")
            # Continue without having a database model
            primary_keys = None
            editable = False

        all_filter = hasattr(gqltype, "__all_filter__")
        field_details = []
        for field_name, field in gqltype.fields.items():
            caption = getattr(field, "__caption__", field_name.title().replace("_", " "))
            dataclass_field = (
                model.__metadata__.dataclass_fields.get(field_name) if model is not None else None
            )
            is_database = dataclass_field is not None
            is_scalar = is_scalar_type(_unwrap_gql_type(field.type))
            field_gql_type = get_named_type(field.type)

            if field_gql_type is None:
                raise GraphQLError(f"Cannot get data type of field {field}")
            elif is_scalar:
                field_data_type = field_gql_type.name.upper()
            else:
                field_data_type = "OBJECT"

            # Handle filter type
            field_filter_type = None
            if getattr(field, "__filter__", is_database or all_filter):  # If has filter
                if field_gql_type is None:
                    raise Exception("Can only filter on Named Types")
                if field_gql_type.name == "String":
                    field_filter_type = "STRING"
                elif field_gql_type.name in ["Int", "Float"]:
                    field_filter_type = "NUMBER"
                elif field_gql_type.name in ["Date", "DateTime"]:
                    field_filter_type = "DATE"
                elif field_gql_type.name == "Boolean":
                    field_filter_type = "BOOLEAN"
                elif isinstance(field_gql_type, GraphQLEnumType):
                    field_filter_type = "STRING"  # Consider Enum as strings
                elif field_gql_type.name == "Json":
                    pass  # Keep None
                else:
                    raise GraphQLError(
                        f"Type {field_gql_type.name} cannot support filtering on field {field_name}"
                    )

            field_details.append(
                {
                    "field_name": field_name,
                    "caption": caption,
                    "is_database": is_database,
                    "is_scalar": is_scalar,
                    "data_type": field_data_type,
                    "filter_type": field_filter_type,
                }
            )

        return {
            "field_details": field_details,
            "primary_keys": primary_keys,
            "editable": editable,
        }

    async def resolve_get_object(_, info, type_name: str, primary_keys: dict):
        gqltype = _get_gql_type(info, type_name)
        model = _get_model_from_gql_type(gqltype, models_dict)
        if model is None:
            raise GraphQLError(f"Could not find database model for GraphQL Object {type_name}")
        db = (model.__metadata__.registry.db_connection_factory or get_db)(info)
        primary_keys = handle_json_fields(model, primary_keys)
        obj = await f.get(db, model, **primary_keys)
        if obj is None:
            return None
        obj.__typename = type_name
        return obj

    async def resolve_load_objects(_, info, type_name: str, controls: dict):
        gqltype = _get_gql_type(info, type_name)
        model = _get_model_from_gql_type(gqltype, models_dict)
        if model is None:
            raise GraphQLError(f"Could not find database model for GraphQL Object {type_name}")

        q = load_from_model_query(model, **process_controls(model, controls))

        recs = await (model.__metadata__.registry.db_connection_factory or get_db)(info).fetch(
            *q.to_sql()
        )

        objs = f.build_all(model, recs)
        for obj in objs:
            obj.__typename = type_name
        return objs

    query_type.set_field("type_inspector", resolve_type_inspector)
    query_type.set_field("get_object", resolve_get_object)
    query_type.set_field("load_objects", resolve_load_objects)


def setup_mutation(mutation_type: MutationType, model_list: list[type[BaseModel]]):
    models_dict = {model.__name__: model for model in model_list}

    def get_model_and_check_scope(info: GraphQLResolveInfo, type_name: str) -> type[BaseModel]:
        gqltype = _get_gql_type(info, type_name)

        if not _editable_allowed(info, gqltype):
            raise GraphQLError("Editing object not allowed")
        model = _get_model_from_gql_type(gqltype, models_dict)
        if model is None:
            raise GraphQLError(f"Could not find database model for GraphQL Object {type_name}")
        return model

    async def resolve_insert_object(_, info: GraphQLResolveInfo, type_name: str, payload: dict):
        model = get_model_and_check_scope(info, type_name)
        payload = handle_json_fields(model, payload)

        obj = model(**payload)
        try:
            await f.insert(
                (model.__metadata__.registry.db_connection_factory or get_db)(info),
                model,
                obj,
            )
        except UniqueViolationError:
            raise GraphQLError("Object already exists")
        # Maybe reload from database?
        return payload

    async def resolve_delete_object(_, info: GraphQLResolveInfo, type_name: str, payload: dict):
        """Payload is primary keys"""
        model = get_model_and_check_scope(info, type_name)
        payload = handle_json_fields(model, payload)
        db = (model.__metadata__.registry.db_connection_factory or get_db)(info)
        obj = await f.get(db, model, **payload)
        if obj is None:
            return None
        await f.delete(db, model, **payload)
        return asdict(obj)

    async def resolve_edit_object(_, info: GraphQLResolveInfo, type_name: str, payload: dict):
        """Payload is primary keys, and fields to edit
        {primary_keys: {[field_name: str]: Any}, fields: {[field_name: str]: Any}]"""
        model = get_model_and_check_scope(info, type_name)
        try:
            primary_keys = handle_json_fields(model, payload["primary_keys"])
            fields = handle_json_fields(model, payload["fields"])
        except KeyError as e:
            raise GraphQLError(f"Error decoding payload '{e}' missing")

        db = (model.__metadata__.registry.db_connection_factory or get_db)(info)
        obj = await f.get_or_error(db, model, **primary_keys)
        for field_name, field_value in fields.items():
            set_dataclass_attribute(obj, field_name, field_value)
        await f.update(db, model, obj, **primary_keys)
        # Maybe reload from database?
        return asdict(obj)

    mutation_type.set_field("insert_object", resolve_insert_object)
    mutation_type.set_field("delete_object", resolve_delete_object)
    mutation_type.set_field("edit_object", resolve_edit_object)


def apply_filter_to_query(q: Select, column: Column, field_type, value) -> Select:
    try:
        if field_type is str:
            return q.where(Like(column, PositionalParameter(value) if q.use_parameters else value))
        elif issubclass(field_type, ValueEnum) or issubclass(field_type, Enum):
            return q.where(
                Like(
                    # cast used to make Enum behave like strings.
                    Cast(column, "varchar"),
                    PositionalParameter(value) if q.use_parameters else value,
                )
            )
        elif field_type in [int, float, decimal.Decimal]:
            return number_filter_parser(q, column, value)
        elif field_type is date:
            return date_filter_parser(q, column, value)
        elif field_type is datetime:
            return datetime_filter_parser(q, column, value)
        elif field_type is bool:
            return boolean_filter_parser(q, column, value)
        raise GraphQLError(f"Cannot filter on column type {field_type}")
    except ParseException as e:
        raise GraphQLError(
            f"Cannot parse value: {value} for field {column} of type {field_type} [{e}]"
        )


def load_from_model_query(
    model: type[BaseModel],
    *,
    filters: Sequence[FieldFilter] | None = None,
    limit: int | None = None,
    offset: int | None = None,
    descending: bool | None = None,
    order_by: Sequence[Term] | None = None,  # None for primary key ordering, [] for no ordering
    init_query: Select | None = None,
    query_modifier: Callable[[Select], Select] | None = None,
) -> Select:
    # Init query
    q = Select(model).select_main_columns() if init_query is None else init_query
    # Apply filter
    filters = [] if filters is None else filters
    for filt in filters:
        full_name = filt["field_name"]
        value = filt["value"]

        *relation_names, col_name = full_name.split(".")
        current_model = model
        for relation_name in relation_names:
            # Join relationship, then get relation model
            q.join_relation(current_model, relation_name)
            current_model = f.get_relation_model(current_model, relation_name)

        # Deducing filter type by model column type. Contrary to resolve_type_inspector.
        column: Column = getattr(current_model, col_name)
        field_type = f.get_field_main_type(current_model, col_name)

        if f.is_field_list_type(current_model, col_name):  # Handle lists
            unnested_table = Unnest(column, alias=col_name + "_unnested", column_names=["col1"])
            q.where(
                Exists(
                    apply_filter_to_query(
                        Select(unnested_table, q.db_type).select_all(),
                        unnested_table.columns[0],
                        field_type,
                        value,
                    )
                )
            )
        else:
            apply_filter_to_query(q, column, field_type, value)

    # Apply query modifiers
    if query_modifier is not None:
        query_modifier(q)

    # Apply order by
    if order_by:
        q.order_by(*order_by)
    elif order_by is None and not q.is_ordered:
        q.order_by(
            *(f.table(model).columns_map[pkname] for pkname in model.__metadata__.primary_keys)
        )

    if descending:
        q.invert_order_by()

    # Apply limit and offsets
    if limit is not None:
        q.limit(limit)
    if offset is not None:
        q.offset(offset)
    return q


def simple_table_resolver_factory[T: BaseModel](
    model: type[T], query_modifier: Callable[[Select], Select] | None = None
):
    async def simple_table_resolver(_, info, controls: dict) -> list[T]:
        q = load_from_model_query(
            model,
            **process_controls(model, process_controls(model, controls)),
            query_modifier=query_modifier,
        )
        db = (model.__metadata__.registry.db_connection_factory or get_db)(info)
        return f.build_all(model, await db.fetch(*q.to_sql()))

    return simple_table_resolver


# Subscription tools


def subscription_permission_check(generator):
    async def new_generator(obj, info, *args, **kwargs):
        try:
            check_permission(info)
        except HideResult:
            yield None
            return

        async for res in generator(obj, info, *args, **kwargs):
            yield res

    return new_generator


# noinspection PyProtectedMember
def assign_simple_resolver(sub_object: SubscriptionType):
    def simple_resolver(val, *_, **__):
        return val

    for sub_field_name in sub_object._subscribers:
        if sub_field_name not in sub_object._resolvers:
            sub_object.set_field(sub_field_name, simple_resolver)


# External executors


async def external_module_executor(module_name, *args: str):
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-u",
        "-m",
        f"scripts.{module_name}",
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    while not proc.stdout.at_eof():
        data = await proc.stdout.readline()
        yield data.decode().rstrip()

    error = await proc.stderr.read()
    if error:
        raise GraphQLError(error.decode().rstrip())


async def external_script_executor(script_name, *args: str):
    proc = await asyncio.create_subprocess_exec(
        script_name,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    while not proc.stdout.at_eof():
        data = await proc.stdout.readline()
        yield data.decode().rstrip()

    error = await proc.stderr.read()
    if error:
        raise GraphQLError(error.decode().rstrip())
