from dataclasses import dataclass

from st_microservice.models_utils import BaseModel, database_model, Registry
from st_microservice.querybuilder import (
    Select,
    Column,
    Value,
    Function,
    Descending,
    PositionalParameter,
    KeyParameter,
    Delete,
    Insert,
    Update,
    DBTypes,
    JoinTypes,
    QueryBuilderBase,
    In,
    Any,
    Array,
    Case,
)

registry = Registry(schema_name="service")


def show(q: QueryBuilderBase, **kwargs):
    q_str, *params = q.to_sql(**kwargs)
    print(q_str)
    print(params)
    print()


@database_model(registry, "header", ["document_type", "document_no"])
@dataclass
class Header(BaseModel):
    document_type: str
    document_no: str
    customer: str
    vin: str


@database_model(registry, "line", ["document_type", "document_no", "line_no"])
@dataclass
class Line(BaseModel):
    document_type: str
    document_no: str
    line_no: int
    item: str
    quantity: int
    amount: float


q1 = Select("ledger", DBTypes.POSTGRESQL).select_all()
show(q1)

q2 = Select("users", DBTypes.POSTGRESQL).select(
    Column("name"), Column("id"), Value("one two", "col5"), Value(5)
)
show(q2)

q3 = (
    Select("ledger", DBTypes.POSTGRESQL)
    .select(Column("name"), Column("id"), Function("SUM", Column("count")))
    .group_by(Column("name"), Column("id"))
    .having(Function("SUM", Column("count")) > 0)
)
show(q3)

q4 = (
    Select(Line)
    .select_all()
    .where(((Line.quantity == 2) | (Line.quantity == 3)) & ~(Line.amount < 0))
    .where(Line.document_no == "doc")
    .limit(10)
    .order_by(Line.document_type, Descending(Line.document_no))
    .offset(40)
)
show(q4)

q5 = (
    Select(Line)
    .select(Line.amount)
    .join(
        Header,
        Header.document_type == Line.document_type,
        Header.document_no == Line.document_no,
        how=JoinTypes.LEFT,
    )
)
show(q5)

q5a = (
    Select(Line)
    .select(Line.amount)
    .join(Header, using=["document_type", "document_no"], how=JoinTypes.LEFT)
)
show(q5a)

q6 = (
    Select(Line)
    .select_main_columns()
    .where(Line.line_no > PositionalParameter(0))
    .where(Line.document_no == PositionalParameter("doc1"))
)

show(q6)

q7 = (
    Select(Line)
    .select_main_columns()
    .select(Line.line_no < KeyParameter("one") + Value(5))
    .where(Line.line_no > KeyParameter("one"))
    .where(Line.document_no == KeyParameter("two"))
)

show(q7, one=1, two="doc2")

q8 = Delete(Line).where(Line.line_no == 0)
show(q8)

q9 = (
    Insert(Line)
    .set_columns_from_table()
    .values(0, 1, 2, "three", 4, 5)
    .values(
        document_type="ord",
        document_no="123",
        line_no=3,
        item="33sw",
        quantity=7,
        amount=2.56,
    )
    .on_conflict("update")
)
show(q9)

q10 = Update(Line).where(Line.document_no == "doc1").set(amount=0, quantity=1).set(item="no")
show(q10)

q11 = (
    Select(Line)
    .distinct()
    .select_all()
    .select(Case(alias="test_case").when(Line.amount > 0).then(5).else_(3))
    .where(In(Line.line_no, [1, 2, 3]), Line.document_no == Any(Array("a'a", "b", "c")))
)
show(q11)
