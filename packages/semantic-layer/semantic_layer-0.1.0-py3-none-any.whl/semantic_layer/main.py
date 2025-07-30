from datetime import datetime
from typing import Dict, List

from sqlglot import select
from sqlglot.expressions import Column, table_

from semantic_layer.models import (
    FactTable,
    DimTable,
    ChartProperties,
    ChartColumn,
)

from semantic_layer.utils import generate_on_clause, SQLTypes


def generate_query(
    chart_properties: ChartProperties, fact_table: FactTable, dims: List[DimTable]
):
    """
    Generates a SQL query for a chart based on the provided chart properties, fact table,
    and dimension tables. The query includes selected columns, filters, joins, and grouping
    based on the input parameters.
    Args:
        chart_properties (ChartProperties): Properties of the chart, including metrics,
            dimensions, and filters.
        fact_table (FactTable): The fact table containing the main data for the query.
        dims (List[DimTable]): A list of dimension tables related to the fact table.
    Returns:
        str: A SQL query string formatted for the Trino dialect.
    The function performs the following steps:
        1. Extracts column information from the fact table and dimension tables.
        2. Constructs the SELECT clause with columns from the fact table and dimension tables.
        3. Applies filters from the chart properties and dimensions to create the WHERE clause.
        4. Joins dimension tables to the fact table based on their relationships.
        5. Groups the query results by the selected columns.
        6. Returns the final SQL query string.
    Notes:
        - The function assumes that the `ChartColumn` class provides methods like
          `encode_select()` and `encode_where()` for generating SQL expressions.
        - The `generate_on_clause` function is used to create join conditions between tables.
        - The query is formatted for the Trino SQL dialect.
    """
    fact_cols: Dict[str, SQLTypes] = {
        column.name: column.data_type for column in fact_table.columns
    }
    dim_cols = {
        dim.name: {col.name: col.data_type for col in dim.columns} for dim in dims
    }

    fact_select_cols: List[ChartColumn] = [
        ChartColumn(
            name=metric.column_name,
            table=fact_table.name,
            expression=metric.expression,
            data_type=fact_cols[metric.column_name],
        )
        for metric in chart_properties.metrics
        if metric.table == fact_table.name
    ] + [
        ChartColumn(
            name=dim.column_name,
            table=fact_table.name,
            data_type=fact_cols[dim.column_name],
        )
        for dim in chart_properties.dimensions
        if dim.column_name in fact_cols
    ]
    dims_select_cols: List[ChartColumn] = [
        ChartColumn(
            name=metric.column_name,
            table=metric.table,
            expression=metric.expression,
            data_type=dim_cols[metric.table][metric.column_name],
        )
        for metric in chart_properties.metrics
        if metric.table in dim_cols.keys()
        and metric.column_name in dim_cols[metric.table]
    ] + [
        ChartColumn(
            name=dim.column_name,
            table=dim.table,
            data_type=dim_cols[dim.table][dim.column_name],
        )
        for dim in chart_properties.dimensions
        if dim.table in dim_cols.keys()
    ]
    dims_select_cols = [col for col in dims_select_cols if col not in fact_select_cols]
    final_select = [col.encode_select() for col in fact_select_cols] + [
        col.encode_select() for col in dims_select_cols
    ]
    all_filters = []
    if chart_properties.filters is not None:
        all_filters = [curr_filter for curr_filter in chart_properties.filters]
    all_filters += [
        curr_filter
        for dim in chart_properties.dimensions
        if dim.filters is not None
        for curr_filter in dim.filters
    ]
    fact_where_cols = [
        ChartColumn(
            name=curr_filter.column_name,
            table=fact_table.name,
            operation=curr_filter.operation,
            where_value=curr_filter.value,
            data_type=fact_cols[curr_filter.column_name],
        )
        for curr_filter in all_filters
        if curr_filter.column_name in fact_cols
    ]
    fact_where_cols_names = [curr_filter.name for curr_filter in fact_where_cols]
    dim_where_cols = [
        ChartColumn(
            name=curr_filter.column_name,
            table=curr_filter.table_name,
            operation=curr_filter.operation,
            where_value=curr_filter.value,
            data_type=dim_cols[curr_filter.table_name][curr_filter.column_name],
        )
        for curr_filter in all_filters
        if curr_filter.table_name in dim_cols.keys()
        and curr_filter.column_name not in fact_where_cols_names
    ]

    dim_where_cols = [col for col in dim_where_cols if col not in fact_where_cols]
    query = select(*final_select).from_(table_(fact_table.name))
    if len(dims_select_cols) > 0 or len(dim_where_cols) > 0:
        combined_joined_cols = [col for col in dims_select_cols] + [
            col for col in dim_where_cols
        ]
        for dim_table in {dim.table for dim in combined_joined_cols}:
            dim_in_fact = [
                (
                    dim_fact.join_type,
                    dim_fact.table_name,
                    dim_fact.dim_key,
                    dim_fact.fact_dim_key,
                )
                for dim_fact in fact_table.dimensions
                if dim_fact.name == dim_table
            ][0]
            query = query.join(
                table_(dim_table),
                join_type=dim_in_fact[0],
                on=generate_on_clause(
                    source_table=dim_in_fact[1],
                    source_col=dim_in_fact[2],
                    dest_table=fact_table.name,
                    dest_col=dim_in_fact[3],
                ),
            )
    query = query.group_by(*[col for col in final_select if isinstance(col, Column)])
    combined_where_cols = [
        col.encode_where() for col in fact_where_cols + dim_where_cols
    ]
    if len(combined_where_cols) > 0:
        query = query.where(*combined_where_cols)
    return query.sql(pretty=True, dialect="trino")


