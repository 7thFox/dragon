
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
        for n in range(0, length + 1):
            if n >= _BUFFER_SIZE*2:  # 8192, reading the next
                self.assertRaises(Exception, l.read)
            else:
                self.assertEqual(l.read(), "D")


if __name__ == '__main__':
    unittest.main()
