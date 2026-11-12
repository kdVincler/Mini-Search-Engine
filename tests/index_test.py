import json
import tempfile
import unittest
from pathlib import Path

from search.index import InvertedIndex, Posting


class TestInvertedIndex(unittest.TestCase):
    def setUp(self):
        self.index = InvertedIndex()


    def test_new_index_is_empty(self):
        self.assertEqual(self.index.doc_count, 0)
        self.assertEqual(dict(self.index.postings), {})
        self.assertEqual(self.index.doc_lengths, {})


    def test_add_document_updates_document_count_and_length(self):
        self.index.add_document("doc1", "python python programming")

        self.assertEqual(self.index.doc_count, 1)
        self.assertEqual(self.index.doc_lengths["doc1"], 3)


    def test_add_document_records_term_frequencies(self):
        self.index.add_document("doc1", "python python programming")

        self.assertEqual(
            self.index.postings["python"],
            [Posting("doc1", 2)]
        )
        self.assertEqual(
            self.index.postings["programming"],
            [Posting("doc1", 1)]
        )


    def test_add_document_uses_tokenizer_rules(self):
        self.index.add_document("doc1", "The PYTHON, and search!")

        self.assertEqual(self.index.doc_lengths["doc1"], 2)
        self.assertIn("python", self.index.postings)
        self.assertIn("search", self.index.postings)
        self.assertNotIn("the", self.index.postings)
        self.assertNotIn("and", self.index.postings)


    def test_empty_document_is_counted_with_zero_length(self):
        self.index.add_document("empty", "")

        self.assertEqual(self.index.doc_count, 1)
        self.assertEqual(self.index.doc_lengths["empty"], 0)
        self.assertEqual(dict(self.index.postings), {})


    def test_same_term_can_have_postings_for_multiple_documents(self):
        self.index.add_document("doc1", "python python")
        self.index.add_document("doc2", "python")

        self.assertEqual(
            self.index.postings["python"],
            [Posting("doc1", 2), Posting("doc2", 1)]
        )


    def test_save_writes_json(self):
        self.index.add_document("doc1", "python programming")

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "index.json"
            self.index.save(path)

            payload = json.loads(path.read_text(encoding="utf-8"))

            self.assertIn("postings", payload)
            self.assertIn("doc_lengths", payload)
            self.assertEqual(payload["doc_lengths"], {"doc1": 2})


    def test_save_and_load_round_trip(self):
        self.index.add_document("doc1", "python python programming")
        self.index.add_document("doc2", "search engine")

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "index.json"
            self.index.save(path)
            loaded = InvertedIndex.load(path)

        self.assertEqual(loaded.doc_count, self.index.doc_count)
        self.assertEqual(loaded.doc_lengths, self.index.doc_lengths)
        self.assertEqual(
            dict(loaded.postings),
            dict(self.index.postings)
        )


    def test_load_reconstructs_posting_objects(self):
        self.index.add_document("doc1", "python")

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "index.json"
            self.index.save(path)
            loaded = InvertedIndex.load(path)

        self.assertIsInstance(loaded.postings["python"][0], Posting)


if __name__ == "__main__":
    unittest.main()
