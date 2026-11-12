from collections import defaultdict
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path

from .tokenizer import tokenize


@dataclass
class Posting:
    """Small dataclass to represent each found posting of a term"""
    doc_id: str
    tf: int


@dataclass
class InvertedIndex:
    """
        Load bearing data structure of the project.

        Instead of storing the list of words (terms) in a document,
        it stores its inverse, meaning for each term it stores the list
        of documents that contain said term (a.k.a. the term's postings),
        plus the term's frequency in each document (which is needed for scoring).
    """
    # word/term/token -> list of documents + term frequency
    postings: dict[str, list[Posting]] = field(
        default_factory=lambda: defaultdict(list)
    )
    # document -> count of words/terms/tokens found after tokenizatin
    doc_lengths: dict[str, int] = field(default_factory=dict)

    @property
    def doc_count(self) -> int:
        """
            Number of documents the inverted index is built on.
            This property is reliant on doc_lengths.
        """
        return len(self.doc_lengths)


    def add_document(self, doc_id: str, text: str) -> None:
        """Add all tokens/words/terms found in a document to our index"""
        tokens = tokenize(text)
        self.doc_lengths[doc_id] = len(tokens)
        frequencies: dict[str, int] = defaultdict(int)
        # find term frequencies for each term
        for t in tokens:
            frequencies[t] += 1
        # add each term to the index with their 
        for term, tf in frequencies.items():
            self.postings[term].append(Posting(doc_id=doc_id, tf=tf))


    def save(self, path: Path) -> None:
        """Save the index into a json file for persistance"""
        path.write_text(json.dumps(
            {
                "postings": {
                    term: [asdict(p) for p in plist]
                    for term, plist in self.postings.items()
                },
                "doc_lengths": self.doc_lengths,
            }
        ))


    @classmethod
    def load(cls, path: Path) -> "InvertedIndex":
        """
            Load a previusly saved instance of the index back from a json
            file into memory as a new instance.
        """
        payload = json.loads(path.read_text())
        index = cls()
        index.doc_lengths = payload["doc_lengths"]
        for term, plist in payload["postings"].items():
            index.postings[term] = [Posting(**p) for p in plist]
        return index
