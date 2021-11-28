from tools import *
from typing import Any

class ParserToken(Sequence):
    def __init__(self, type: str, data: dict[str, Any], raw: list[str | Any]):
        self.type = type
        self.data = data
        self.raw = raw

    def __getitem__(self, index: int) -> T:
        return self.raw[index]

    def __len__(self) -> int:
        return len(self.raw)

    def __repr__(self) -> str:
        if len(self) > 3:
            newline = "\n"

            return f"({self.type}:{newline}{f', {newline}'.join([f'{x}' for x in self.raw])}{newline})"
        else:
            return f"({self.type}: {[x for x in self.raw]})"

class Parser:
    types = ["Num"]
    vars  = []
    funcs = []
    ops   = ["+", "-", "*", "/", "%", "&", "^", "|"]

    def __init__(self, tokens: Reader[str]) -> None:
        self.tokens = tokens

    def parenize(self, first: bool = True) -> list[str | list]:
        if first:
            first_token = self.tokens.read() # eat the first parenthesis

            if first_token != "(": error("first token wasnt a parenthesis")

        # last token read is a paren
        result: list[str | list] = []

        while True:
            token = self.tokens.read()

            match token:
                case ")":
                    return result

                case "(":
                    result.append(self.parenize(first = False)) # go down the line

                case _:
                    result.append(token)

    def find_token_type(self, token: ParserToken) -> str: # todo make it check if token is correct (length & types) # todo expr_arr 
        match len(token):
            case 0:
                return "empty"

            case 1:
                if token[0] in self.vars:
                    token.data = {
                        "var": token[0]
                    }

                    return "var"

                elif type(token[0]) == ParserToken:
                    return "var_arr"

                else:
                    token.data = {
                        "imm": token[0]
                    }

                    return "imm"

        if token[1] == "=": # var_set
            token.data = {
                "source": token[0], 
                "dest"  : token[2]
            }

            return "var_set"

        elif token[1] in self.ops:
            return "var_op"

        else:
            first = token[0]

            match first:
                case "free" | "return":
                    token.data = {"keyword": token[1]}

                    return f"var_{first}"

                case "func" | "proc":
                    token.data = {
                        "func_type": token[0],
                        "name"     : token[1],
                        "ret_type" : token[2],
                        "args"     : token[3],
                        "code"     : token[4]
                    }

                    return f"{first}_def"

                case _:
                    if type(first) == str:
                        if first in self.types:
                            token.data = {
                                "type": token[0],
                                "name": token[1]
                            }

                            return "var_def"

                        elif first in self.funcs:
                            token.data = {
                                "name": token[0],
                                "args": token[1]
                            }
                            
                            return "func_call"

                    elements_are_singles = []
                    for x in token.raw:
                        if type(x) == str:
                            if x.isnumeric() or x in self.vars:
                                elements_are_singles.append(True)
                            else:
                                elements_are_singles.append(False)
                        elif type(x) == ParserToken:
                            elements_are_singles.append(True)

                    if any(elements_are_singles):
                        return "var_arr"

        return "undefined"

    def list_to_token(self, ls: list[str | list]) -> ParserToken:
        result = ParserToken("undefined", {}, [])

        for item in ls:
            if type(item) == str:
                result.raw.append(item)
                
            elif type(item) == list:
                result.raw.append(self.list_to_token(item))

        result.type = self.find_token_type(result)

        return result


    def parse(self) -> ParserToken:
        result_1 = self.parenize(self.tokens)

        result_2 = self.list_to_token(result_1)

        return result_2
