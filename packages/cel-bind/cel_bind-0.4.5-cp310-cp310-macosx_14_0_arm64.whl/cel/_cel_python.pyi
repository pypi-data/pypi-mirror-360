"""
Reduced bindings of github.com/google/cel-cpp,supporting static type checking and function extensions
"""
from __future__ import annotations
import typing
__all__ = ['BoolType', 'BytesType', 'CelExpression', 'CheckedExpr', 'Compiler', 'Descriptor', 'DescriptorPool', 'DoubleType', 'FunctionRegistry', 'IntType', 'Interpreter', 'ListType', 'NullType', 'StringType', 'UintType']
class BoolType:
    def __init__(self) -> None:
        ...
class BytesType:
    def __init__(self) -> None:
        ...
class CelExpression:
    pass
class CheckedExpr:
    pass
class Compiler:
    """
    Parses and type-checks an expression.
    """
    def __init__(self, descriptor_pool: DescriptorPool, context: dict[str, BoolType | IntType | UintType | DoubleType | StringType | BytesType | NullType | Descriptor | ListType], function_registry: FunctionRegistry | None) -> None:
        ...
    def compile_to_checked_expr(self, expr: str) -> CheckedExpr:
        """
        Parses and type-checks an expression, returning a reusable CheckedExpr
        """
class Descriptor:
    pass
class DescriptorPool:
    """
    A pool of object descriptions used to type-check CEL expressions.
    """
    def __init__(self) -> None:
        ...
    def add_json_schema(self, name: str, schema: str) -> Descriptor:
        """
        Adds a object description to the pool given a JSON schema.
        """
class DoubleType:
    def __init__(self) -> None:
        ...
class FunctionRegistry:
    """
    Registry for python extension functions to be made available to expressions.
    """
    def __init__(self) -> None:
        ...
    def add_function(self, name: str, func: typing.Callable, return_type: BoolType | IntType | UintType | DoubleType | StringType | BytesType | NullType | Descriptor | ListType, arguments_type: list[BoolType | IntType | UintType | DoubleType | StringType | BytesType | NullType | Descriptor | ListType]) -> None:
        """
        Registers an extension function to be used in expressions.
        """
class IntType:
    def __init__(self) -> None:
        ...
class Interpreter:
    def __init__(self, descriptor_pool: DescriptorPool, context: dict[str, BoolType | IntType | UintType | DoubleType | StringType | BytesType | NullType | Descriptor | ListType], function_registry: FunctionRegistry | None) -> None:
        ...
    def build_expression_plan(self, checked_expr: CheckedExpr) -> CelExpression:
        """
        Builds an execution plan for a checked expression. Execution plan should be reused.
        """
    def evaluate(self, expr_plan: CelExpression, environment: dict[str, typing.Any]) -> bool | int | int | float | str | bytes | None | dict | list:
        """
        Executes a planned expression with the given environment values.
        """
class ListType:
    def __init__(self, arg0: BoolType | IntType | UintType | DoubleType | StringType | BytesType | NullType | Descriptor | ListType) -> None:
        ...
class NullType:
    def __init__(self) -> None:
        ...
class StringType:
    def __init__(self) -> None:
        ...
class UintType:
    def __init__(self) -> None:
        ...
