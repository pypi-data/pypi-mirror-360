import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime
from decimal import Decimal
from enum import Enum
from inspect import isclass
from typing import Sequence, Iterable, Literal
from warnings import warn

from .exceptions import QueryBuilderException


type OnConflict = Literal["nothing", "update"]


class DBTypes(Enum):
    POSTGRESQL = "postgresql"
    SQLSERVER = "sqlserver"


class JoinTypes(Enum):
    INNER = "inner"
    OUTER = "outer"
    LEFT = "left"
    RIGHT = "right"


class QueryBuilderWarning(UserWarning):
    pass


class BuildContext:
    def __init__(self, db_type: DBTypes):
        self.db_type = db_type
        self.parameter_list_values = []
        self.parameter_dict_keys = []

    def get_dict_params(self, **kwvalues) -> Sequence:
        if keys_diff := set(kwvalues.keys()).symmetric_difference(set(self.parameter_dict_keys)):
            raise QueryBuilderException(
                f"Please provide exact parameters to keyed parameters: difference is {', '.join(keys_diff)}"
            )
        return [kwvalues[key] for key in self.parameter_dict_keys]


class QueryObjectBase(ABC):
    @abstractmethod
    def render(self, build_context: BuildContext) -> str:
        pass


class Aliasable(ABC):
    def __init__(self, alias: str | None):
        self.alias = alias

    def _handle_alias(self, sql_str: str) -> str:
        if self.alias is not None:
            return f'{sql_str} "{self.alias}"'
        else:
            return sql_str


class TableBase(QueryObjectBase, Aliasable, ABC):
    """Can be used in a FROM clause"""

    def __init__(self, alias: str | None = None):
        super().__init__(alias)
        self._columns: list[Column] = []
        self._columns_map: dict[
            str, Column
        ] = {}  # Keys is identifier, meaning alias if it has one, or real name

    @property
    def columns(self) -> list["Column"]:
        if not self._columns:
            raise QueryBuilderException("Table does not have columns specified")
        return self._columns

    @property
    def columns_map(self) -> dict[str, "Column"]:
        if not self._columns_map:
            raise QueryBuilderException("Table does not have columns specified")
        return self._columns_map

    @property
    @abstractmethod
    def identifier(self) -> str:
        pass

    def add_column(self, name: str, alias: str | None = None) -> "Column":
        c = Column(name, self, alias)
        if c.identifier in self._columns_map:
            raise QueryBuilderException(
                f"Column with identifier {c.identifier} already exists in table {self.identifier}"
            )
        self._columns.append(c)
        self._columns_map[c.identifier] = c
        return c

    def has_column(self, column) -> bool:
        if not self._columns_map:
            raise QueryBuilderException("Table does not have columns specified")
        if isinstance(column, Column):
            column = column.identifier
        return column in self._columns_map


class Table(TableBase):
    def __init__(self, name: str, schema: str | None = None, alias: str | None = None):
        super().__init__(alias)
        self.name = name
        self.schema = schema

    def __repr__(self):
        return f"Table({self.name}', schema={self.schema}, alias={self.alias})"

    @property
    def identifier(self) -> str:
        return self.alias or self.name

    def as_alias(self, alias) -> "Table":
        atable = Table(self.name, self.schema, alias)
        for column in self.columns:
            atable.add_column(column.name, column.alias)
        return atable

    def render(self, build_context: BuildContext) -> str:
        res = f'"{self.name}"'
        if self.schema is not None:
            res = f'"{self.schema}".' + res
        return self._handle_alias(res)


class ModelInterface(ABC):
    class MetadataInterface:
        class RegistryInterface:
            db_type: DBTypes

        primary_keys: list[str]
        table: Table
        registry: RegistryInterface
        relations: dict

    __metadata__: MetadataInterface


type TableParam = type[ModelInterface] | TableBase | str


