from enum import Enum
from sqlglot.expressions import (
    String,
    Int64,
    ToDouble,
    Boolean,
    Date,
    Timestamp,
    Literal,
    Column,
    Condition,
    Sum,
    Avg,
    Count,
    Min,
    Max,
    EQ,
    NEQ,
    GT,
    GTE,
    LT,
    LTE,
)


class SQLTypes(Enum):
    STRING = String
    INTEGER = Int64
    FLOAT = ToDouble
    BOOLEAN = Boolean
    DATE = Date
    TIMESTAMP = Timestamp

    def expression(self, value):
        if self.name in ["INTEGER", "FLOAT"]:
            return self.value(this=Literal.number(value))
        return self.value(this=Literal.string(value))


class SQLOperations(Enum):
    EQ = EQ
    NEQ = NEQ
    GT = GT
    GTE = GTE
    LT = LT
    LTE = LTE

    def expression(self, column: Column, right: Condition):
        return self.value(this=column, expression=right)


class SQLExpressions(Enum):
    SUM = Sum
    AVG = Avg
    COUNT = Count
    MIN = Min
    MAX = Max

    def expression(self, column: Column):
        return self.value(this=column).as_(column.name)
