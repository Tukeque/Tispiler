from typing import Any
from tools import *
from parse import Parser, ParserToken
from shunt import Shunter
import cls
import config

class Compiler:
    parser : Parser
    shunter: Shunter
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

        self.shunter = Shunter()

    def add_var(self, var: cls.Var) -> list[str]:
        self.vars[var.name] = var
        self.parser.vars.append(var.name) # add name to the list

        return [var.name, "@DEF"] # TODO automatic reference counting

    def free_var(self, var: cls.Var) -> list[str]:
        self.vars.pop(var.name)
        self.parser.vars.remove(var.name) # remove name from the list

        return [var.name, "@FREE"]

    def compile(self, expr: ParserToken | str, expect_result: bool = True, big: bool = False) -> list[str]:
        debug(f"compiling {repr(expr)}")

        if type(expr) == str:
            return [expr]

        if expr.type == "var_arr" or expr.type == "expr_arr":
            result: list[str] = []

            for e in expr.raw:
                ssert(type(e) != str, "cant compile a str expression")

                result += self.compile(e, expect_result=False) # todo remember to use expect_result

            if big:
                self.main += result
            else:
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

                case "var_op": # always used to return
                    compiled_tokens: list[list[str]] = []

                    for token in expr.raw:
                        if token in self.parser.ops:
                            compiled_tokens.append(token)
                        else:
                            compiled_tokens.append(self.compile(token, expect_result=True))

                    tokens = self.shunter.tokenize(compiled_tokens, self.parser)
                    shuntd = self.shunter.shunt   (tokens)
                    result = self.shunter.codeize (shuntd)

                case "var_neg": # always used to return
                    result = ["0", self.compile(expr.data["var"], expect_result=True), "-"]

                case "var": # always used to return # todo fill out var # also fix var parsing
                    if type(expr[0]) == str:
                        if len(expr[0]) == 1: # its a variable
                            result = expr[0]
                    else:
                        raise NotImplementedError

                case "imm": # always used to return
                    result = expr.data["imm"]

            return self.make_return(result, optional_result, expect_result)

    def make_return(self, result: list[str], optional_result: list[str], expect_result: bool):
        appendix = (["\n"] if config.debug else []) # atleast this appendix doesnt kill its host :D

        if expect_result:
            return result + optional_result + appendix
        else:
            return result + appendix

    def output(self, file_name: str) -> None:
        result = []
        for x in (self.funcs + self.main):
            result += [x, " " if x != "\n" else ""]

        result = "".join(result)
        if result[-1] == "\n": result = result[:-1]

        with open(file_name, "w") as f:
            f.write(result)
