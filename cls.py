from tools import *
from parse import ParserToken

class Var:
    def __init__(self, name: str, type: str, width: int):
        self.name     = name
        self.type     = type
        self.width    = width

class Func:
    def __init__(self, name: str, func_type: str, args: list[ParserToken], code: ParserToken, ret_type):
        self.name = name
        self.func_type = func_type
        self.args = args
        self.code = code
        self.ret_type = ret_type
