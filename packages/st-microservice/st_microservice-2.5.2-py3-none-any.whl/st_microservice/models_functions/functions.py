from dataclasses import asdict
import datetime as dt
from decimal import Decimal
from math import floor
from types import UnionType
from typing import get_type_hints, get_origin, get_args, Sequence, Iterable, Mapping, Any

from graphql import GraphQLResolveInfo
from aiodataloader import DataLoader

from ..database import DBInterface
from ..exceptions import NoRowsError, MultipleRowsError, QueryBuilderException
from ..models_utils import BaseModel
from ..querybuilder import (
    Table,
    Column,
    Term,
    And,
    In,
    Tuple,
    DBTypes,
    OnConflict,
    Select,
    Insert,
    Update,
    Delete,
    KeyParameter,
    PositionalParameter,
    BuildContext,
)
from ..request_utils import get_state, get_db


def table(model: type[BaseModel] | BaseModel) -> Table:
    return model.__metadata__.table


def all_columns(model: type[BaseModel]) -> list[Column]:
    return table(model).columns


def build_from_tuple[T: BaseModel](model: type[T], rec: Sequence | None) -> T | None:
    if rec is None:
        return None
    return model(*rec)


def build_from_mapping[T: BaseModel](model: type[T], rec: Mapping | None) -> T | None:
    if rec is None:
        return None
    return model(**rec)


def build[T: BaseModel](model: type[T], rec) -> T | None:
    try:
        return build_from_mapping(model, rec)
    except TypeError:
        return build_from_tuple(model, rec)


def build_all[T: BaseModel](model: type[T], recs: Sequence) -> list[T]:
    try:
        return [build_from_mapping(model, rec) for rec in recs]
    except TypeError:
        return [build_from_tuple(model, rec) for rec in recs]


def primary_key_filter(model: type[BaseModel], **primary_keys) -> Term:
    """Return Criterion to be used in a .where()"""
    metadata = model.__metadata__
    if diff := set(primary_keys.keys()).symmetric_difference(set(metadata.primary_keys)):
        raise QueryBuilderException(f"Please specify all primary keys. Difference is : {diff}")
    return And(*(metadata.table.columns_map[pk] == value for pk, value in primary_keys.items()))


def get_query(model: type[BaseModel], **primary_keys) -> Select:
    """Primary keys can be Params"""
    q = Select(model).select_main_columns().where(primary_key_filter(model, **primary_keys))
    return q


async def get[T: BaseModel](db: DBInterface, model: type[T], **primary_keys) -> T | None:
    db_type = model.__metadata__.registry.db_type
    q = get_query(model, **{key: KeyParameter(key) for key in primary_keys.keys()})
    rows = await db.fetch(*q.to_sql(**primary_keys))
    row_count = len(rows)
    if row_count == 0:
        return None
    if row_count > 1:
        raise MultipleRowsError

    if db_type == DBTypes.SQLSERVER:
        return build_from_tuple(model, rows[0])
    else:
        return build_from_mapping(model, rows[0])


async def get_or_error[T: BaseModel](db: DBInterface, model: type[T], **primary_keys) -> T:
    row = await get(db, model, **primary_keys)
    if row is None:
        raise NoRowsError
    return row


def delete_query(model: type[BaseModel], **primary_keys) -> Delete:
    q = Delete(model).where(primary_key_filter(model, **primary_keys))
    return q


async def delete(db: DBInterface, model: type[BaseModel], **primary_keys) -> None:
    q = delete_query(model, **{key: KeyParameter(key) for key in primary_keys.keys()})
    await db.execute(*q.to_sql(**primary_keys))


async def insert[T: BaseModel](
    db: DBInterface, model: type[T], obj: T, on_conflict: OnConflict | None = None
):
    obj_dict = asdict(obj)
    q = (
        Insert(model)
        .set_columns_from_table()
        .values(**{key: KeyParameter(key) for key in obj_dict})
        .on_conflict(on_conflict)
    )
    await db.execute(*q.to_sql(**obj_dict))


async def insert_many[T: BaseModel](
    db: DBInterface,
    model: type[T],
    objs: Iterable[T],
    on_conflict: OnConflict | None = None,
):
    obj_dicts = [asdict(obj) for obj in objs]
    if not obj_dicts:  # Ensure at least one
        return
    q = (
        Insert(model)
        .set_columns_from_table()
        .values(**{key: KeyParameter(key) for key in obj_dicts[0]})
        .on_conflict(on_conflict)
    )
    build_context = BuildContext(q.db_type)
    q_str = q.render(build_context)
    await db.executemany(
        q_str, (build_context.get_dict_params(**obj_dict) for obj_dict in obj_dicts)
    )


