from collections.abc import Container

import sqlglot
import sqlglot.expressions


def remove_expression_part(child: sqlglot.Expression) -> None:
    """
    Remove the specified expression from its parent, respecting the logical structure.
    """
    parent = child.parent
    if parent is None:
        raise ValueError("Cannot remove child from parent because it has no parent")

    if isinstance(parent, sqlglot.expressions.And | sqlglot.expressions.Or):
        # Ands have a .this and .expression
        parent.replace(parent.expression if parent.this == child else parent.this)
    elif isinstance(parent, sqlglot.expressions.Where):
        # If we're in an and, we should just be a tru
        grandparent = parent.parent
        assert grandparent is not None
        grandparent.set("where", None)
    elif isinstance(parent, sqlglot.expressions.Paren):
        remove_expression_part(parent)
    elif isinstance(parent, sqlglot.expressions.Not):
        # This could happen if we're in a statement like
        # x not in (1, 2, 3, 4, 5))
        #
        # Which becomes:
        # not (x in (1, 2, 3, 4, 5))
        #
        # Leaving an empty not isn't valid so just remove it.
        remove_expression_part(parent)
    elif isinstance(parent, sqlglot.expressions.If):
        # If we're in a case statement, we could remove this branch.
        # If the case statement is empty remove everything.

        # The If statement, has the comparision which is stored
        # in this .this

        # Otherwise the child could be in the true
        # or false branches.

        if parent.this == child:
            grandparent = parent.parent
            assert grandparent is not None
            if isinstance(grandparent, sqlglot.expressions.Case):
                ifs = grandparent.args["ifs"]
                assert parent in ifs
                ifs = [x for x in ifs if x != parent]
                if len(ifs) == 0:
                    remove_expression_part(grandparent)
                else:
                    grandparent.set("ifs", ifs)
            else:
                raise ValueError(
                    f"Cannot remove If child from parent of type {type(grandparent)} {grandparent.sql()}"
                )
        else:
            # we are in one of the two value branches.
            raise ValueError(
                f"Cannot remove child because its present in a true or false branch from parent of type {type(parent)} {parent.sql()}"
            )
    else:
        raise ValueError(f"Cannot remove child from parent of type {type(parent)} {parent.sql()}")


def filter_column_references_statement(
    *, sql: str, allowed_column_names: Container[str], dialect: str = "duckdb"
) -> sqlglot.Expression:
    """
    Filter SQL statement to remove predicates with columns not in allowed_column_names.

    Args:
        sql: The SQL statement to filter
        allowed_column_names: Container of column names that should be preserved
        dialect: The SQL dialect to use for parsing (default is "duckdb")

    Returns:
        Filtered SQLGlot expression with non-allowed columns removed

    Raises:
        ValueError: If a column can't be cleanly removed due to interactions with allowed columns
    """
    # Parse and optimize the statement for predictable traversal
    statement = sqlglot.parse_one(sql, dialect=dialect)

    # If there's no WHERE clause, nothing to filter
    where_clause = statement.find(sqlglot.expressions.Where)
    if where_clause is None:
        return statement

    # Find all column references not in allowed_column_names
    column_refs_to_remove = [
        col
        for col in where_clause.find_all(sqlglot.expressions.Column)
        if col.name not in allowed_column_names
    ]

    # Process each column reference that needs to be removed
    for column_ref in column_refs_to_remove:
        # Find the closest expression containing this column that's a direct child of
        # a logical connector (AND/OR) or the WHERE clause itself
        closest_expression = _find_closest_removable_expression(column_ref)

        # Check if removing this expression would affect allowed columns
        if _can_safely_remove_expression(closest_expression, allowed_column_names):
            remove_expression_part(closest_expression)
        else:
            raise ValueError(
                f"Column '{column_ref.name}' is involved with allowed columns that cannot be eliminated: "
                f"'{closest_expression.sql()}'"
            )

    return statement


def _find_closest_removable_expression(
    column_ref: sqlglot.expressions.Column,
) -> sqlglot.expressions.Expression:
    """Find the closest parent expression that can be safely removed as a unit."""
    current: sqlglot.expressions.Expression = column_ref
    while current.parent is not None and not isinstance(
        current.parent, sqlglot.expressions.And | sqlglot.expressions.Or | sqlglot.expressions.Where
    ):
        current = current.parent

    if current.parent is None:
        raise ValueError(f"Could not find removable parent for column {column_ref.name}")

    return current


def _can_safely_remove_expression(
    expression: sqlglot.expressions.Expression, allowed_column_names: Container[str]
) -> bool:
    """
    Check if an expression can be safely removed without affecting allowed columns.

    Args:
        expression: The expression to check
        allowed_column_names: Container of allowed column names

    Returns:
        True if the expression can be safely removed, False otherwise
    """
    # If the parent isn't a supported type, we can't safely remove it
    if not isinstance(
        expression.parent,
        sqlglot.expressions.Predicate
        | sqlglot.expressions.DPipe
        | sqlglot.expressions.Array
        | sqlglot.expressions.PropertyEQ
        | sqlglot.expressions.Binary
        | sqlglot.expressions.Condition
        | sqlglot.expressions.And
        | sqlglot.expressions.Or
        | sqlglot.expressions.Where,
    ):
        return False

    # Check if this expression references any allowed columns
    allowed_columns_referenced = [
        col.name
        for col in expression.find_all(sqlglot.expressions.Column)
        if col.name in allowed_column_names
    ]

    # If there are no allowed columns referenced, it's safe to remove
    return len(allowed_columns_referenced) == 0
