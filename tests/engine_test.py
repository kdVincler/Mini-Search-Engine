import tempfile
import unittest
from pathlib import Path

from search.engine import SearchEngine
from search.index import InvertedIndex


class TestSearchEngineFromCorpus(unittest.TestCase):
    def test_builds_index_from_txt_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus = Path(temp_dir)

            (corpus / "first.txt").write_text(
                "python programming",
                encoding="utf-8"
            )
            (corpus / "second.txt").write_text(
                "search engine",
                encoding="utf-8"
            )
            (corpus / "ignored.md").write_text(
                "not indexed",
                encoding="utf-8"
            )

            engine = SearchEngine.from_corpus(corpus)

        self.assertEqual(engine.index.doc_count, 2)
        self.assertEqual(
            set(engine.index.doc_lengths),
            {"first", "second"}
        )
        self.assertNotIn("ignored", engine.index.doc_lengths)


    def test_reads_files_in_sorted_filename_order(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus = Path(temp_dir)

            (corpus / "z.txt").write_text("shared", encoding="utf-8")
            (corpus / "a.txt").write_text("shared", encoding="utf-8")

            engine = SearchEngine.from_corpus(corpus)

        self.assertEqual(
            [posting.doc_id for posting in engine.index.postings["shared"]],
            ["a", "z"]
        )


    def test_empty_corpus_creates_empty_index(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = SearchEngine.from_corpus(Path(temp_dir))

        self.assertEqual(engine.index.doc_count, 0)



class TestSearchEngineSearch(unittest.TestCase):
    def setUp(self):
        index = InvertedIndex()
        index.add_document("doc1", "python programming")
        index.add_document("doc2", "python search engine")
        index.add_document("doc3", "javascript programming")

        self.engine = SearchEngine(index)


    def test_search_returns_only_matching_documents(self):
        results = self.engine.search("python")

        self.assertEqual(
            {doc_id for doc_id, _score in results},
            {"doc1", "doc2"}
        )


    def test_search_for_unknown_term_returns_empty_list(self):
        self.assertEqual(self.engine.search("fortran"), [])


    def test_search_with_stopword_query_returns_empty_list(self):
        self.assertEqual(self.engine.search("the and is"), [])


    def test_k_limits_number_of_results(self):
        results = self.engine.search("programming python", k=1)

        self.assertEqual(len(results), 1)


    def test_k_larger_than_results_returns_all_matches(self):
        results = self.engine.search("python", k=10)

        self.assertEqual(len(results), 2)


    def test_results_are_ordered_by_descending_score(self):
        results = self.engine.search("python programming")
        scores = [score for _doc_id, score in results]

        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
