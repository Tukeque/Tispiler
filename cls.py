from tools import *
import compiler as c

class Var:
    def __init__(self, name: str, type: str, width: int, compiler):
        self.name     = name
        self.type     = type
        self.width    = width
        self.compiler: c.Compiler = compiler
