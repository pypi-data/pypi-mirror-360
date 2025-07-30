from collections.abc import Container

import pytest
import sqlglot
import sqlglot.expressions
import sqlglot.optimizer
import sqlglot.optimizer.normalize
import sqlglot.optimizer.qualify

from . import transforms

RULES_WITHOUT_NORMALIZE = [
    rule
    for rule in sqlglot.optimizer.RULES
    if rule not in (sqlglot.optimizer.normalize.normalize, sqlglot.optimizer.qualify.qualify)
]


def _remove_target_predicate(sql: str, target: str, expected: str) -> None:
    """
    Remove a target predicate from the SQL statement and check if the remaining SQL matches the expected output.

    Args:
        sql: The WHERE clause SQL to analyze
        target: The predicate to remove
        expected: The expected SQL after removal
    """
    # Define constants
    statement_prefix = 'SELECT * FROM "data" AS "data"'
    dialect = "duckdb"

    # Parse the full SQL statement and target predicate
    full_statement = f"{statement_prefix} WHERE {sql}"
    parse_result = sqlglot.parse_one(full_statement, dialect=dialect)
    target_predicate = sqlglot.parse_one(target, dialect=dialect)

    # Optimize the expression before modification
    expression = sqlglot.optimizer.optimize(
        parse_result, rules=RULES_WITHOUT_NORMALIZE, dialect=dialect
    )

    # Find matching predicates
    predicates = list(expression.find_all(sqlglot.expressions.Predicate))
    matching_predicates = [p for p in predicates if p == target_predicate]

    # Assert that we found at least one match
    assert matching_predicates, f"No matching predicate found for: {target}"

    # Remove all matching predicates
    for matched_predicate in matching_predicates:
        assert matched_predicate.parent is not None, "Predicate has no parent"
        transforms.remove_expression_part(matched_predicate)

    # Optimize the modified expression
    optimized = sqlglot.optimizer.optimize(
        expression, rules=RULES_WITHOUT_NORMALIZE, dialect=dialect
    )

    # Extract the WHERE clause and compare with expected
    optimized_where_clause = optimized.find(sqlglot.expressions.Where)
    final_sql = ""
    if optimized_where_clause is not None:
        final_sql = optimized_where_clause.this.sql(dialect=dialect)

    # Assert the result matches the expected output
    assert final_sql == expected, f"Expected '{expected}', got '{final_sql}'"


@pytest.mark.parametrize(
    "sql,target,expected",
    [
        ("""x=1 AND y=1""", '"x" = 1', '"y" = 1'),
        ("""not x=1 AND y=1""", '"x" <> 1', '"y" = 1'),
        ("""x not in (1,2,3)""", '"x" in (1,2,3)', ""),
        ("""x in (1,2,3)""", '"x" in (1,2,3)', ""),
        (
            """x in (1,2,3) or y = case when z = 1 then 5 else z end""",
            '"x" in (1,2,3)',
            '"y" = CASE WHEN "z" = 1 THEN 5 ELSE "z" END',
        ),
        ("""case when x=1 then true else false end""", '"x" = 1', ""),
        (
            """case when x=1 then true when x=2 then true else false end""",
            '"x" = 1',
            'CASE WHEN "x" = 2 THEN TRUE ELSE FALSE END',
        ),
        ("""(x not in (1,2,3) and z = 20)""", '"z" = 20', 'NOT "x" IN (1, 2, 3)'),
        ("""(x not in (1,2,3) OR z = 20)""", '"z" = 20', 'NOT "x" IN (1, 2, 3)'),
        ("""not (x in (1,2,3) OR z = 20)""", '"z" <> 20', 'NOT "x" IN (1, 2, 3)'),
        ("""not (x in (1,2,3) OR z = 20)""", '"x" in (1,2, 3)', '"z" <> 20'),
        ("""not (x in (1,2,3) OR z < 20)""", '"x" in (1,2, 3)', '"z" >= 20'),
        ("""not (x like 'test%')""", "\"x\" like 'test%'", ""),
        (
            """x=1 AND y is null AND z is not null""",
            '"x" = 1',
            '"y" IS NULL AND NOT "z" IS NULL',
        ),
        ("""x=1 AND y=1 AND z=1""", '"x" = 1', '"y" = 1 AND "z" = 1'),
        ("""x=1 AND y=1 AND z=1""", '"z" = 1', '"x" = 1 AND "y" = 1'),
        ("""(x=1 AND y=1) OR z=1""", '"z" = 1', '"x" = 1 AND "y" = 1'),
        ("""(x=1 AND y=1) OR z <> 1""", '"z" <> 1', '"x" = 1 AND "y" = 1'),
        ("""(x=1 AND y=1) OR z <> 1""", '"y" = 1', '"x" = 1 OR "z" <> 1'),
        (
            """(x=1 AND y=1) OR (z <> 1 AND y=1)""",
            '"y" = 1',
            '"x" = 1 OR "z" <> 1',
        ),
        (
            """(x=1 AND y=1) OR not (z <> 1 AND y=1)""",
            '"y" = 1',
            '"x" = 1 OR "y" <> 1 OR "z" = 1',
        ),
        (
            """(x=1 AND y=2) OR z=3""",
            '"y" = 2',
            '"x" = 1 OR "z" = 3',
        ),
    ],
)
def test_remove_logical_predicates(sql: str, target: str, expected: str) -> None:
    _remove_target_predicate(sql, target, expected)