class Term(QueryObjectBase, ABC):
    def __eq__(self, other) -> "Expression":
        return Expression(self, "=", _try_term_or_value(other))

    def __ne__(self, other) -> "Expression":
        return Expression(self, "!=", _try_term_or_value(other))

    def __and__(self, other) -> "Expression":
        return Expression(self, "AND", _try_term_or_value(other))

    def __or__(self, other) -> "Expression":
        return Expression(self, "OR", _try_term_or_value(other), parenthesised=True)

    def __lt__(self, other) -> "Expression":
        return Expression(self, "<", _try_term_or_value(other))

    def __le__(self, other) -> "Expression":
        return Expression(self, "<=", _try_term_or_value(other))

    def __gt__(self, other) -> "Expression":
        return Expression(self, ">", _try_term_or_value(other))

    def __ge__(self, other) -> "Expression":
        return Expression(self, ">=", _try_term_or_value(other))

    def __invert__(self) -> "Expression":
        return Expression(None, "NOT", self)

    def __add__(self, other) -> "Expression":
        return Expression(self, "+", _try_term_or_value(other))

    def __sub__(self, other) -> "Expression":
        return Expression(self, "-", _try_term_or_value(other))

    def __mul__(self, other) -> "Expression":
        return Expression(self, "*", _try_term_or_value(other))

    def __truediv__(self, other) -> "Expression":
        return Expression(self, "/", _try_term_or_value(other))


def _try_term_or_value(t) -> Term:
    """For use in expressions and functions"""
    return t if isinstance(t, Term) else Value(t)


def _check_term(term):
    """Ensure is term"""
    if not isinstance(term, Term):
        raise QueryBuilderException(f"{term} must be of type Term")
    return term


def _check_terms(terms: Sequence):
    """Ensure all are terms"""
    for term in terms:
        _check_term(term)
    return terms


def _get_table(table: TableParam) -> TableBase:
    if isclass(table) and issubclass(table, ModelInterface):
        return table.__metadata__.table
    if isinstance(table, TableBase):
        return table
    if isinstance(table, str):
        return Table(table)
    raise QueryBuilderException("Cannot handle from_table parameter")


def _init_db_type(from_table: TableParam, db_type: DBTypes | None) -> DBTypes:
    if db_type is None:
        if not inspect.isclass(from_table) or not issubclass(from_table, ModelInterface):
            raise QueryBuilderException("db_type must be specified if from_table is not a Model")
        return from_table.__metadata__.registry.db_type
    return db_type


class Value(Term, Aliasable):
    def __init__(self, value: str | int | float | Decimal | None, alias: str | None = None):
        super().__init__(alias)
        self.value = value

    def render(self, build_context: BuildContext) -> str:
        if isinstance(self.value, str):
            return self._handle_alias(f"'{self.value.replace("'", "''")}'")  # Handle SQL Injection
        if isinstance(self.value, (datetime.datetime, datetime.date)):
            return self._handle_alias(f"'{self.value}'")
        if isinstance(self.value, bool):
            return self._handle_alias(
                f"{
                    ('1' if self.value else '0')
                    if build_context.db_type == DBTypes.SQLSERVER
                    else self.value
                }"
            )
        if isinstance(self.value, (int, float, Decimal)):
            return self._handle_alias(f"{self.value}")
        if self.value is None:
            return self._handle_alias("NULL")
        else:
            raise QueryBuilderException(f"Cannot handle value {self.value}")


class Expression(Term, Aliasable):
    def __init__(
        self,
        left: Term | None,
        operator: str,
        right: Term,
        *,
        alias: str | None = None,
        parenthesised: bool = False,
    ):
        super().__init__(alias)
        self.left = left
        self.operator = operator
        self.right = right
        self.alias = alias
        self.parenthesised = parenthesised or alias is not None

    def __repr__(self):
        return f"Expression({self.left}, {self.operator}, {self.right})"

    def __bool__(self):
        raise QueryBuilderException("Expression cannot be converted to boolean")

    def render(self, build_context: BuildContext) -> str:
        res = (
            "" if self.left is None else f"{self.left.render(build_context)} "
        )  # Order is important here
        res += self.operator + f" {self.right.render(build_context)}"
        if self.parenthesised:
            res = f"({res})"
        return self._handle_alias(res)


