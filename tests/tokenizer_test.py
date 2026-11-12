import unittest

from search.tokenizer import tokenize


class TestTokenize(unittest.TestCase):
    def test_lowercases_text(self):
        self.assertEqual(
            tokenize("PYTHON SEARCH ENGINE"),
            ["python", "search", "engine"]
        )


    def test_removes_punctuation(self):
        self.assertEqual(
            tokenize("hello, world! python."),
            ["hello", "world", "python"]
        )


    def test_removes_stopwords(self):
        self.assertEqual(
            tokenize("the python is great"),
            ["python", "great"]
        )


    def test_removes_single_character_tokens(self):
        self.assertEqual(
            tokenize("I a x developer"),
            ["developer"]
        )


    def test_empty_string(self):
        self.assertEqual(tokenize(""), [])


    def test_only_stopwords(self):
        self.assertEqual(tokenize("the and is a"), [])


    def test_preserves_numbers(self):
        self.assertEqual(
            tokenize("python 123 version 3"),
            ["python", "123", "version"]
        )


    def test_preserves_repeated_tokens(self):
        self.assertEqual(
            tokenize("python python search"),
            ["python", "python", "search"]
        )


if __name__ == "__main__":
    unittest.main()
