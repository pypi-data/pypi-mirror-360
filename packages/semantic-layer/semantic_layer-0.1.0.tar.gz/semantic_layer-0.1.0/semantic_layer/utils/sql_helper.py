from sqlglot.expressions import EQ, Column, Condition, column, condition


def generate_on_clause(
    source_table: str, source_col: str, dest_table: str, dest_col: str
) -> EQ:
    return column(source_col, source_table).eq(column(dest_col, dest_table))
