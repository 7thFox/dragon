from io import TextIOWrapper
from enum import Enum

# Buffer class for lexing based on the disucssions within CH 3

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

    def __init__(self, text_buffer):
        assert isinstance(text_buffer, TextIOWrapper)
        self._text_buffer = text_buffer
        self.is_EOF = False
        self._lines = 0
        self._cols = 0
        self._chars = 0
        self._start = (0, 0)
        self._forward = (0, -1)
        self._line_col_char_start = (0, 0, 0)
        self._forward_behind_start = True

        self._buffers = [self._read_buffer(), None]

    def _read_buffer(self):
        assert not self.is_EOF
        ret = [c for c in self._text_buffer.read(_BUFFER_SIZE)]
        if len(ret) < _BUFFER_SIZE:
            ret.append(EOF)
            self.is_EOF = True
        return ret

    def _get_next_forward(self):
        if self._forward[1] == _BUFFER_SIZE - 1:  # End of current buffer
            # Ensure we're not reading over the buffer of Start
            if not self._forward_behind_start and self._forward[0] != self._start[0]:
                raise Exception("lexeme extending past 2x buffer")
            other_buffer_index = (self._forward[0] + 1) % 2
            if self._buffers[other_buffer_index] == None:  # not peeked and already read
                self._buffers[other_buffer_index] = self._read_buffer()
            self._forward_behind_start = False
            return (other_buffer_index, 0)
        self._forward_behind_start = False
        return (self._forward[0], self._forward[1]+1)

    def peek(self):
        new_forward = self._get_next_forward()
        return self._buffers[new_forward[0]][new_forward[1]]

    def read(self):
        self._forward = self._get_next_forward()
        val = self._buffers[self._forward[0]][self._forward[1]]

        self._chars += 1
        if val == '\n':
            self._lines += 1
            self._cols = 0
        else:
            self._cols += 1
        return val

    def emit(self, tag, value_or_func):
        text = ""

        if self._start[0] == self._forward[0]:
            text = ''.join(self._buffers[self._start[0]
                                         ][self._start[1]:self._forward[1]+1])
        else:
            text = ''.join(self._buffers[self._start[0]][self._start[1]:] +
                           self._buffers[self._forward[0]][:self._forward[1]+1])

        # make sure the next _start isn't in the next buffer
        # most cases would be handled by the else above, but there's
        # the edgecase of the next _start being the beginning of the
        # next buffer
        # forward is now 1 behind the start because it's not been read yet
        # on the next read() call, it will be the same as start
        next_start = self._get_next_forward()
        if next_start[0] != self._start[0]:
            self._buffers[self._start[0]] = None
        self._start = next_start
        self._forward_behind_start = True

        span = Span(self._line_col_char_start[2],
                    self._line_col_char_start[2] + len(text),
                    self._line_col_char_start[0],
                    self._line_col_char_start[1])
        self._line_col_char_start = (self._lines, self._cols, self._chars)

        if callable(value_or_func):
            return Token(tag, value_or_func(text), text, span)
        return Token(tag, value_or_func, text, span)
