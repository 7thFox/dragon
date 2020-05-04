from io import TextIOWrapper
from enum import Enum

# Buffer class for lexing based on the disucssions within CH 3

# You could have up to N*2 in size for tokens, but it's only garunteed
# for N (we could do something to allow N+1, but really they shouldn't
# even approch the buffer size)
_BUFFER_SIZE = 4096
EOF = "<EOF>"


class Token():
    def __init__(self, tag, value, text, span):
        assert isinstance(tag, Enum)
        self.tag = tag
        self.value = value
        self.span = span
        self.text = text

    def __str__(self):
        end = ">"
        if self.value != None:
            end = ", " + str(self.value) + end
        return "<" + self.tag.name + end

    def __eq__(self, other):
        return isinstance(other, Token) and \
            self.tag == other.tag and \
            self.value == other.value and \
            self.span == other.span and \
            self.text == other.text


class Span:
    def __init__(self, char_start, char_end, line_start, col_start):
        self.line_start = line_start
        self.col_start = col_start
        self.char_start = char_start
        self.char_end = char_end

    def __eq__(self, other):
        return isinstance(other, Span) and \
            self.line_start == other.line_start and \
            self.col_start == other.col_start and \
            self.char_start == other.char_start and \
            self.char_end == other.char_end

    def __str__(self):
        return "["+str(self.char_start)+", "+str(self.char_end)+"]"

    def location(self):
        return "("+str(self.line_start)+", "+str(self.col_start)+")"


class LexingBuffer:
    class _State:
        def __init__(self, lines=0, cols=0, chars=0, buffer_number=0, pos=0):
            self.lines = lines
            self.cols = cols
            self.chars = chars
            self.buffer_number = buffer_number
            self.pos = pos

        def move_next(self, is_newline):
            buffer_number = self.buffer_number
            pos = self.pos + 1
            if self.pos == _BUFFER_SIZE - 1:  # end of current buffer
                buffer_number = (buffer_number + 1) % 2
                pos = 0
            if is_newline:
                return LexingBuffer._State(self.lines + 1, 0, self.chars + 1, buffer_number, pos)
            return LexingBuffer._State(self.lines, self.cols + 1, self.chars + 1, buffer_number, pos)

    def __init__(self, text_buffer):
        assert isinstance(
            text_buffer, TextIOWrapper), "Buffer not of TextIOWrapper"
        self._text_buffer = text_buffer
        self.is_EOF = False
        self._states = []
        self._next_state = LexingBuffer._State()
        self._buffers = [self._read_buffer(), None]

    def _read_buffer(self):
        assert not self.is_EOF, "Buffer read after EOF"
        ret = [c for c in self._text_buffer.read(_BUFFER_SIZE)]
        if len(ret) < _BUFFER_SIZE:
            ret.append(EOF)
            self.is_EOF = True
        return ret

    def read(self):

        if self._buffers[self._next_state.buffer_number] == None:
            self._buffers[self._next_state.buffer_number] = self._read_buffer()

        val = self._buffers[self._next_state.buffer_number][self._next_state.pos]

        self._states.append(self._next_state)
        s = self._next_state.move_next(val == '\n')
        if s.buffer_number != self._next_state.buffer_number:  # next read will be on the other buffer
            assert self._buffers[
                s.buffer_number] == None, "Attempt to read over buffer (token too long)"
        self._next_state = s
        return val

    def retract(self, n=1):
        if n > 0:
            assert len(
                self._states) > 0, "Retract attempted with no past states"
            self._next_state = self._states.pop()
            self.retract(n - 1)

    def emit(self, tag, value_or_func):
        text = ""
        start = self._states[0]
        end = self._states[-1]

        if start.buffer_number == end.buffer_number:
            text = ''.join(self._buffers[start.buffer_number
                                         ][start.pos:end.pos+1])
        else:
            text = ''.join(self._buffers[start.buffer_number][start.pos:] +
                           self._buffers[end.buffer_number][:end.pos + 1])

        if self._next_state.buffer_number != start.buffer_number:  # old buffer won't be needed any longer
            self._buffers[start.buffer_number] = None

        self._states = []
        span = Span(start.chars, end.chars+1, start.lines, start.cols)

        if callable(value_or_func):
            return Token(tag, value_or_func(text), text, span)
        return Token(tag, value_or_func, text, span)
