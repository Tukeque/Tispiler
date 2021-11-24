from tools import *
from typing import Any
from copy import deepcopy as copy

class ParserToken:
    def __init__(self, type: str, data: dict[str, Any], raw: list[str]):
        self.type = type
        self.data = data
        self.raw = raw

class ParserRule:
    def __init__(self, type: str, childs: list = [], array: list[str] = [], is_name: bool = False, is_number: bool = False, numerous: bool = False, raw: str = "BEAN"):
        self.type = type

        self.childs = childs
        self.array = array
        self.is_name = is_name
        self.is_number = is_number
        self.numerous = numerous
        self.raw = raw
        self.is_optional = False

    def optional(self):
        copied = copy(self)
        copied.is_optional = True

        return copied

types = ["Num", "None"]
used_tokens = [] # TODO fill out

#* Rules
def raw_rule(token: str) -> ParserRule: return ParserRule("raw", raw = token)
type      = ParserRule("in_array", array = types)
name      = ParserRule("not_in_array", array = used_tokens, is_name = True)
number    = ParserRule("not_in_array", array = used_tokens, is_number = True)
operation = ParserRule("in_array", array = [x for x in "+-*/%"])
expr      = None

var_def    = ParserRule("childs", childs = [type, raw_rule(":"), name])
var_set    = ParserRule("childs", childs = [expr, raw_rule("="), expr])
var_free   = ParserRule("childs", childs = [raw_rule("free"), name])
func_def   = ParserRule("childs", childs = []) # todo
proc_def   = ParserRule("childs", childs = []) # todo
var_return = ParserRule("childs", childs = [raw_rule("return"), expr])

# mathematical expressions
var_op = None
var_op_optional = None
var_op = ParserRule("childs", childs = [expr, operation.optional(), var_op_optional])
var_op_optional = var_op.optional()

# var manipulation
var_index = ParserRule("childs", childs = [expr, raw_rule("["), expr, raw_rule("]")])
args = ParserRule("childs", childs = [var_def], numerous = True)
func_call = ParserRule("childs", childs = [name, raw_rule("("), args, raw_rule(")")])
var_access = ParserRule("childs", childs = [expr, raw_rule("."), expr])

# todo conditionals, control flow, structs & objects

default_expr = ParserRule("choose", childs = [expr, var_def, var_set, var_free, func_def, proc_def, var_return, var_op, var_index, func_call, var_access])
expr_array = ParserRule("childs", childs = [expr], numerous = True)

sub_expr = ParserRule("choose", childs = [default_expr, expr_array])
paren_expr = ParserRule("childs", childs = [raw_rule("("), sub_expr, raw_rule(")")])

expr = ParserRule("choose", childs = [paren_expr, name, number])
program = expr

class Parser: # TODO # LL2 parser
    def __init__(self, tokens: Reader[str], program: ParserRule) -> None:
        self.tokens = tokens 
        self.program = program

    def parse(self) -> list[ParserToken]:
        exit() # todo
