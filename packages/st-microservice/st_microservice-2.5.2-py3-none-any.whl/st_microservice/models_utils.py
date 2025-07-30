from dataclasses import is_dataclass, field, fields, Field
from typing import Callable, dataclass_transform

from graphql import GraphQLResolveInfo

from . import querybuilder as qb
from .database import DBInterface


class ValueEnum:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattr__(self, item):
        return self.__dict__[item]

    def __getitem__(self, item):
        return self.__dict__[item]


class Registry:
    def __init__(
        self,
        db_type: qb.DBTypes = qb.DBTypes.POSTGRESQL,
        schema_name: str | None = None,
        db_connection_factory: Callable[[GraphQLResolveInfo], DBInterface] | None = None,
    ):
        self.db_type = db_type
        self.schema_name = schema_name
        self.db_connection_factory = db_connection_factory
        self.models: list[type[BaseModel]] = []


class ModelMetaData:
    def __init__(
        self,
        registry: Registry,
        table_name: str,
        primary_keys: list[str],
        table: qb.Table,
        dataclass_fields: dict[str, Field],
    ):
        self.registry = registry
        self.table_name = table_name
        self.primary_keys = primary_keys
        self.table = table
        self.dataclass_fields = dataclass_fields

        self.relations: dict[str, Relation] = {}


class BaseModel(qb.ModelInterface):
    __metadata__: ModelMetaData


@dataclass_transform()
def database_model(
    registry: Registry,
    table_name: str,
    primary_keys: list[str],
):
    def database_model_sub[T: type[BaseModel]](cls: T) -> T:
        assert is_dataclass(cls)

        # Collect Fields
        dc_fields = fields(cls)

        assert issubclass(cls, BaseModel)  # Need to be after fields(cls)

        # Check primary keys
        for pk in primary_keys:
            if pk not in [f.name for f in dc_fields]:
                raise TypeError(f"primary key column '{pk}' not found in {cls.__name__}")

        database_table = qb.Table(table_name, registry.schema_name)

        # Build fields
        dataclass_fields = {}
        for dc_field in dc_fields:
            field_name = dc_field.name
            db_real_name = dc_field.metadata.get("db_name", field_name)
            table_column = database_table.add_column(
                name=db_real_name,
                alias=field_name if field_name != db_real_name else None,
            )
            setattr(
                cls, field_name, table_column
            )  # After dataclass processing, reset class attibutes
            dataclass_fields[field_name] = dc_field

        metadata = ModelMetaData(
            registry, table_name, primary_keys, database_table, dataclass_fields
        )

        cls.__metadata__ = metadata

        # Add to registry
        registry.models.append(cls)

        return cls

    return database_model_sub


class Relation:
    def __init__(
        self,
        model: type[BaseModel],
        rel_model: type[BaseModel],
        join_on: dict[str, qb.Column],
    ):
        self.model = model
        self.rel_model = rel_model
        self.join_on = join_on
        # key is model's column name and value is rel_model's Column object


def setup_relation(
    model: type[BaseModel], relation_name: str, rel_model: type[BaseModel], **join_on
):
    assert len(join_on) > 0
    assert model.__metadata__.registry is rel_model.__metadata__.registry

    main_field_names = model.__metadata__.table.columns_map.keys()
    ref_table = rel_model.__metadata__.table

    for main_field_name, ref_column in join_on.items():
        if main_field_name not in main_field_names:
            raise Exception(
                f"Main field {main_field_name} does not exist in {model.__name__} "
                f"for relation {relation_name}"
            )
        if not ref_table.has_column(ref_column):
            raise Exception(
                f"Field {ref_column} does not exist in {rel_model.__name__} "
                f"for relation {model.__name__}.{relation_name}"
            )

    model.__metadata__.relations[relation_name] = Relation(model, rel_model, join_on)


def db_name(val: str):
    return field(metadata={"db_name": val})
