from tools import *
from parse import Parser

class Shunter:
    def __init__(self) -> None:
        pass

    def convert_op(self, x: str):
        return {
            "+": "@ADD",
            "-": "@SUB",
            "*": "@MLT",
            "/": "@DIV",
            "%": "@MOD",
            "&": "@AND",
            "|": "@OR",
            "^": "@XOR"
        }[x]
    
    def tokenize(self, tokens: list[list[str] | str], parser: Parser) -> Reader[Token]:
        result: list[Token] = []

        for token in tokens:
            if type(token) == str:
                if token in parser.ops:
                    result.append(Token("op",    single=token))
                elif token in ["(", ")"]:
                    result.append(Token("paren", single=token))
                elif token.isnumeric():
                    result.append(Token("imm",   single=token))
            else:
                result.append(Token("var", single=token))

        return Reader[result]

    def shunt(self, tokens: Reader[Token]) -> Reader[Token]: # todo test
        operators: list[Token] = []
        output   : list[Token] = []

        while not tokens.finished():
            token = tokens.read()

            if token.type in ["var", "imm"]:
                output.append(token)

            elif token.type == "op":
                while (len(operators) >= 1 and operators[-1].get() != "(") and (operators[-1].precedence >= token.precedence or (operators[-1].precedence == token.precedence and token.associativity == "left")):
                    output.append(operators.pop())

                operators.append(token)

            elif token.get() == "(":
                operators.append(token)

            elif token.get() == ")":
                while operators[-1].get() != "(":
                    assert len(operators) != 0 # for debug

                    output.append(operators.pop())

                assert operators[-1].get() == "("
                operators.pop()
        else: # after
            while len(operators) != 0:
                assert operators[-1].get() != "("

                output.append(operators.pop())

        return Reader(output)

    def codeize(self, tokens: Reader[Token]) -> list[str]:
        output: list[str] = []

        while not tokens.finished():
            token = tokens.read()

            match token.type:
                case "imm":
                    output.append(token.get())

                case "var":
                    output += [token.get(), "@GET"]

                case "op":
                    output.append(self.convert_op(token.get()))

        return output