if __name__ == "__main__":
    fact_table = FactTable(
        **{
            "name": "sales_fact",
            "description": "This table is the sales fact table.\n",
            "columns": [
                {"name": "sale_id", "description": "heshbonit", "data_type": "INTEGER"},
                {
                    "name": "taarich",
                    "description": "The date and time of the sale.",
                    "data_type": "TIMESTAMP",
                },
                {
                    "name": "makat",
                    "description": "The unique identifier for the product sold.",
                    "data_type": "STRING",
                },
                {
                    "name": "amount",
                    "description": "The amount of the sale.",
                    "data_type": "INTEGER",
                },
                {
                    "name": "price",
                    "description": "The price of the product sold.",
                    "data_type": "FLOAT",
                },
                {
                    "name": "snif_id",
                    "description": "The branch where the sale occurred.",
                    "data_type": "INTEGER",
                },
            ],
            "dimensions": [
                {
                    "name": "dim_makat",
                    "table_name": "dim_makat",
                    "fact_dim_key": "makat",
                    "dim_key": "makat",
                    "join_type": "inner",
                },
                {
                    "name": "dim_snif",
                    "table_name": "dim_snif",
                    "fact_dim_key": "snif_id",
                    "dim_key": "snif_id",
                    "join_type": "inner",
                },
            ],
        }
    )
    dim_makat = DimTable(
        **{
            "name": "dim_makat",
            "description": "This table contains product information.\n",
            "columns": [
                {
                    "name": "makat",
                    "description": "The unique identifier for the product.",
                    "data_type": "string",
                    "primary_key": True,
                },
                {
                    "name": "mishkal",
                    "description": "The weight of the product.",
                    "data_type": "float",
                },
                {
                    "name": "shem_makat",
                    "description": "The name of the product.",
                    "data_type": "string",
                },
            ],
        }
    )
    dim_snif = DimTable(
        **{
            "name": "dim_snif",
            "description": "This table contains information about branches (snifs).\nEach branch has a unique identifier and associated details.\n",
            "columns": [
                {
                    "name": "snif_id",
                    "description": "The unique identifier for the branch.",
                    "data_type": "integer",
                    "primary_key": True,
                },
                {
                    "name": "godel",
                    "description": "size of the branch.",
                    "data_type": "float",
                },
                {
                    "name": "shem_snif",
                    "description": "Last name of the customer.",
                    "data_type": "string",
                },
                {
                    "name": "ir",
                    "description": "The city where the branch is located.",
                    "data_type": "string",
                },
                {
                    "name": "medina",
                    "description": "The state where the branch is located.",
                    "data_type": "string",
                },
            ],
            "hierarchies": [
                {
                    "name": "snif_hierarchy",
                    "type": "levels",
                    "description": "This hierarchy represents the branch structure.\nIt includes the branch ID and its associated details.\n",
                    "levels": [
                        {"column_name": "medina"},
                        {"column_name": "ir"},
                        {"column_name": "snif_id"},
                    ],
                }
            ],
        }
    )
    bar_chart_req = ChartProperties(
        **{
            "dimensions": [
                {
                    "table": "dim_snif",
                    "column_name": "medina",
                    "label": "Branch ID",
                    "hierarchy": True,
                }
            ],
            "metrics": [
                {"table": "sales_fact", "column_name": "amount", "expression": "avg"},
                {"table": "sales_fact", "column_name": "price", "expression": "sum"},
            ],
            "filters": [
                {
                    "table_name": "sales_fact",
                    "column_name": "taarich",
                    "value": datetime(2010, 2, 11, 11, 2, 57),
                    "operation": "eq",
                }
            ],
        }
    )
    print(generate_query(bar_chart_req, fact_table, [dim_makat, dim_snif]))
