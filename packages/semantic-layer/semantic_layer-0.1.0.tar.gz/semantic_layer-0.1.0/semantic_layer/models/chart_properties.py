from __future__ import annotations
from datetime import datetime
from typing import List
from pydantic import BaseModel, field_validator
from sqlglot.expressions import Alias, Column, column, condition

from semantic_layer.utils import SQLTypes, SQLExpressions, SQLOperations


class ChartColumn(BaseModel):
    name: str
    data_type: SQLTypes
    table: str
    expression: SQLExpressions | None = None
    where_value: datetime | str | int | None = None
    operation: SQLOperations | None = None

    @field_validator("data_type", mode="before")
    @classmethod
    def validate_data_type(cls, value):
        if isinstance(value, str):
            try:
                return SQLTypes[value.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid data_type: {value}. Valid options are: {[e.name for e in SQLTypes]}"
                )
        return value

    @field_validator("expression", mode="before")
    @classmethod
    def validate_expression(cls, value):
        if isinstance(value, str) and value is not None:
            try:
                return SQLExpressions[value.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid expression: {value}. Valid options are: {[e.name for e in SQLExpressions]}"
                )
        return value

    @field_validator("operation", mode="before")
    @classmethod
    def validate_operation(cls, value):
        if isinstance(value, str) and value is not None:
            try:
                return SQLOperations[value.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid operation: {value}. Valid options are: {[e.name for e in SQLOperations]}"
                )
        return value

    def __eq__(self, value: object) -> bool:
        if isinstance(value, ChartColumn):
            return self.name == value.name
        return False

    def encode_select(self) -> Alias | Column:
        if self.expression is None:
            return column(self.name, self.table)
        else:
            return self.expression.expression(
                column=column(self.name, self.table),
            )

    def encode_where(self):
        if self.where_value is None or self.operation is None:
            raise ValueError(
                "Both 'where_value' and 'operation' must be set to encode a where condition"
            )
        return condition(
            self.operation.expression(
                column=column(self.name, self.table),
                right=self.data_type.expression(self.where_value),
            )
        )


class Dimension(BaseModel):
    table: str
    column_name: str
    label: str
    hierarchy: bool = False
    filters: List[Filter] | None = None


class Metric(BaseModel):
    table: str
    column_name: str
    expression: SQLExpressions

    @field_validator("expression", mode="before")
    @classmethod
    def validate_expression(cls, value):
        if isinstance(value, str):
            try:
                return SQLExpressions[value.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid expression: {value}. Valid options are: {[e.name for e in SQLExpressions]}"
                )
        return value


class ChartProperties(BaseModel):
    dimensions: List[Dimension]
    metrics: List[Metric]
    filters: List[Filter] | None = None


class Filter(BaseModel):
    table_name: str
    column_name: str
    value: int | str | datetime
    operation: SQLOperations

    @field_validator("operation", mode="before")
    @classmethod
    def validate_operation(cls, value):
        if isinstance(value, str):
            try:
                return SQLOperations[value.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid operation: {value}. Valid options are: {[e.name for e in SQLOperations]}"
                )
        return value
