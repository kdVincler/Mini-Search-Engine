import tempfile
import unittest
from argparse import ArgumentTypeError
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import cli


class TestCLIValidators(unittest.TestCase):
    def test_valid_corpus_accepts_directory_containing_txt_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus = Path(temp_dir)
            (corpus / "doc.txt").write_text("hello", encoding="utf-8")

            self.assertEqual(cli.valid_corpus(str(corpus)), corpus)


    def test_valid_corpus_rejects_missing_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing"

            with self.assertRaises(ArgumentTypeError):
                cli.valid_corpus(str(missing))


    def test_valid_corpus_rejects_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "doc.txt"
            file_path.write_text("hello", encoding="utf-8")

            with self.assertRaises(ArgumentTypeError):
                cli.valid_corpus(str(file_path))


    def test_valid_corpus_rejects_directory_without_txt_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ArgumentTypeError):
                cli.valid_corpus(temp_dir)


    def test_valid_output_accepts_nonexistent_file_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "index.json"

            self.assertEqual(cli.valid_output(str(path)), path)


    def test_valid_output_rejects_non_json_file_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "index.txt"

            with self.assertRaises(ArgumentTypeError):
                cli.valid_output(str(path))


    def test_valid_output_rejects_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ArgumentTypeError):
                cli.valid_output(temp_dir)


    def test_valid_index_accepts_existing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "index.json"
            path.write_text("{}", encoding="utf-8")

            self.assertEqual(cli.valid_index(str(path)), path)


    def test_valid_index_rejects_existing_non_json_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "index.txt"
            path.write_text("{}", encoding="utf-8")

            with self.assertRaises(ArgumentTypeError):
                cli.valid_index(str(path))


    def test_valid_index_rejects_missing_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "missing.json"

            with self.assertRaises(ArgumentTypeError):
                cli.valid_index(str(path))


    def test_valid_index_rejects_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ArgumentTypeError):
                cli.valid_index(temp_dir)


    def test_positive_int_accepts_positive_integer(self):
        self.assertEqual(cli.positive_int("12"), 12)


    def test_positive_int_rejects_zero_and_negative(self):
        for value in ("0", "-2"):
            with self.subTest(value=value):
                with self.assertRaises(ArgumentTypeError):
                    cli.positive_int(value)


    def test_positive_int_rejects_non_integer(self):
        with self.assertRaises(ArgumentTypeError):
            cli.positive_int("abc")


    def test_valid_query_preserves_nonblank_query(self):
        self.assertEqual(cli.valid_query("python search"), "python search")


    def test_valid_query_rejects_whitespace(self):
        with self.assertRaises(ArgumentTypeError):
            cli.valid_query("   ")



class TestCLICommands(unittest.TestCase):
    def test_build_command_creates_index_and_reports_document_count(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            corpus = root / "corpus"
            output = root / "data" / "index.json"

            corpus.mkdir()
            (corpus / "doc1.txt").write_text(
                "python programming",
                encoding="utf-8"
            )

            captured = StringIO()

            with patch("sys.argv", [
                "cli.py", "build", str(corpus), str(output)
            ]):
                with redirect_stdout(captured):
                    cli.main()

            self.assertTrue(output.is_file())
            self.assertIn("indexed 1 documents", captured.getvalue())


    def test_query_command_prints_matching_document(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            corpus = root / "corpus"
            index_path = root / "index.json"

            corpus.mkdir()
            (corpus / "doc1.txt").write_text(
                "python programming",
                encoding="utf-8"
            )

            with patch("sys.argv", [
                "cli.py", "build", str(corpus), str(index_path)
            ]):
                cli.main()

            captured = StringIO()

            with patch("sys.argv", [
                "cli.py", "query", str(index_path), "python"
            ]):
                with redirect_stdout(captured):
                    cli.main()

            self.assertIn("doc1", captured.getvalue())


    def test_query_command_reports_no_results(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            corpus = root / "corpus"
            index_path = root / "index.json"

            corpus.mkdir()
            (corpus / "doc1.txt").write_text(
                "python programming",
                encoding="utf-8"
            )

            with patch("sys.argv", [
                "cli.py", "build", str(corpus), str(index_path)
            ]):
                cli.main()

            captured = StringIO()

            with patch("sys.argv", [
                "cli.py", "query", str(index_path), "fortran"
            ]):
                with redirect_stdout(captured):
                    cli.main()

            self.assertIn("No results found", captured.getvalue())


    def test_query_command_respects_k_argument(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            corpus = root / "corpus"
            index_path = root / "index.json"

            corpus.mkdir()
            (corpus / "a.txt").write_text("python", encoding="utf-8")
            (corpus / "b.txt").write_text("python", encoding="utf-8")

            with patch("sys.argv", [
                "cli.py", "build", str(corpus), str(index_path)
            ]):
                cli.main()

            captured = StringIO()

            with patch("sys.argv", [
                "cli.py", "query", str(index_path), "python", "--k", "1"
            ]):
                with redirect_stdout(captured):
                    cli.main()

            result_lines = [
                line for line in captured.getvalue().splitlines()
                if line.strip() and not line.startswith("indexed")
            ]

            self.assertEqual(len(result_lines), 1)


    def test_invalid_cli_arguments_exit(self):
        with patch("sys.argv", ["cli.py", "query"]):
            with self.assertRaises(SystemExit):
                cli.main()


if __name__ == "__main__":
    unittest.main()