def update_query(model: type[BaseModel], **primary_keys) -> Update:
    """specifiying primary keys allows for renaming a record. They're prefixed by pk_"""
    metadata = model.__metadata__
    table_columns = metadata.table.columns_map
    q = Update(model)

    if primary_keys:
        if pk_diff := set(primary_keys.keys()) != set(metadata.primary_keys):
            raise QueryBuilderException(
                f"Please specify the correct primary keys for model {model.__name__}."
                f" Difference is {pk_diff}"
            )
        for field_name, value in primary_keys.items():
            q.where(table_columns[field_name] == KeyParameter("pk_" + field_name))

    for field_name, column in table_columns.items():
        if not primary_keys and field_name in metadata.primary_keys:
            q.where(column == KeyParameter(field_name))
        else:
            q.set(**{column.name: KeyParameter(field_name)})
    return q


async def update[T: BaseModel](db: DBInterface, model: type[T], obj: T, **primary_keys):
    """specifiying primary keys allows for renaming a record. They're prefixed by pk_"""
    q = update_query(model, **primary_keys)
    await db.execute(*q.to_sql(**asdict(obj), **{"pk_" + k: v for k, v in primary_keys.items()}))


async def update_many[T: BaseModel](db: DBInterface, model: type[T], objs: Iterable[T]):
    obj_dicts = [asdict(obj) for obj in objs]
    if not obj_dicts:  # Ensure at least one
        return
    q = update_query(model)
    build_context = BuildContext(q.db_type)
    q_str = q.render(build_context)
    await db.executemany(q_str, (build_context.get_dict_params(**obj) for obj in obj_dicts))


def get_relation_model(model: type[BaseModel], relation_name: str) -> type[BaseModel]:
    try:
        relation = model.__metadata__.relations[relation_name]
    except KeyError:
        raise Exception(f"Could not find Relation {relation_name} in model {model.__name__}")
    return relation.rel_model


async def batch_load[T: BaseModel](
    db: DBInterface, model: type[T], columns: Sequence[str], keys_list: Sequence[tuple]
) -> list[T]:
    """Load many records by using tuple equality"""
    if not columns:
        raise QueryBuilderException("Please specify at least 1 column")
    if not keys_list:
        return []

    temp_table: Table | None = None

    q = Select(model).select_main_columns()
    if len(columns) == 1:
        q.where(
            In(
                getattr(model, columns[0]),
                [PositionalParameter(keys[0]) for keys in keys_list],
            )
        )
    else:
        if q.db_type == DBTypes.SQLSERVER:
            type_to_col = {
                str: "VARCHAR(MAX) COLLATE DATABASE_DEFAULT",
                int: "INTEGER",
                dt.datetime: "DATETIME",
                dt.date: "DATETIME",
            }
            column_and_types = {
                col: type_to_col[model.__metadata__.dataclass_fields[col].type] for col in columns
            }
            # Build table
            temp_table = Table("#" + model.__metadata__.table_name)
            qc = f"CREATE TABLE {temp_table.render(BuildContext(DBTypes.SQLSERVER))} ({
                ', '.join(f'"{c}" {t}' for c, t in column_and_types.items())
            })"
            await db.execute(qc)
            # Query Insert into temp
            qi = (
                Insert(temp_table, DBTypes.SQLSERVER)
                .columns(*columns)
                .values(*(KeyParameter(col) for col in columns))
            )
            qi_str = qi.render(BuildContext(q.db_type))
            # Assuming keys_list should be ordered correctly
            await db.executemany(qi_str, keys_list)
            # Query join on temp
            q.inner_join(
                temp_table,
                *(Column(col, temp_table) == getattr(model, col) for col in columns),
            )
        else:
            q.where(
                In(
                    Tuple(*(getattr(model, column) for column in columns)),
                    [Tuple(*(PositionalParameter(key) for key in keys)) for keys in keys_list],
                )
            )

    objs = build_all(model, await db.fetch(*q.to_sql()))
    if temp_table is not None:
        await db.execute(f"DROP TABLE {temp_table.render(BuildContext(q.db_type))}")
    return objs


def get_autoloaders(info: GraphQLResolveInfo) -> dict[str:DataLoader]:
    state = get_state(info)
    if not hasattr(state, "auto_loaders"):
        state.auto_loaders = {}
    return state.auto_loaders


