from __future__ import annotations
from typing import Any
from decimal import Decimal as PyDecimal

from .. import builder as b

def _make_expr(op: str, *args: Any) -> b.Expression:
    return b.Expression(b.Relationship.builtins[op], *args)

# Coerce a number to Decimal64.
def decimal64(value: b.Producer|int|float|PyDecimal) -> b.Expression:
    if isinstance(value, int):
        return _make_expr("int_to_decimal64", value, b.Decimal64.ref("res"))
    if isinstance(value, float):
        return _make_expr("float_to_decimal64", value, b.Decimal64.ref("res"))
    return _make_expr("decimal64", value, b.Decimal64.ref("res"))

# Coerce a number to Decimal128.
def decimal128(value: b.Producer|int|float|PyDecimal) -> b.Expression:
    if isinstance(value, int):
        return _make_expr("int_to_decimal128", value, b.Decimal128.ref("res"))
    if isinstance(value, float):
        return _make_expr("float_to_decimal128", value, b.Decimal128.ref("res"))
    return _make_expr("decimal128", value, b.Decimal128.ref("res"))

def decimal(value: b.Producer|int|float|PyDecimal) -> b.Expression:
    return decimal128(value)

def parse_decimal64(value: b.Producer|str) -> b.Expression:
    return _make_expr("parse_decimal64", value, b.Decimal64.ref("res"))

def parse_decimal128(value: b.Producer|str) -> b.Expression:
    return _make_expr("parse_decimal128", value, b.Decimal128.ref("res"))
