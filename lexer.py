from tools import *

class Lexer:
    def __init__(self, separators: list[str], joiner: str = ";", strings: list[str] = ['"', "'"], comments: bool = True, comment_tokens: list[str] = ["#", "//"], multi_comment_tokens: list[list[str]] = [["/*", "*/"], ["///", "///"], ['"""', '"""']]):
        self.separators = separators
        self.joiner = joiner
        self.strings = strings

        self.comments = comments
        self.comment_tokens = comment_tokens
        self.multi_comment_tokens = multi_comment_tokens

    def remove_comments(self, raw: list[str]) -> list[str]:
        for i, line in enumerate(raw):
            raw[i] = line.replace("\n", "")

            for comment_token in self.comment_tokens:
                if line.count(comment_token) >= 1:
                    raw[i] = line[:line.index(comment_token)] # remove comment

        return raw

    def multi_remove_comments(self, tokens: Reader[str]) -> Reader[str]:
        result: list[str] = []

        while not tokens.finished():
            token = tokens.read()

            commented = False

            for multi_comment_token in self.multi_comment_tokens:
                if token == multi_comment_token[0]:
                    tokens.until(multi_comment_token[0], multi_comment_token[1], True)
                    commented = True
            else:
                if not commented:
                    result.append(token)

        return Reader(result)

    def lex(self, raw: list[str]) -> Reader[str]: # TODO replace unary
        def is_something(x: str):
            return (token.replace(" ", "").replace(self.joiner, "") != "")

        if self.comments:
            code = self.remove_comments(raw)
        else:
            code = raw

        stream = Reader("".join(code))
        tokens: list[str] = []
        token  = ""

        while not stream.finished():
            char = stream.read()

            if char in self.strings: # handle strings
                if is_something(token):
                    tokens.append(token)
                token = ""

                tokens.append("".join(stream.until(char, char, True)))
            elif char in self.separators: # if not string, handle separators
                if is_something(token):
                    tokens.append(token)
                    token = ""

                if char != " ":
                    tokens.append(char)

            elif char != " ": # else, continue constructing token
                token += char

                if token in self.separators: # token is fully found
                    tokens.append(token)
                    token = ""

        tokens.append(token)

        # tokens is now constructed

        if self.comments: # remove multiline comments
            result = self.multi_remove_comments(Reader(tokens))
        else:
            result = Reader(tokens)

        return result
                