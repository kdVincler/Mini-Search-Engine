from pathlib import Path
import heapq

from .index import InvertedIndex
from .scorer import score_query
from .tokenizer import tokenize


class SearchEngine:
    """
        Orchestrator of the project.

        Owns and builds (from directory vie the `from_corpus()` function) the Index. 
        
        Exposes the `search()` method that actually carries out the tokenisation, scoring and returning of the result.
    """
    def __init__(self, index: InvertedIndex):
        self.index = index

    @classmethod
    def from_corpus(cls, corpus_dir: Path) -> "SearchEngine":
        """
            Build function.
            Initialises a new instance of the index, adds each document to it,
            finally returns an Engine instance with the populated Index via the constructor above.
        """
        idx = InvertedIndex()
        for path in sorted(corpus_dir.glob("*.txt")):
            idx.add_document(doc_id=path.stem, text=path.read_text(encoding="utf-8"))
        return cls(idx)

    def search(self, query: str, k: int = 5) -> list[tuple[str, float]]:
        """
            Tokenises the query, uses the scoring function to get scores for the index, then returns the top `k` results.
        """
        query_tokens = tokenize(query)
        scores = score_query(query_tokens, self.index)
        # Return the top k (default top 5) documents based on their scores
        # using heap queue's nlargest algorithm to be more efficient in the case the dataset
        # contains a lot of documents compared to a much smaller k (like is the case in most search engines).
        #
        # Basically equivalent to sorted(iterable, key=lambda kv: kv[1], reverse=True)[:k],
        # but this could be slow when corpus is large and we only want a small amount of k
        return heapq.nlargest(k, scores.items(), key=lambda kv: kv[1])
