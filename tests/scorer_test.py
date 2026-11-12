import math
import unittest

from search.index import InvertedIndex
from search.scorer import score_query


class TestScoreQuery(unittest.TestCase):
    def setUp(self):
        self.index = InvertedIndex()
        self.index.add_document("doc1", "python python python programming")
        self.index.add_document("doc2", "python programming")
        self.index.add_document("doc3", "programming language")


    def test_empty_query_returns_empty_dict(self):
        self.assertEqual(score_query([], self.index), {})


    def test_unknown_term_returns_empty_dict(self):
        self.assertEqual(score_query(["javascript"], self.index), {})


    def test_known_term_only_scores_documents_containing_it(self):
        scores = score_query(["python"], self.index)

        self.assertEqual(set(scores), {"doc1", "doc2"})
        self.assertGreater(scores["doc1"], 0)
        self.assertGreater(scores["doc2"], 0)


    def test_repeated_query_terms_do_not_change_score(self):
        once = score_query(["python"], self.index)
        repeated = score_query(["python", "python"], self.index)

        self.assertEqual(once, repeated)


    def test_multiple_query_terms_accumulate_scores(self):
        python_only = score_query(["python"], self.index)
        combined = score_query(["python", "programming"], self.index)

        self.assertGreater(
            combined["doc1"],
            python_only["doc1"]
        )
        self.assertIn("doc3", combined)


    def test_score_matches_sublinear_tf_idf_and_length_normalisation(self):
        # N=3, df(python)=2, tf(doc1)=3, document length=4.
        expected = (
            math.log((1 + 3) / (1 + 2)) + 1.0
        ) * ((1.0 + math.log(3)) / math.sqrt(4))

        scores = score_query(["python"], self.index)

        self.assertAlmostEqual(
            scores["doc1"],
            expected,
            places=12
        )


    def test_common_term_has_lower_idf_than_rare_term(self):
        programming = score_query(["programming"], self.index)
        language = score_query(["language"], self.index)

        # Both postings have tf=1 and their documents have length=2.
        self.assertGreater(
            language["doc3"],
            programming["doc2"]
        )


if __name__ == "__main__":
    unittest.main()