async def dataloader_get[T: BaseModel](
    info: GraphQLResolveInfo, model: type[T], **primary_keys
) -> T | None:
    """Get one record by primary key"""
    # Check keys
    pk_names = model.__metadata__.primary_keys
    if diff := set(primary_keys.keys()).symmetric_difference(set(pk_names)):
        raise QueryBuilderException(
            f"Please specify the correct primary keys for model {model.__name__}."
            f" Difference is {diff}"
        )

    auto_loaders = get_autoloaders(info)
    try:
        dl = auto_loaders[model.__name__]
    except KeyError:
        registry = model.__metadata__.registry
        db = (registry.db_connection_factory or get_db)(info)

        async def batch_get_wrapper(keys_list: Sequence[tuple]):
            objs = await batch_load(db, model, pk_names, keys_list)
            # Build dict
            d = {tuple(getattr(obj, pk) for pk in pk_names): obj for obj in objs}
            return [d.get(keys) for keys in keys_list]

        # SQL Server limit is 2100
        max_batch_size = (
            floor(2000 / len(pk_names)) if registry.db_type == DBTypes.SQLSERVER else 10_000
        )
        dl = auto_loaders[model.__name__] = DataLoader(
            batch_get_wrapper, max_batch_size=max_batch_size
        )

    return await dl.load(tuple(primary_keys[pk] for pk in pk_names))


async def dataloader_load[T: BaseModel](
    info: GraphQLResolveInfo, model: type[T], **key_values
) -> list[T]:
    """Get many records filtering by columns"""
    # Handle keys
    columns = sorted(key_values.keys())
    if diff := (set(columns) - set(model.__metadata__.table.columns_map.keys())):
        raise QueryBuilderException(
            f"Columns [{', '.join(diff)}] do not exist in model {model.__name__}"
        )

    auto_loaders = get_autoloaders(info)
    loader_name = f"{model.__name__}__{'_'.join(columns)}"
    try:
        dl = auto_loaders[loader_name]
    except KeyError:
        registry = model.__metadata__.registry
        db = (registry.db_connection_factory or get_db)(info)

        async def batch_get_wrapper(keys_list: Sequence[tuple]):
            objs = await batch_load(db, model, columns, keys_list)
            # Build dict
            d: dict[tuple, list[BaseModel]] = {}
            for obj in objs:
                d.setdefault(tuple(getattr(obj, col) for col in columns), []).append(obj)
            return [d.get(keys, []) for keys in keys_list]

        # SQL Server limit is 2100
        max_batch_size = (
            floor(2000 / len(columns)) if registry.db_type == DBTypes.SQLSERVER else 10_000
        )
        dl = auto_loaders[loader_name] = DataLoader(
            batch_get_wrapper, max_batch_size=max_batch_size
        )

    return await dl.load(tuple(key_values[col] for col in columns))


def _handle_field_value[T](field_type: type[T], field_value) -> T:
    """Casts field_value according to field_type"""
    if get_origin(field_type) is UnionType:  # If it's a union, get first sub-type
        field_type = get_args(field_type)[0]

    if field_type is Decimal:
        if isinstance(field_value, float):  # Convert float to Decimal
            field_value = Decimal(field_value)
    elif field_type is dt.date:
        if isinstance(field_value, str):
            field_value = dt.date.fromisoformat(field_value)
    elif field_type is dt.datetime:
        if isinstance(field_value, str):
            field_value = dt.datetime.fromisoformat(field_value)

    return field_value


def set_dataclass_attribute(obj: BaseModel, field_name: str, field_value):
    """Like setattr but try to handle types"""
    field_type = get_type_hints(obj.__class__)[field_name]
    setattr(obj, field_name, _handle_field_value(field_type, field_value))


def handle_json_fields(model: type[BaseModel], json_dict: dict[str, Any]) -> dict[str, Any]:
    type_hints = get_type_hints(model)
    return {
        field_name: _handle_field_value(type_hints[field_name], field_value)
        for field_name, field_value in json_dict.items()
    }


# Python type handlers
def extract_main_from_union_type(type_) -> type:
    """Return main type when nullable"""
    if get_origin(type_) is UnionType:
        unioned_types = []
        for unioned_type in get_args(type_):
            if unioned_type is not type(None):
                unioned_types.append(unioned_type)
        assert len(unioned_types) == 1
        return unioned_types[0]
    return type_


def extract_main_from_list_type(type_) -> type:
    """Return main type when list"""
    if get_origin(type_) is list:
        return get_args(type_)[0]
    return type_


def extract_main_type(type_) -> type:
    type_ = extract_main_from_union_type(type_)  # Handle first level of nullable
    type_ = extract_main_from_list_type(type_)  # Dig into one level of list
    return extract_main_from_union_type(type_)  # Handle second level of nullable


def is_field_list_type(model: type[BaseModel], field_name: str) -> type:
    type_ = model.__metadata__.dataclass_fields[field_name].type
    # Handle first level of nullable
    type_ = extract_main_from_union_type(type_)
    return get_origin(type_) is list


def get_field_main_type(model: type[BaseModel], field_name: str) -> type:
    type_ = model.__metadata__.dataclass_fields[field_name].type
    return extract_main_type(type_)
