from typing import Any
from tools import *
from parse import Parser, ParserToken
import cls
import config

class Compiler:
    parser: Parser
    type_to_width = {
        "Num": 1,
        "None": 1
    }

    vars : dict[str, Any] = {}
    funcs: dict[str, Any] = {}
    var_names : list[str]
    func_names: list[str]

    main : list[str] = []
    funcs: list[str] = []
    in_func: bool    = False

    def __init__(self, parser: Parser) -> None:
        self.parser    = parser
        self.var_names = parser.vars
        self.funcs     = parser.funcs

    def add_var(self, var: cls.Var) -> list[str]:
        self.vars[var.name] = var
        self.parser.vars.append(var.name) # add name to the list

        return [var.name, "@DEF"] # TODO automatic reference counting

    def free_var(self, var: cls.Var) -> list[str]:
        self.vars.pop(var.name)
        self.parser.vars.remove(var.name) # remove name from the list

        return [var.name, "@FREE"]

    def compile(self, expr: ParserToken, expect_result: bool = True) -> list[str]:
        if expr.type == "var_arr" or expr.type == "expr_arr":
            result: list[str] = []

            for e in expr.raw:
                ssert(type(e) != str, "cant compile a str expression")

                result += self.compile(e, expect_result=False) # todo remember to use expect_result

            return result
        else:
            result         : list[str] = []
            optional_result: list[str] = []

            match expr.type:
                case "var_set":
                    pass

                case "var_def":
                    name = expr.data["name"]; t = expr.data["type"]

                    result = self.add_var(cls.Var(name, t, self.type_to_width[t], self))
                    optional_result = [name]

                case "var_free":
                    name = expr.data["keyword"]

                    result = self.free_var(self.vars[name])

                case "var_return":
                    pass

                case "var_op":
                    result = [""] # todo shunting yard

                    return " ".join(result)

                case "var": # todo fill out var # also fix var parsing
                    if type(expr[0]) == str:
                        if len(expr[0]) == 1: # its a variable
                            result = expr[0]
                    else:
                        raise NotImplementedError

                case "imm":
                    pass

            if expect_result:
                return result + optional_result
            else:
                return result

    def output(self, file_name: str) -> None:
        with open(file_name, "w") as f:
            f.write("\n".join(self.funcs + self.main))
