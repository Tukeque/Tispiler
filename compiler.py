from typing import Any
from tools import *
from parse import Parser, ParserToken
import classes as cls
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
        
    def emit(self, x) -> None:
        target = self.main if not self.in_func else self.funcs

        if type(x) == str:
            target.append(x)
        elif type(x) == list:
            target += x
        else:
            error("cant append something that isnt a string or a list to the output")

    def add_var(self, var: cls.Var) -> None:
        self.vars[var.name] = var
        self.parser.vars.append(var.name) # add name to the list

        self.emit(f"{var.name} @DEF") # TODO automatic reference counting

    def free_var(self, var: cls.Var) -> None:
        self.vars.pop(var.name)
        self.parser.vars.remove(var.name) # remove name from the list

        self.emit(f"{var.name} @FREE")

    def compile(self, expr: ParserToken) -> None: # todo statical return of object thinger
        if expr.type == "var_arr" or expr.type == "expr_arr":
            for e in expr.raw:
                ssert(type(e) != str, "cant compile a str expression")

                self.compile(e)
        else:
            match expr.type:
                case "var_set":
                    pass

                case "var_def":
                    name = expr.data["name"]
                    self.add_var(cls.Var(name, expr.data["type"], self.type_to_width[name], self))

                case "var_free":
                    self.free_var(self.vars[expr.data["keyword"]])

                case "var_return":
                    pass

                case "var_op":
                    pass

                case "var":
                    pass

                case "imm":
                    pass

    def output(self, file_name: str) -> None:
        with open(file_name, "w") as f:
            f.write("\n".join(self.funcs + self.main))
