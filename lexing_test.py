
import unittest
from enum import Enum
from lexing import LexingBuffer, Token, Span, EOF, _BUFFER_SIZE
from io import TextIOWrapper, BytesIO


class TestTags(Enum):
    Test = 0


class LexingBufferTests(unittest.TestCase):
    def test_basic(self):
        length = 1000
        l = LexingBuffer(TextIOWrapper(BytesIO(("D" * length).encode())))

        for n in range(0, length + 1):
            if n == length:
                self.assertEqual(l.read(), EOF)
            else:
                self.assertEqual(l.read(), "D")
                emitted = l.emit(TestTags.Test, None)
                self.assertEqual(emitted, Token(
                    TestTags.Test, None, "D", Span(n, n + 1, 0, n)))

    def test_linebreaks(self):
        length = 1000
        l = LexingBuffer(TextIOWrapper(BytesIO(("DDDD\n" * length).encode())))

        for n in range(0, length*5 + 1):
            if n == length*5:
                self.assertEqual(l.read(), EOF)
            elif n % 5 == 4:
                self.assertEqual(l.read(), "\n")
                emitted = l.emit(TestTags.Test, None)
                self.assertEqual(emitted, Token(
                    TestTags.Test, None, "\n", Span(n, n + 1, n // 5, n % 5)))
            else:
                self.assertEqual(l.read(), "D")
                emitted = l.emit(TestTags.Test, None)
                self.assertEqual(emitted, Token(
                    TestTags.Test, None, "D", Span(n, n + 1, n // 5, n % 5)))

    def test_value_func(self):
        length = 1000
        l = LexingBuffer(TextIOWrapper(BytesIO(("1" * length).encode())))

        for n in range(0, length + 1):
            if n == length:
                self.assertEqual(l.read(), EOF)
            else:
                self.assertEqual(l.read(), "1")
                emitted = l.emit(TestTags.Test, lambda x: int(x))
                self.assertEqual(emitted, Token(
                    TestTags.Test, 1, "1", Span(n, n + 1, 0, n)))
                self.assertIsInstance(emitted.value, int)

    def test_longer_token(self):
        length = 333*3
        l = LexingBuffer(TextIOWrapper(BytesIO(("D" * length).encode())))

        for n in range(0, length + 1):
            if n == length:
                self.assertEqual(l.read(), EOF)
            else:
                self.assertEqual(l.read(), "D")
                if n % 3 == 2:
                    emitted = l.emit(TestTags.Test, None)
                    self.assertEqual(emitted, Token(
                        TestTags.Test, None, "DDD", Span(n - 2, n + 1, 0, n - 2)))

    def test_long_token_throws(self):
        length = 10000
        l = LexingBuffer(TextIOWrapper(BytesIO(("D" * length).encode())))
        for _ in range(0, _BUFFER_SIZE - 1):  # consume all but 1 char of buffer
            l.read()
        l.emit(TestTags.Test, None)
        for _ in range(0, _BUFFER_SIZE):  # should still consume safely up to BUFFER_SIZE
            l.read()

        def unsafe_reads():
            l.read()  # N + 1: could technically read this if we wanted, but that would add a lot of work/complexity to the buffer
            l.read()  # N + 2: will be unable to safely read next buffer without overriding a buffer that's still in use

        self.assertRaises(Exception, unsafe_reads)

    def test_retract(self):
        length = 1000
        l = LexingBuffer(TextIOWrapper(BytesIO(("ABCDE" * length).encode())))

        for _ in range(0, length):
            # read 5, retract 4, emit
            self.assertEqual(l.read(), "A")
            self.assertEqual(l.read(), "B")
            self.assertEqual(l.read(), "C")
            self.assertEqual(l.read(), "D")
            self.assertEqual(l.read(), "E")
            l.retract(4)
            self.assertEqual(l.emit(TestTags.Test, None).text, "A")

            # re-read remaining 4, retract 1, emit
            self.assertEqual(l.read(), "B")
            self.assertEqual(l.read(), "C")
            self.assertEqual(l.read(), "D")
            self.assertEqual(l.read(), "E")
            l.retract()
            self.assertEqual(l.emit(TestTags.Test, None).text, "BCD")

            # read final, emit
            self.assertEqual(l.read(), "E")
            self.assertEqual(l.emit(TestTags.Test, None).text, "E")

        self.assertEqual(l.read(), EOF)


if __name__ == '__main__':
    unittest.main()
