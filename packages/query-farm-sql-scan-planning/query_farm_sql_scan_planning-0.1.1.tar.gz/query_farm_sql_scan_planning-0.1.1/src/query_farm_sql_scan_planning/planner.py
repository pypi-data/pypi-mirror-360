from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import sqlglot
import sqlglot.expressions
import sqlglot.optimizer.simplify


@dataclass
class BaseFieldInfo:
    """
    The base class for information about a field known for scan planning.
    """

    has_nulls: bool
    has_non_nulls: bool


@dataclass
class RangeFieldInfo[T: Any](BaseFieldInfo):
    """
    Information about a field that has a min and max value.
    """

    min_value: T
    max_value: T


@dataclass
class SetFieldInfo[T: Any](BaseFieldInfo):
    """
    Information about a field where the set of values are known.
    The information about what values that are contained can produce
    false positives.
    """

    values: set[
        T
    ]  # Set of values that are known to be present in the field, false positives are okay.


AnyFieldInfo = (
    SetFieldInfo[Decimal]
    | SetFieldInfo[float]
    | SetFieldInfo[str]
    | SetFieldInfo[int]
    | RangeFieldInfo[int]
    | RangeFieldInfo[None]
)


FileFieldInfo = dict[str, AnyFieldInfo]

# When bailing out we should know why we bailed out if we couldn't evaluate the expression.


