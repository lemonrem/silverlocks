import unittest
from parser import parse_rows


class ParserTests(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(parse_rows('name,note\nAlice,ok\n'), [['name', 'note'], ['Alice', 'ok']])

    def test_quoted_comma(self):
        self.assertEqual(parse_rows('Alice,"hello, world"\n'), [['Alice', 'hello, world']])

    def test_quoted_newline(self):
        self.assertEqual(parse_rows('Alice,"line one\nline two"\n'), [['Alice', 'line one\nline two']])

    def test_escaped_quote(self):
        self.assertEqual(parse_rows('Alice,"say ""hello"""\n'), [['Alice', 'say "hello"']])

    def test_empty(self):
        self.assertEqual(parse_rows(''), [])
