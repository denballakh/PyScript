__all__ = [
    "Lexer",
    "Parser",
    "Visitor",
]

from abc import ABCMeta

from .lexer import Lexer, Token
from .parser import Parser


class Visitor(metaclass=ABCMeta):
    def visit_literal_expr(self, expr): pass
    def visit_variable_expr(self, expr): pass
    def visit_access_expr(self, expr): pass
    def visit_call_expr(self, expr): pass
    def visit_array_expr(self, expr): pass
    def visit_group_expr(self, expr): pass
    def visit_unary_expr(self, expr): pass
    def visit_binary_expr(self, expr): pass
    def visit_assign_expr(self, expr): pass
    def visit_declaration_expr(self, expr): pass

    def visit_expression_stmt(self, stmt): pass
    def visit_block_stmt(self, stmt): pass
    def visit_declaration_stmt(self, stmt): pass
    def visit_function_stmt(self, stmt): pass
    def visit_class_stmt(self, stmt): pass
    def visit_if_stmt(self, stmt): pass
    def visit_for_stmt(self, stmt): pass
    def visit_while_stmt(self, stmt): pass
    def visit_try_stmt(self, stmt): pass
    def visit_throw_stmt(self, stmt): pass
    def visit_break_stmt(self, stmt): pass
    def visit_continue_stmt(self, stmt): pass
    def visit_exit_stmt(self, stmt): pass


def error(where, message):
    if isinstance(where, int):
        _report(where, "", message)
    elif isinstance(where, Token):
        _report(where.line, f" at '{where.lexeme}'", message)


def _report(line, where, message):
    print(f"[line {line}] Error{where}: {message}")