class Column(Term, Aliasable):
    def __init__(self, name: str, table: TableBase | str | None = None, alias: str | None = None):
        super().__init__(alias)
        self.name = name
        self.table = table

    def __repr__(self):
        return f"Column({self.name}, alias={self.alias})"

    @property
    def identifier(self):
        return self.name if self.alias is None else self.alias

    def as_alias(self, alias) -> "Column":
        return Column(self.name, self.table, alias)

    def render(self, build_context: BuildContext) -> str:
        if self.name == "*":
            if self.alias is not None:
                raise QueryBuilderException("Cannot alias *")
            res = "*"
        else:
            res = f'"{self.name}"'

        if self.table is not None:
            if isinstance(self.table, TableBase):
                if self.table.alias is not None:
                    res = f'"{self.table.alias}".' + res
                else:
                    if isinstance(self.table, Table):
                        res = f'"{self.table.name}".' + res
                        if self.table.schema is not None:
                            res = f'"{self.table.schema}".' + res
                    else:
                        raise QueryBuilderException(
                            "TableBase object does not have alias or name property"
                        )
            else:  # is str
                res = f'"{self.table}".' + res

        return res  # Manually handle alias

    def render_with_alias(self, build_context: BuildContext):
        return self._handle_alias(self.render(build_context))


class Descending(Term):
    def __init__(self, term):
        self.term = _check_term(term)

    def __repr__(self):
        return f"Descending({repr(self.term)})"

    def render(self, build_context: BuildContext) -> str:
        return f"{self.term.render(build_context)} DESC"


class PositionalParameter(Term):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"PositionalParameter({self.value})"

    def render(self, build_context: BuildContext) -> str:
        if build_context.parameter_dict_keys:
            raise QueryBuilderException("Cannot use PositionalParameter if KeyParameter is used")
        build_context.parameter_list_values.append(self.value)
        return (
            "?"
            if build_context.db_type == DBTypes.SQLSERVER
            else f"${len(build_context.parameter_list_values)}"
        )


class KeyParameter(Term):
    def __init__(self, key: str):
        self.key = key

    def __repr__(self):
        return f"KeyParameter({self.key})"

    def render(self, build_context: BuildContext) -> str:
        if build_context.parameter_list_values:
            raise QueryBuilderException("Cannot use KeyParameter if PositionalParameter is used")

        if build_context.db_type == DBTypes.SQLSERVER:
            build_context.parameter_dict_keys.append(self.key)
            return "?"

        if self.key not in build_context.parameter_dict_keys:  # Re-use same postgres parameter
            build_context.parameter_dict_keys.append(self.key)
        return f"${build_context.parameter_dict_keys.index(self.key) + 1}"


def positional_parameters(values: Iterable):
    return [PositionalParameter(value) for value in values]


@dataclass
class _JoinClause:
    table: TableBase
    on_conditions: Sequence[Term]
    using: list[str] | None
    how: JoinTypes


class QueryBuilderBase(QueryObjectBase, ABC):
    def __init__(self, db_type: DBTypes):
        self.db_type = db_type
        self.use_parameters = True

    def to_sql(self, **key_parameter_values) -> tuple:
        build_context = BuildContext(self.db_type)
        q_str = self.render(build_context)

        if build_context.parameter_dict_keys:
            params = build_context.get_dict_params(**key_parameter_values)
        else:
            if key_parameter_values:
                raise QueryBuilderException(
                    "Keyword arguments only allowed in keyed parameter mode"
                )
            params = build_context.parameter_list_values

        return q_str, *params

    def __str__(self):
        warn(QueryBuilderWarning("Usage of __str__ outside of .to_sql() function"))
        return self.render(BuildContext(self.db_type))


