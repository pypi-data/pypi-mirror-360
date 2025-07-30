from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, field_validator

from semantic_layer.utils import SQLTypes


class Column(BaseModel):
    name: str
    description: str
    data_type: SQLTypes
    primary_key: bool | None = None

    @field_validator("data_type", mode="before")
    @classmethod
    def validate_data_type(cls, value):
        if isinstance(value, str):
            # Convert string to uppercase and match the enum
            try:
                return SQLTypes[value.upper()]
            except KeyError:
                raise ValueError(
                    f"Invalid data_type: {value}. Valid options are: {[e.name for e in SQLTypes]}"
                )
        return value


class FactTable(BaseModel):
    name: str
    description: str
    columns: List[Column]
    dimensions: List[Dimension]


class Dimension(BaseModel):
    name: str
    table_name: str
    fact_dim_key: str
    dim_key: str
    join_type: Literal["inner", "left", "right", "full"] = "inner"

    @field_validator("join_type", mode="before")
    @classmethod
    def validate_join_type(cls, value):
        if isinstance(value, str):
            value_lower = value.lower()
            valid_types = ["inner", "left", "right", "full"]
            if value_lower in valid_types:
                return value_lower
            else:
                raise ValueError(
                    f"Invalid join_type: {value}. Valid options are: {valid_types}"
                )
        return value


class DimTable(BaseModel):
    name: str
    description: str
    columns: List[Column]
    hierarchies: List[Hierarchy] | None = None


class Level(BaseModel):
    column_name: str


class Hierarchy(BaseModel):
    name: str
    type: Literal["recursive", "levels"]
    description: str
    column_name: str | None = None
    levels: List[Level] | None = None

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, value):
        if isinstance(value, str):
            value_lower = value.lower()
            valid_types = ["recursive", "levels"]
            if value_lower in valid_types:
                return value_lower
            else:
                raise ValueError(
                    f"Invalid type: {value}. Valid options are: {valid_types}"
                )
        return value
