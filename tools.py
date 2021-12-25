from collections.abc import Sequence
from typing import Generic, TypeVar
from rich import print
import config

errors = []

def press_any_key():
    _ = input("Press any key to continue... ")

def error(msg):
    print(f"[red]<error>: {msg}")
    errors.append(msg)

    press_any_key()

def ssert(expr, msg):
    if not expr:
        error(msg)

def debug(msg):
    if config.debug:
        print(f"[yellow]\[debug]: {msg}")

        press_any_key()

T = TypeVar("T")

class Reader(Generic[T], Sequence):
    def __init__(self, elements: list[T]) -> None:
        self.elements = elements
        self.pointer = 0

        super().__init__()

    def __getitem__(self, index: int) -> T:
        return self.elements[index]

    def __len__(self) -> int:
        return len(self.elements)

    def read(self) -> T:
        self.pointer += 1
        return self.elements[self.pointer - 1]

    def peek(self) -> T:
        return self.elements[-1]

    def peek_start(self) -> T:
        return self.elements[0]

    def peek_read(self) -> T:
        return self.elements[self.pointer]

    def finished(self) -> bool:
        if self.pointer >= len(self.elements):
            return True
        return False

    def length(self) -> int:
        return len(self.elements)

    def until(self, enter: str, exit: str, keep: bool = False):
        level  = 0
        inside = False
        result: list[T] = []

        while not self.finished():
            item = self.read()

            if inside:
                if item == enter:
                    level += 1

                if item == exit and keep is False:
                    level -= 1

                if level == 0:
                    if keep is False:
                        self.decrement() # to make it so you can still read the top later
                    break

                if item == exit and keep is True:
                    level -= 1

                    if level == 0: # skip
                        result.append(item)
                        break

                result.append(item)

            if item == enter:
                level += 1
                inside = True

                if keep:
                    result.append(item)
        if level != 0: # hasn't properly exited
            error("Reader failed to find an until()")

        return result

    def decrement(self) -> None:
        self.pointer -= 1

        if self.pointer == -1:
            error("decremented pointer to -1 in a Reader()")

    def reset(self) -> None:
        self.pointer = 0
        return self

    def __repr__(self) -> str:
        representation = "[" + ", ".join([repr(x) for x in self.elements]) + "]"
        return representation

    def split(self, splitter: T) -> list[list[T]]:
        result = [[]]

        for item in self.elements:
            if item == splitter:
                result.append([])
            else:
                result[-1].append(item)

        return result

class Token(Generic[T], Sequence):
    ops = ["+", "-", "*", "/", "%", "^", "&", "|"]
    unarys = ["~-", "~+", "!"]

    @staticmethod
    def get_associativity(operator) -> str:
        return {
            "+": "both",
            "-": "left",
            "/": "left",
            "*": "both",
            "%": "left",
            "|": "both",
            "&": "both",
            "^": "both",
            "~+": "right",
            "~-": "right",
            "!": "right",
            "**": "both"
        }[operator]

    @staticmethod
    def get_precedence(operator) -> int:
        return {
            "+": 3,
            "-": 3,
            "/": 4,
            "*": 4,
            "%": 4,
            "|": 0,
            "&": 2,
            "^": 1,
            "**": 5,
            "~+": 6,
            "~-": 6,
            "!": 6
        }[operator]

    def __init__(self, kind: str, data: list[str] | str, temp_var: bool = None) -> None:
        assert kind in ["imm", "var", "func", "op", "unary", "paren", "stack", "comma"]

        self.type = kind
        if type(data) == list:
            self.data = data
        elif type(data) == str:
            self.data = [data]
        else:
            error("intialized without data")

        if kind == "op":
            self.precedence = self.get_precedence(self.get())
            self.associativity = self.get_associativity(self.get())

        self.temp_var = temp_var
        super().__init__()

    def get(self) -> T:
        return self.data[0]

    def __getitem__(self, index: int) -> T:
        return self.data[index]

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"{self.type}: {' '.join(self.data)}"