class Select(QueryBuilderBase):
    def __init__(self, from_table: TableParam, db_type: DBTypes | None = None):
        super().__init__(_init_db_type(from_table, db_type))
        self._table = _get_table(from_table)

        self._select: list[Term] = []
        self._joinlist: list[_JoinClause] = []
        self._where: list[Term] = []
        self._group_by: list[Term] = []
        self._having: list[Term] = []
        self._order_by: list[Term] = []
        self._limit: int | None = None
        self._offset: int | None = None
        self._distinct = False

    def select_all(self):
        self._select.append(Column("*"))
        return self

    def select(self, *columns):
        self._select.extend(_check_terms(columns))
        return self

    def select_main_columns(self):
        if not self._table.columns:
            raise QueryBuilderException(
                f"Main Table {self._table.identifier} does not have columns"
            )
        self._select.extend(self._table.columns)
        return self

    def distinct(self):
        self._distinct = True
        return self

    def is_joined(self, table: TableParam):
        return _get_table(table).identifier in [t.table.identifier for t in self._joinlist]

    def join(
        self,
        table: TableParam,
        *on_conditions,
        using: list[str] | None = None,
        how: JoinTypes = JoinTypes.INNER,
    ):
        if self.db_type == DBTypes.SQLSERVER and using is not None:
            raise QueryBuilderException("Cannot use USING with MS SQL Server")
        if on_conditions and using is not None:
            raise QueryBuilderException("Cannot use USING and ON conditions together")
        table = _get_table(table)
        if self.is_joined(table):
            raise QueryBuilderException(f"Table {table.identifier} already in JOIN clause")

        self._joinlist.append(_JoinClause(table, _check_terms(on_conditions), using, how))
        return self

    def left_join(self, table: TableParam, *on_conditions, using: list[str] | None = None):
        return self.join(table, *on_conditions, using=using, how=JoinTypes.LEFT)

    def inner_join(self, table: TableParam, *on_conditions, using: list[str] | None = None):
        return self.join(table, *on_conditions, using=using, how=JoinTypes.INNER)

    def join_relation(
        self,
        model: type[ModelInterface],
        relation_name: str,
        join_type: JoinTypes = JoinTypes.INNER,
    ):
        try:
            relation = model.__metadata__.relations[relation_name]
        except KeyError:
            raise Exception(f"Could not find Relation {relation_name} in model {model.__name__}")

        if not self.is_joined(relation.rel_model):
            self.join(
                relation.rel_model,
                *(
                    getattr(model, col_name) == rel_column
                    for col_name, rel_column in relation.join_on.items()
                ),
                how=join_type,
            )
        return self

    def where(self, *conditions):
        self._where.extend(_check_terms(conditions))
        return self

    def group_by(self, *columns):
        if self._group_by:
            raise QueryBuilderException("GROUP BY already set")
        self._group_by = _check_terms(columns)
        return self

    def having(self, *conditions):
        if self._having:
            raise QueryBuilderException(
                "HAVING already set"
            )  # Expected to be set once with the group by
        self._having = _check_terms(conditions)
        return self

    def order_by(self, *columns):
        if self._order_by:
            raise QueryBuilderException("ORDER BY already set")
        self._order_by = _check_terms(columns)
        return self

    @property
    def is_ordered(self):
        return self._order_by

    def invert_order_by(self):
        if not self.is_ordered:
            raise QueryBuilderException("ORDER BY not set")
        self._order_by = [
            col.term if isinstance(col, Descending) else Descending(col) for col in self._order_by
        ]
        return self

    def limit(self, limit: int | Term):
        if self._limit is not None:
            raise QueryBuilderException("LIMIT already set")
        self._limit = limit
        return self

    def offset(self, offset: int | Term):
        if self._offset is not None:
            raise QueryBuilderException("OFFSET already set")
        self._offset = offset
        return self

    def render(
        self, build_context: BuildContext
    ) -> (
        str
    ):  # Make sure to build the SQL in top-down order so SQL Server paramters get injected in order
        # Validating
        if not self._select:
            raise QueryBuilderException("SELECT is not defined")
        if self._having and not self._group_by:
            raise QueryBuilderException("Cannot use HAVING without GROUP BY")

        # Building
        select_str = ", ".join(
            s.render_with_alias(build_context) if isinstance(s, Column) else s.render(build_context)
            for s in self._select
        )
        res = "SELECT"
        if self._distinct:
            res += " DISTINCT"
        res += f" {select_str}\nFROM {self._table.render(build_context)}"
        if self._joinlist:
            for jc in self._joinlist:
                res += f"\n{jc.how.value.upper()} JOIN {jc.table.render(build_context)} "
                if jc.using:
                    res += f"USING({', '.join(f'"{uc}"' for uc in jc.using)})"
                else:
                    res += f"ON {And(*jc.on_conditions).render(build_context)}"
        if self._where:
            where_str = "\nAND ".join(w.render(build_context) for w in self._where)
            res += f"\nWHERE {where_str}"
        if self._group_by:
            groupby_str = ", ".join(s.render(build_context) for s in self._group_by)
            res += f"\nGROUP BY {groupby_str}"
            if self._having:
                res += f"\nHAVING {And(*self._having).render(build_context)}"
        if self._order_by:
            res += f"\nORDER BY {', '.join(col.render(build_context) for col in self._order_by)}"
        # Limits and offsets
        if self.db_type == DBTypes.SQLSERVER:
            if self._offset or self._limit:
                res += f"\nOFFSET {self._offset or 0} ROWS"
            if self._limit:
                res += f"\nFETCH NEXT {self._limit} ROWS ONLY"
        else:  # Postgresql
            if self._limit is not None:
                res += f"\nLIMIT {self._limit}"
            if self._offset is not None:
                res += f"\nOFFSET {self._offset}"

        return res