@pytest.mark.parametrize(
    "sql,target",
    [
        # Can't remove x = 1 because its on the false branch.
        ("""case when x > 5 then x = 1 else False end""", '"x" = 1'),
        # Should fail to remove this predicate, because its part of an eq expression.
        ("""x in (1,2,3) or y = case when z = 1 then 5 else z end""", '"z" = 1'),
        # Cannot remove y = 1 because its part of conditional comparison.
        ("""x = (y = 1)""", '"y" = 1'),
        # Cannot remove y = 1 because its part of conditional comparison.
        ("""x <> (y = 1)""", '"y" = 1'),
        ("""x in (y = 1)""", '"y" = 1'),
        ("""coalesce(x, y = 1)""", '"y" = 1'),
        ("""coalesce(y = 1, x)""", '"y" = 1'),
    ],
)
def test_remove_logical_predicates_errors(sql: str, target: str) -> None:
    """
    Test that certain predicates cannot be removed due to their context in the SQL expression.
    """
    with pytest.raises(ValueError):
        _remove_target_predicate(sql, target, "")


@pytest.mark.parametrize(
    "column_names, sql, expected_sql",
    [
        ({"filters"}, """contains(cidr_block, '16')""", ""),
        (
            {},
            """color || '_' || maker in ('red')""",
            "",
        ),
        (
            {},
            """color in ('red')""",
            "",
        ),
        (
            {},
            """color || '_foo' in ('red')""",
            "",
        ),
        (
            {},
            """[color][1] = ['red'][1]""",
            "",
        ),
        ({}, """[color, type] = ['red', 'car']""", ""),
        ({}, """[color, type] = [color, 'car']""", ""),
        ({}, """[color, type] = [color || 'foo', 'car']""", ""),
        ({}, """[color, type] = [color is null, 'car']""", ""),
        ({}, """{'c': color} = {'c': color, 'm': 'bar'}""", ""),
        (
            {"color"},
            """CASE WHEN color = 'red' THEN TRUE ELSE FALSE END""",
            """CASE WHEN "color" = 'red' THEN TRUE ELSE FALSE END""",
        ),
        (
            {},
            """CASE WHEN color = 'red' THEN TRUE ELSE FALSE END""",
            "",
        ),
        (
            {},
            """color = 'red' or (color = 'blue' and type = 'car')""",
            "",
        ),
        (
            {"color"},
            """size % 5 and color = 'red'""",
            """"color" = 'red'""",
        ),
        (
            {"color"},
            """length(size) > 3 and color = 'red'""",
            """"color" = 'red'""",
        ),
        (
            {"color"},
            """substr(make, 0, 10) > 'b' and color = 'red'""",
            """"color" = 'red'""",
        ),
        (
            {"color"},
            """color = 'red' or (color = 'blue' and type = 'car')""",
            """"color" = 'blue' OR "color" = 'red'""",
        ),
        (
            {"color"},
            """color = 'red' or not (color = 'blue' and type = 'car')""",
            """"color" <> 'blue' OR "color" = 'red'""",
        ),
        (
            {"color"},
            """color = 'red' and (color = 'b' || 'lue')""",
            """"color" = 'blue' AND "color" = 'red'""",
        ),
        (
            {"color"},
            """color = 'red' OR (color = 'blue' and type = maker)""",
            """"color" = 'blue' OR "color" = 'red'""",
        ),
        (
            {"color"},
            """not color = 'red' and type = 'car'""",
            """"color" <> 'red'""",
        ),
        (
            {"color"},
            """color != 'red' and type = 'car'""",
            """"color" <> 'red'""",
        ),
        (
            {},
            """color = maker""",
            "",
        ),
        (
            {"color"},
            """CASE WHEN color = 'red' and type = 'car' THEN TRUE ELSE FALSE END""",
            """CASE WHEN "color" = 'red' THEN TRUE ELSE FALSE END""",
        ),
        (
            {"color"},
            """CASE WHEN color = 'red' and (type = 'car' and maker = 'volvo') THEN TRUE ELSE FALSE END""",
            """CASE WHEN "color" = 'red' THEN TRUE ELSE FALSE END""",
        ),
        (
            {"color"},
            """CASE WHEN color = 'red' and not type = 'car' THEN TRUE ELSE FALSE END""",
            """CASE WHEN "color" = 'red' THEN TRUE ELSE FALSE END""",
        ),
        (
            {"color"},
            """CASE WHEN color = 'red' and not (type = 'car') THEN TRUE ELSE FALSE END""",
            """CASE WHEN "color" = 'red' THEN TRUE ELSE FALSE END""",
        ),
        (
            {"color"},
            """CASE WHEN color = 'red' and not ('car' = type) THEN TRUE ELSE FALSE END""",
            """CASE WHEN "color" = 'red' THEN TRUE ELSE FALSE END""",
        ),
        (
            {"color", "maker"},
            """CASE WHEN color = 'red' and (type = 'car' and maker = 'volvo') THEN TRUE ELSE FALSE END""",
            """CASE WHEN "color" = 'red' AND "maker" = 'volvo' THEN TRUE ELSE FALSE END""",
        ),
        (
            {"filter"},
            """not (filter = 'red' and color = 'big_blue' and type = 'car')""",
            """"filter" <> 'red'""",
        ),
        (
            {"type"},
            """not (filter = 'red' and color = 'big_blue' and type = 'car')""",
            """"type" <> 'car'""",
        ),
        (
            {"aws_region"},
            """filter not in (1, 2, 3)""",
            "",
        ),
        (
            {"aws_region"},
            """not filter = 'banana'""",
            "",
        ),
        (
            {"aws_region"},
            """not (filter = 'banana')""",
            "",
        ),
        (
            {"aws_region"},
            """not (filter = 'banana' and color = 'red')""",
            "",
        ),
        (
            {"aws_region"},
            """not (filter is null and filter <> 'banana')""",
            "",
        ),
        (
            {},
            """"filter" = 'a'""",
            "",
        ),
        (
            {"age"},
            """"filter" = 'a' and "age" < 55""",
            """"age" < 55""",
        ),
        (
            {"aws_region", "aws_profile"},
            """"aws_profile" = 'default' AND "aws_region" = 'us-east-1'""",
            """"aws_profile" = 'default' AND "aws_region" = 'us-east-1'""",
        ),
        (
            {"aws_region"},
            """instance_type in ('small', 'large') AND "aws_region" = 'us-east-1'""",
            """"aws_region" = 'us-east-1'""",
        ),
        (
            {"aws_region"},
            """"aws_region" IN ('us-east-1', 'us-east-2')""",
            """"aws_region" IN ('us-east-1', 'us-east-2')""",
        ),
        (
            {"aws_region"},
            """("aws_region" = 'us-east-1' and "filter" = "large") or ("aws_region" = 'us-east-2' and "filter" = "small")""",
            """"aws_region" = 'us-east-1' OR "aws_region" = 'us-east-2'""",
        ),
        (
            {"aws_region"},
            """"aws_region" = 'us-east-1' and "filter" = {"a": [1]}.a[1] """,
            """"aws_region" = 'us-east-1'""",
        ),
        (
            {"aws_region"},
            """"aws_region" = 'us-east-1' and not "filter" = {"a": [1]}.a[1] """,
            """"aws_region" = 'us-east-1'""",
        ),
        (
            {"aws_region"},
            """"aws_region" <> 'us-east-1'""",
            """"aws_region" <> 'us-east-1'""",
        ),
    ],
)
def test_filter_column_references(
    column_names: Container[str], sql: str, expected_sql: str
) -> None:
    dialect = "duckdb"
    full_sql = f'SELECT * FROM "data" AS "data" WHERE {sql}'
    result = transforms.filter_column_references_statement(
        sql=full_sql, allowed_column_names=column_names
    )

    optimized = sqlglot.optimizer.optimize(result, rules=RULES_WITHOUT_NORMALIZE, dialect=dialect)

    optimized_where_clause = optimized.find(sqlglot.expressions.Where)
    final_sql = ""
    if optimized_where_clause is not None:
        where_expression = optimized_where_clause.this
        assert isinstance(where_expression, sqlglot.expressions.Expression), (
            f"Expected WHERE clause to be an Expression, got {type(where_expression)}"
        )
        final_sql = where_expression.sql(dialect=dialect)

    # Assert the result matches the expected output
    assert final_sql == expected_sql, f"Expected '{expected_sql}', got '{final_sql}'"
