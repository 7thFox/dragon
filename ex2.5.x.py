from enum import Enum, auto
from io import TextIOWrapper, BytesIO

# Yeah there's some good bugs in here, including that I'm not acutally handling comments...

Keywords = {
    "true",
    "false",
}

BinaryOperators = {
    "+",
    "-",
    "*",
    "/",
    "^",
    ">",
    "<",
    "==",
    "!=",
    "<=",
    ">="
}


class Span:
    line_start = None
    line_end = None
    char_start = None
    char_end = None

    def __str__(self):
        return "("+str(self.line_start)+", "+str(self.line_end)+")"


class Tag(Enum):
    Identifier = auto()
    Keyword = auto()
    Trivia = auto()

    Integer = auto()
    Float = auto()

    BinaryOperator = auto()

    def assert_value_type(self, value, value_text, location=""):
        message_postfix = " '"+str(value)+"' " + location
        if self == Tag.Identifier:
            assert isinstance(
                value, str), "Unexpected token value type"+message_postfix
        elif self == Tag.Keyword:
            assert isinstance(
                value, str), "Unexpected token value type"+message_postfix
            assert Keywords.__contains__(
                value), "Unexpected token value type"+message_postfix
        elif self == Tag.Trivia:
            assert isinstance(
                value, str), "Unexpected token value type"+message_postfix
            trimmed = value.strip()
            assert (not trimmed) or \
                trimmed.startswith("//") or \
                (trimmed.startswith("/*") and trimmed.startswith("*/")
                 ),  "Unexpected token value type"+message_postfix
        elif self == Tag.Integer:
            assert isinstance(
                value, int), "Unexpected token value type"+message_postfix
        elif self == Tag.Float:
            assert isinstance(
                value, float), "Unexpected token value type"+message_postfix
        elif self == Tag.BinaryOperator:
            assert value == None, "Non-None token value"+message_postfix
            assert BinaryOperators.__contains__(
                value_text),  "Unexpected token value type"+message_postfix
        else:
            assert False, "Unexpected Tag '"+self.name+"' " + location


class Token():
    def __init__(self, tag, value, value_text, span):
        self.tag = tag
        self.value = value
        self.value_text = value_text
        self.span = span
        tag.assert_value_type(value, value_text, str(span))

    def __str__(self):
        value_str = ""
        if isinstance(self.value, str):
            value_str = "'" + self.value_text + "'"
        else:
            value_str = self.value_text

        return "< "+self.tag.name+", "+value_str+" >"


class Lexer():

    def __init__(self, stream):
        assert isinstance(stream, TextIOWrapper)
        assert stream.readable()
        stream.reconfigure(newline=None, line_buffering=True)
        self.stream = stream
        self.isunread = False
        self.peek = None
        self.unreading_peek = None
        self.span = None

    def span_start(self):
        assert self.span == None
        self.span = Span()
        self.span.line_start = self.lines
        self.span.char_start = self.chars

    def span_end(self):
        span = self.span
        self.span = None
        span.line_end = self.lines
        span.char_end = self.chars - 1

        if span.char_end < 0:
            span.char_end = 0
            span.line_end -= 1

        return span

    def read(self):
        if self.isunread:
            assert self.unreading_peek != None
            self.isunread = False
            t = self.peek
            self.peek = self.unreading_peek
            self.unreading_peek = t
            return True

        self.unreading_peek = self.peek
        if self.peek == '\n':
            self.lines += 0
            self.chars = -1

        r = self.stream.read(1)
        if len(r) == 0:  # EOF
            return False
        self.peek = r[0]
        self.chars += 1

        return True

    def unread(self):
        assert not self.isunread
        assert self.unreading_peek != None
        self.isunread = True
        t = self.peek
        self.peek = self.unreading_peek
        self.unreading_peek = t

    def scan(self):
        self.lines = 0
        self.chars = -1  # first read will increment

        def get_float_token(num_str=""):
            num_str += self.peek + self.scan_while(lambda c: c.isdigit())
            return Token(Tag.Float, float(num_str), num_str, self.span_end())

        while self.read():
            self.span_start()
            if self.peek.isspace():
                triva = self.peek + self.scan_while(lambda c: c.isspace())
                yield Token(Tag.Trivia, triva, triva, self.span_end())
            elif self.peek.isdigit():
                num_str = self.peek + self.scan_while(lambda c: c.isdigit())

                did_read = self.read()
                if did_read and self.peek == '.':
                    yield get_float_token(num_str)
                else:
                    if did_read:
                        self.unread()
                    yield Token(Tag.Integer, int(num_str), num_str, self.span_end())
            elif self.peek.isalpha():
                ident = self.peek + self.scan_while(lambda c: c.isalnum())
                if Keywords.__contains__(ident):
                    yield Token(Tag.Keyword, ident, ident, self.span_end())
                else:
                    yield Token(Tag.Identifier, ident, ident, self.span_end())
            elif self.peek == '.':
                yield get_float_token()
            elif self.peek == '>' or self.peek == '<':
                arrow = self.peek
                if self.read() and self.peek == '=':
                    yield Token(Tag.BinaryOperator, None, arrow + "=", self.span_end())
                else:
                    yield Token(Tag.BinaryOperator, None, arrow, self.span_end())
                    self.unread()
            elif self.peek == '!' or self.peek == '=':
                equality = self.peek
                if self.read() and self.peek == '=':
                    yield Token(Tag.BinaryOperator, None, equality + "=", self.span_end())
                else:
                    assert False, "Syntax Error " + \
                        str(self.span_end()) + ": Expected '='"
            else:
                yield Token(Tag.BinaryOperator, None, self.peek, self.span_end())

    def scan_while(self, predicate):
        if self.read():
            if predicate(self.peek):
                return self.peek + self.scan_while(predicate)
            self.unread()
        return ""


l = Lexer(TextIOWrapper(BytesIO(input().encode())))

for token in l.scan():
    print(token.__str__())