def _try_pure_value(v):
    """For values in INSERT statements"""
    if isinstance(v, (Value, PositionalParameter, KeyParameter)):
        try:
            if v.alias is not None:
                raise QueryBuilderException("Pure Value cannot have alias")
        except AttributeError:
            pass
    else:
        if isinstance(v, Term):
            raise QueryBuilderException("Term can only be of instance Value or Parameter")
        v = Value(v)
    return v


class Insert(QueryBuilderBase):
    def __init__(self, into_table: TableParam, db_type: DBTypes | None = None):
        super().__init__(_init_db_type(into_table, db_type))
        self._table = _get_table(into_table)
        self._primary_keys: list[str] | None = None

        self._column_names: list[str] = []
        self._values_list: list[Sequence[Value]] = []
        self._on_conflict: OnConflict | None = None

        if isclass(into_table) and issubclass(into_table, ModelInterface):
            self._primary_keys = into_table.__metadata__.primary_keys

    def set_columns_from_table(self):
        self._column_names = [c.name for c in self._table.columns]
        if not self._column_names:
            raise QueryBuilderException(f"Table {self._table.identifier} does not have columns")
        return self

    def columns(self, *column_names: str):
        self._column_names = column_names
        return self

    def values(self, *pos_values, **kw_values):
        if not self._column_names:
            raise QueryBuilderException("Please set column names first")

        if pos_values and kw_values:
            raise QueryBuilderException("Cannot use positional and keyword values together")

        if pos_values:
            if len(self._column_names) != len(pos_values):
                raise QueryBuilderException("Please provide the exact number of values")
            values = pos_values
        else:
            if set(self._column_names) != set(kw_values.keys()):
                raise QueryBuilderException("Column names do not match")
            values = [kw_values[cn] for cn in self._column_names]

        self._values_list.append([_try_pure_value(v) for v in values])
        return self

    def on_conflict(self, action: OnConflict):
        if self.db_type == DBTypes.SQLSERVER:
            raise QueryBuilderException("ON CONFLICT is not supported for SQL Server")
        self._on_conflict = action
        return self

    def render(self, build_context: BuildContext) -> str:
        if not self._column_names:
            raise QueryBuilderException("Cannot render query without column names")
        res = f"INSERT INTO {self._table.render(build_context)} ({', '.join(f'"{cn}"' for cn in self._column_names)}) VALUES\n"
        res += ",\n".join(
            f"({', '.join(v.render(build_context) for v in values)})"
            for values in self._values_list
        )
        if self._on_conflict is not None:
            res += f"\nON CONFLICT ({
                ', '.join(
                    f'"{self._table.columns_map[pk_name].name}"' for pk_name in self._primary_keys
                )
            }) DO "
            if self._on_conflict == "update":
                res += "UPDATE SET\n"
                res += ",\n".join(
                    f'"{cn}" = EXCLUDED."{cn}"'
                    for cn in self._column_names
                    if cn not in self._primary_keys
                )
            elif self._on_conflict == "nothing":
                res += "NOTHING"
            else:
                raise QueryBuilderException(f"Cannot handle ON CONFLICT action {self._on_conflict}")
        return res