class Planner:
    """
    Filter files based on their min/max ranges using AST-parsed expressions.
    """

    def __init__(self, files: list[tuple[str, FileFieldInfo]]):
        """
        Initialize with list of (filename, min_value, max_value) tuples.

        Args:
            file_ranges: List of tuples containing (filename, min_val, max_val)
        """
        self.files = files

    def _eval_predicate(
        self,
        file_info: FileFieldInfo,
        node: sqlglot.expressions.Predicate,
    ) -> bool | None:
        """
        Check if a file's range could satisfy a single condition.

        For a file to potentially contain data satisfying the condition,
        there must be some overlap between the file's range and the condition's range.
        """
        assert isinstance(node, sqlglot.expressions.Predicate)
        assert isinstance(node, sqlglot.expressions.Binary), (
            f"Expected a binary predicate but got {node} {type(node)}"
        )

        if isinstance(node, sqlglot.expressions.Is):
            return self._evaluate_node_is(node, file_info)

        # Handle comparison operations
        if not isinstance(node.left, sqlglot.expressions.Column):
            return None

        # The thing on the right side should be something that can be evaluated against a range.
        # ideally, its going to be a
        assert isinstance(
            node.right,
            sqlglot.expressions.Literal
            | sqlglot.expressions.Null
            | sqlglot.expressions.Neg,
        ), (
            f"Expected a literal or null on righthand side of predicate {node} got a {type(node.right)}"
        )

        right_val = node.right.to_py()

        left_val = node.left
        assert isinstance(left_val, sqlglot.expressions.Column), (
            f"Expected a column on left side of {node}, got {left_val}"
        )
        assert isinstance(left_val.this, sqlglot.expressions.Identifier), (
            f"Expected an identifier on left side of {node}, got {left_val.this}"
        )
        referenced_field_name = left_val.this.this

        field_info = file_info.get(referenced_field_name)

        if field_info is None:
            return None

        if isinstance(field_info, SetFieldInfo):
            match type(node):
                case sqlglot.expressions.EQ:
                    if right_val is None:
                        return False
                    return right_val in field_info.values
                case sqlglot.expressions.NEQ:
                    if right_val is None:
                        return False
                    return right_val not in field_info.values
                case _:
                    raise ValueError(
                        f"Unsupported operator type for SetFieldInfo: {type(node)}"
                    )

        if type(node) is sqlglot.expressions.NullSafeNEQ:
            if right_val is not None and field_info.has_non_nulls is False:
                return True
            return not (field_info.min_value == field_info.max_value == right_val)
        elif type(node) is sqlglot.expressions.NullSafeEQ:
            if right_val is None and field_info.has_non_nulls:
                return True
            if field_info.min_value is None or field_info.max_value is None:
                return False
            assert right_val is not None
            return field_info.min_value <= right_val <= field_info.max_value

        if field_info.min_value is None or field_info.max_value is None:
            return False

        if right_val is None:
            return False

        match type(node):
            case sqlglot.expressions.EQ:
                return field_info.min_value <= right_val <= field_info.max_value
            case sqlglot.expressions.NEQ:
                return not (field_info.min_value == field_info.max_value == right_val)
            case sqlglot.expressions.LT:
                return field_info.min_value < right_val
            case sqlglot.expressions.LTE:
                return field_info.min_value <= right_val
            case sqlglot.expressions.GT:
                return field_info.max_value > right_val
            case sqlglot.expressions.GTE:
                return field_info.max_value >= right_val
            case sqlglot.expressions.NullSafeEQ:
                if right_val is None and field_info.has_non_nulls:
                    return True
                return field_info.min_value <= right_val <= field_info.max_value
            case sqlglot.expressions.NullSafeNEQ:
                if right_val is not None and field_info.has_non_nulls is False:
                    return True
                return not (field_info.min_value == field_info.max_value == right_val)
            case _:
                raise ValueError(f"Unsupported operator type: {type(node)}")

    def _evaluate_node_connector(
        self, node: sqlglot.Expression, file_info: FileFieldInfo
    ) -> bool | None:
        """
        Evaluate a connector node (AND, OR, XOR) against a file's field info.

        Returns True, False, or None if the expression cannot be evaluated.
        """
        op_map: dict[
            type[sqlglot.expressions.Connector], Callable[[bool, bool], bool]
        ] = {
            sqlglot.expressions.And: lambda left, right: left and right,
            sqlglot.expressions.Or: lambda left, right: left or right,
            sqlglot.expressions.Xor: lambda left, right: left ^ right,
        }

        for expr_type, op in op_map.items():
            if isinstance(node, expr_type):
                left_result = self._evaluate_sql_node(node.left, file_info)
                right_result = self._evaluate_sql_node(node.right, file_info)
                if left_result is None or right_result is None:
                    return None
                return op(left_result, right_result)

        raise ValueError(f"Unsupported connector type: {type(node)}")

    def _evaluate_node_in(
        self, node: sqlglot.expressions.In, file_info: FileFieldInfo
    ) -> bool | None:
        """
        Evaluate an IN predicate against a file's field info.
        Returns True if the left side is in the set of values on the right side,
        False if it is not, and None if the left side cannot be evaluated.
        """
        in_val = node.this

        # If the left side is a NULL, then it can't be in anything.
        if isinstance(in_val, sqlglot.expressions.Null):
            return False

        # So the left side should be a column, but if its not just kind of give up.
        if not isinstance(in_val, sqlglot.expressions.Column):
            # FIXME: this could be improved because if the left side is a literal, we could
            # do a little better job of checking if we have set presence for that literal.
            return None

        assert isinstance(in_val, sqlglot.expressions.Column), (
            f"Expected a column on left side of {node}, got {in_val}"
        )
        assert isinstance(in_val.this, sqlglot.expressions.Identifier), (
            f"Expected an identifier on left side of {node}, got {in_val.this}"
        )

        if len(node.expressions) == 0:
            return False

        for in_exp in node.expressions:
            assert isinstance(
                in_exp,
                sqlglot.expressions.Literal
                | sqlglot.expressions.Neg
                | sqlglot.expressions.Null,
            ), (
                f"Expected a literal in in side of {node}, got {in_exp} type {type(in_exp)}"
            )
            if self._eval_predicate(
                file_info,
                sqlglot.expressions.EQ(this=in_val, expression=in_exp),
            ):
                return True
        return False

    def _evaluate_node_not_in(
        self, node: sqlglot.expressions.In, file_info: FileFieldInfo
    ) -> bool | None:
        """
        Evaluate a NOT IN predicate against a file's field info.
        Returns True if the left side is not in the set of values on the right side,
        False if it is, and None if the left side cannot be evaluated.
        """
        in_val = node.this

        if isinstance(in_val, sqlglot.expressions.Null):
            return False

        if not isinstance(in_val, sqlglot.expressions.Column):
            return None
        assert isinstance(in_val, sqlglot.expressions.Column), (
            f"Expected a column on left side of {node}, got {in_val}"
        )
        assert isinstance(in_val.this, sqlglot.expressions.Identifier), (
            f"Expected an identifier on left side of {node}, got {in_val.this}"
        )

        if len(node.expressions) == 0:
            return True

        for in_exp in node.expressions:
            assert isinstance(
                in_exp, sqlglot.expressions.Literal | sqlglot.expressions.Neg
            ), (
                f"Expected a literal in in side of {node}, got {in_exp} type {type(in_exp)}"
            )
            if self._eval_predicate(
                file_info,
                sqlglot.expressions.NEQ(this=in_val, expression=in_exp),
            ):
                return True
        return False

    def _evaluate_node_is(
        self, node: sqlglot.expressions.Is, file_info: FileFieldInfo
    ) -> bool:
        """
        Evaluate an IS NULL or IS NOT NULL predicate against a file's field info.
        Returns True if the left side is NULL or NOT NULL, False otherwise.
        """
        in_val = node.left
        assert isinstance(in_val, sqlglot.expressions.Column), (
            f"Expected a column on left side of {node}, got {in_val}"
        )
        assert isinstance(in_val.this, sqlglot.expressions.Identifier), (
            f"Expected an identifier on left side of {node}, got {in_val.this}"
        )
        assert isinstance(node.right, sqlglot.expressions.Null), (
            f"Expected a NULL literal on right side of {node}, got {node.right}"
        )
        target_field_name = in_val.this.this
        target_field_info = file_info.get(target_field_name)
        if target_field_info is None:
            raise ValueError(f"Unsupported variable name: {target_field_name}.")
        return target_field_info.has_nulls

    def _evaluate_node_predicate(
        self, node: sqlglot.Expression, file_info: FileFieldInfo
    ) -> bool | None:
        """
        Evaluate a predicate node against a file's field info.
        Returns True, False, or None if the expression cannot be evaluated.
        """
        if isinstance(node, sqlglot.expressions.In):
            return self._evaluate_node_in(node, file_info)

        assert isinstance(node, sqlglot.expressions.Predicate)
        assert isinstance(node, sqlglot.expressions.Binary), (
            f"Expected a binary predicate but got {node} {type(node)}"
        )

        if isinstance(node, sqlglot.expressions.Is):
            return self._evaluate_node_is(node, file_info)

        return self._eval_predicate(file_info, node)

    def _evaluate_node_case(
        self, node: sqlglot.expressions.Case, file_info: FileFieldInfo
    ) -> bool | None:
        """
        Evaluate a CASE statement against a file's field info.
        """
        for if_statement in node.args["ifs"]:
            assert isinstance(if_statement, sqlglot.expressions.If), (
                f"Expected an If statement in Case but got {if_statement}"
            )
            assert isinstance(if_statement.this, sqlglot.expressions.Predicate), (
                f"Expected a Predicate in If statement but got {if_statement.this}"
            )
            clause_result = self._evaluate_sql_node(if_statement.this, file_info)
            if clause_result is None:
                return None
            if clause_result:
                return self._evaluate_sql_node(if_statement.args["true"], file_info)
        if "default" in node.args:
            return self._evaluate_sql_node(node.args["default"], file_info)
        # the default is null, so don't return the file.
        return False

    def _evaluate_sql_node(
        self, node: sqlglot.Expression, file_info: FileFieldInfo
    ) -> bool | None:
        """
        Evaluate a SQL node against a file's field info.
        Returns True, False, or None if the expression cannot be evaluated.
        """
        if isinstance(node, sqlglot.expressions.Connector):
            return self._evaluate_node_connector(node, file_info)
        elif isinstance(node, sqlglot.expressions.Predicate):
            return self._evaluate_node_predicate(node, file_info)
        elif isinstance(node, sqlglot.expressions.Not):
            if isinstance(node.this, sqlglot.expressions.In):
                # Handle 'not in' operations
                return self._evaluate_node_not_in(node.this, file_info)
            # Handle 'not' operations
            return not self._evaluate_sql_node(node.this, file_info)
        elif isinstance(node, sqlglot.expressions.Boolean):
            return node.to_py()
        elif isinstance(node, sqlglot.expressions.Case):
            return self._evaluate_node_case(node, file_info)
        elif isinstance(node, sqlglot.expressions.Null):
            return False
        else:
            raise ValueError(f"Unsupported node type: {type(node)}")

        return False

    def get_matching_files(
        self, expression: str, *, dialect: str = "duckdb"
    ) -> set[str]:
        """
        Get a set of files that match the given SQL expression.
        Args:
            expression: The SQL expression to evaluate.
            dialect: The SQL dialect to use for parsing the expression.
            Returns:
                A set of filenames that match the expression.
        """
        parse_result = sqlglot.parse_one(expression, dialect=dialect)

        # Simplify the parsed expression, move all of the literals to the right side
        parse_result = sqlglot.optimizer.simplify.simplify(parse_result)

        matching_files = set()

        for filename, file_info in self.files:
            eval_result = self._evaluate_sql_node(parse_result, file_info)
            if eval_result is None or eval_result is True:
                # If the expression evaluates to True or cannot be evaluated, add the file
                # to the result set since the caller will be able to filter the rows further.
                matching_files.add(filename)

        return matching_files