class Update(QueryBuilderBase):
    def __init__(self, update_table: TableParam, db_type: DBTypes | None = None):
        super().__init__(_init_db_type(update_table, db_type))
        self._table = _get_table(update_table)

        self._where: list[Term] = []
        self._values: dict[str, Term] = {}

    def where(self, *conditions):
        self._where.extend(_check_terms(conditions))
        return self

    def set_value(self, column: Column | str, value):
        if self._table.columns:
            if not self._table.has_column(column):
                raise QueryBuilderException(
                    f'Column "{column}" does not exist on table {self._table.identifier}'
                )
            # Handle aliasing
            if not isinstance(column, Column):  # is a str
                column = self._table.columns_map[column]
            column_name = column.name
        else:  # use as is in case no columns specified on table
            if isinstance(column, Column):
                raise QueryBuilderException(
                    "Update's table does not have columns, so cannot use Column object"
                )
            column_name = column

        if column_name in self._values:
            raise QueryBuilderException(f"Column {column_name} already set")
        self._values[column_name] = _try_term_or_value(value)
        return self

    def set(self, **kw_values):
        for k, v in kw_values.items():
            self.set_value(k, v)
        return self

    def render(self, build_context: BuildContext) -> str:
        if not self._where:
            raise QueryBuilderException("Cannot use UPDATE without WHERE clause")

        res = f"UPDATE {self._table.render(build_context)} SET\n"
        res += ",\n".join(
            f'"{cn}" = {value.render(build_context)}' for cn, value in self._values.items()
        )
        res += "\nWHERE" + "\nAND ".join(f"({w.render(build_context)})" for w in self._where)
        return res


class Delete(QueryBuilderBase):
    def __init__(self, from_table: TableParam, db_type: DBTypes | None = None):
        super().__init__(_init_db_type(from_table, db_type))
        self._table = _get_table(from_table)

        self._where: list[Term] = []

    def where(self, *conditions):
        self._where.extend(_check_terms(conditions))
        return self

    def render(self, build_context: BuildContext) -> str:
        if not self._where:
            raise QueryBuilderException("Cannot use DELETE without WHERE clause")

        res = f"DELETE FROM {self._table.render(build_context)} WHERE\n"
        res += "\nAND ".join(f"({w.render(build_context)})" for w in self._where)
        return res


class And(Term):
    def __init__(self, *terms):
        self.terms = _check_terms(terms)

    def render(self, build_context: BuildContext) -> str:
        return " AND ".join(t.render(build_context) for t in self.terms)


class Or(Term):
    def __init__(self, *terms):
        self.terms = _check_terms(terms)

    def render(self, build_context: BuildContext) -> str:
        return f"({' OR '.join(t.render(build_context) for t in self.terms)})"


class Like(Term, Aliasable):
    def __init__(self, left, right, alias: str | None = None, case_sensitive=False):
        super().__init__(alias)
        self.left = _check_term(left)
        self.right = _try_term_or_value(right)
        self.case_sensitive = case_sensitive

    def render(self, build_context: BuildContext) -> str:
        if build_context.db_type == DBTypes.SQLSERVER and not self.case_sensitive:
            return self._handle_alias(
                f"LOWER({self.left.render(build_context)}) LIKE LOWER({self.right.render(build_context)})"
            )
        else:
            operator = "LIKE" if self.case_sensitive else "ILIKE"
            return self._handle_alias(
                f"{self.left.render(build_context)} {operator} {self.right.render(build_context)}"
            )


class IsNull(Term):
    def __init__(self, term):
        self.term = _check_term(term)

    def render(self, build_context: BuildContext) -> str:
        return f"{self.term.render(build_context)} IS NULL"


class NotNull(Term):
    def __init__(self, term):
        self.term = _check_term(term)

    def render(self, build_context: BuildContext) -> str:
        return f"{self.term.render(build_context)} IS NOT NULL"


class NullIf(Term, Aliasable):
    def __init__(self, term1, term2, alias: str | None = None):
        super().__init__(alias)
        self.term1 = _check_term(term1)
        self.term2 = _try_term_or_value(term2)

    def render(self, build_context: BuildContext) -> str:
        return self._handle_alias(
            f"NULLIF({self.term1.render(build_context)}, {self.term2.render(build_context)})"
        )


class Function(Term, Aliasable):
    def __init__(self, function_name: str, *parameters, alias: str | None = None):
        super().__init__(alias)
        self.function_name = function_name
        self.parameters = [_try_term_or_value(p) for p in parameters]

    def render(self, build_context: BuildContext) -> str:
        res = f"{self.function_name}({', '.join(p.render(build_context) for p in self.parameters)})"
        return self._handle_alias(res)


class Coalesce(Term, Aliasable):
    def __init__(self, *terms, alias: str | None = None):
        super().__init__(alias)
        self.terms = _check_terms(terms)

    def render(self, build_context: BuildContext) -> str:
        return self._handle_alias(
            f"COALESCE({', '.join(t.render(build_context) for t in self.terms)})"
        )


class Cast(Term, Aliasable):
    def __init__(self, term, newtype: str, alias: str | None = None):
        super().__init__(alias)
        self.term = _check_term(term)
        self.newtype = newtype

    def render(self, build_context: BuildContext) -> str:
        return self._handle_alias(f"CAST({self.term.render(build_context)} AS {self.newtype})")


class Sum(Term, Aliasable):
    def __init__(self, term, alias: str | None = None):
        super().__init__(alias)
        self.term = _check_term(term)

    def render(self, build_context: BuildContext) -> str:
        return self._handle_alias(f"SUM({self.term.render(build_context)})")


class Count(Term, Aliasable):
    def __init__(self, term, alias: str | None = None):
        super().__init__(alias)
        self.term = _check_term(term)

    def render(self, build_context: BuildContext) -> str:
        return self._handle_alias(f"COUNT({self.term.render(build_context)})")


class Avg(Term, Aliasable):
    def __init__(self, term, alias: str | None = None):
        super().__init__(alias)
        self.term = _check_term(term)

    def render(self, build_context: BuildContext) -> str:
        return self._handle_alias(f"AVG({self.term.render(build_context)})")


class Max(Term, Aliasable):
    def __init__(self, term, alias: str | None = None):
        super().__init__(alias)
        self.term = _check_term(term)

    def render(self, build_context: BuildContext) -> str:
        return self._handle_alias(f"MAX({self.term.render(build_context)})")


class Min(Term, Aliasable):
    def __init__(self, term, alias: str | None = None):
        super().__init__(alias)
        self.term = _check_term(term)

    def render(self, build_context: BuildContext) -> str:
        return self._handle_alias(f"MIN({self.term.render(build_context)})")


class Tuple(Term):
    def __init__(self, *terms):
        if not terms:
            raise QueryBuilderException("Tuple cannot be empty")
        self.terms = _check_terms(terms)

    def render(self, build_context: BuildContext) -> str:
        if len(self.terms) == 1:
            return str(self.terms[0])
        return f"({', '.join(term.render(build_context) for term in self.terms)})"


class Array(Term):
    def __init__(self, *terms):
        self.terms = [_try_term_or_value(term) for term in terms]

    def render(self, build_context: BuildContext) -> str:
        return f"ARRAY[{', '.join(term.render(build_context) for term in self.terms)}]"


class Any(Term):
    def __init__(self, array: Array | Select):
        if not isinstance(array, (Array, Select)):
            raise QueryBuilderException("Any can only take and Array or Select object")
        self.array = array

    def render(self, build_context: BuildContext) -> str:
        if build_context.db_type == DBTypes.SQLSERVER:
            raise QueryBuilderException("Cannot use ANY in SQLSERVER")
        return f"ANY({self.array.render(build_context)})"


class In(Term):
    def __init__(self, left, terms: Iterable):
        if not terms:
            raise QueryBuilderException("In cannot be empty")
        self.left = _check_term(left)
        self.terms = [_try_term_or_value(t) for t in terms]

    def render(self, build_context: BuildContext) -> str:
        return f"{self.left.render(build_context)} IN ({', '.join(term.render(build_context) for term in self.terms)})"


class Between(Term, Aliasable):
    def __init__(self, term, start, end, alias: str | None = None):
        super().__init__(alias)
        self.term = _check_term(term)
        self.start = _try_term_or_value(start)
        self.end = _try_term_or_value(end)

    def render(self, build_context: BuildContext) -> str:
        return self._handle_alias(
            f"{self.term.render(build_context)}"
            f" BETWEEN {self.start.render(build_context)} AND {self.end.render(build_context)}"
        )


class TableSubQuery(TableBase):
    def __init__(self, sub: Select, alias: str):
        super().__init__(alias)
        self.sub = sub

    @property
    def identifier(self) -> str:
        if self.alias is None:
            raise QueryBuilderException("SubQuery does not have identifier. Please supply an alias")
        return self.alias

    def render(self, build_context: BuildContext) -> str:
        return self._handle_alias(f"(\n{self.sub.render(build_context)}\n)")


class ValueSubQuery(Term, Aliasable):
    def __init__(self, sub: Select, alias: str | None = None):
        super().__init__(alias)
        self.sub = sub

    def render(self, build_context: BuildContext) -> str:
        return self._handle_alias(f"(\n{self.sub.render(build_context)}\n)")


class Unnest(TableBase):
    def __init__(
        self,
        *array_column_list: Term,
        alias: str | None = None,
        column_names: list[str] | None = None,
    ):
        super().__init__(alias)
        self.arrays_list = array_column_list
        if column_names is not None:
            if self.alias is None:
                raise QueryBuilderException("Cannot add columns if not alias is specified")
            if len(array_column_list) != len(column_names):
                raise QueryBuilderException(
                    "Please provide the same number of column names as there are arrays"
                )
            for cn in column_names:
                self.add_column(cn)

    @property
    def identifier(self) -> str:
        if self.alias is None:
            raise QueryBuilderException(
                "UNNEST function does not have identifier. Please supply an alias"
            )
        return self.alias

    def render(self, build_context: BuildContext) -> str:
        res = f"UNNEST({', '.join(array_col.render(build_context) for array_col in self.arrays_list)})"
        if self.alias is not None:
            res += f" AS {self.alias}"
            if self.columns:
                res += f"({', '.join(str(c.name) for c in self.columns)})"
        return res


class Exists(Term):
    def __init__(self, subselect: Select):
        self.subselect = subselect

    def render(self, build_context: BuildContext) -> str:
        return f"EXISTS(\n{self.subselect.render(build_context)}\n)"


class Case(Term, Aliasable):
    def __init__(self, term=None, alias: str | None = None):
        super().__init__(alias)
        self._case_term = _check_term(term) if term is not None else None
        self._when_terms: list[tuple[Term, Term]] = []
        self._else_term = None

        self._next_when: Term | None = None

    def when(self, term):
        if self._next_when is not None:
            raise QueryBuilderException("WHEN already set in CASE statement")
        self._next_when = _check_term(term)
        return self

    def then(self, term):
        if self._next_when is None:
            raise QueryBuilderException("WHEN not set in CASE statement")
        self._when_terms.append((self._next_when, _try_term_or_value(term)))
        self._next_when = None
        return self

    def else_(self, term):
        self._else_term = _try_term_or_value(term)
        return self

    def render(self, build_context: BuildContext) -> str:
        res = "CASE"
        if self._case_term:
            res += f" {self._case_term.render(build_context)}"
        for when_term, then_term in self._when_terms:
            res += f" WHEN {when_term.render(build_context)} THEN {then_term.render(build_context)}"
        if self._else_term:
            res += f" ELSE {self._else_term.render(build_context)}"
        res += " END"
        return self._handle_alias(res)
