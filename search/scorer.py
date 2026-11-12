import math
from collections import Counter

from .index import InvertedIndex


def score_query(
    query_tokens: list[str],
    index: InvertedIndex,
) -> dict[str, float]:
    """
        TF-IDF scorer that returns a document -> score map for a single query.

        As the name implies, in its most basic form, TF-IDF relies on 2 things:
        (Based on information researched [here](https://www.geeksforgeeks.org/machine-learning/understanding-tf-idf-term-frequency-inverse-document-frequency/))
        
        Term frequency (TF): Measures how frequently a term occurs in a document. 

        Inverse Document Frequency (IDF): Reduces the weight of common words accross multiple documents while increasing the weight of rare words

        TF-IDF is then calculated by multiplying together these 2 values.
        As inline comments shown this scorer is relying on an improved TF-IDF scorer
    """
    if not query_tokens:
        return {}

    idf: dict[str, float] = {}
    scores: dict[str, float] = Counter() # Internally use counter so missing key's just default to 0 instead of raising errors

    # total number of documents indexed
    N = index.doc_count

    # unique query tokens/terms
    uqt = set(query_tokens)

    for term in uqt:
        """
            For each term in the query tokens calculate IDF, and from each posting for each term use the stored TF,
            turn it into sublinear and lenght normalized, then accumulate the score
        """
        df = len(index.postings.get(term, []))
        # Smoothed IDF: log((1 + N) / (1 + df)) + 1
        # https://sklearn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfTransformer.html
        idf[term] = math.log((1 + N) / (1 + df)) + 1.0

        plist = index.postings.get(term)
        if not plist:
            continue
        for posting in plist:
            # Sublinear TF: 1 + log(tf) if tf > 0 else 0
            # https://sklearn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfTransformer.html
            # + handled the edgecase of tf = 0 as we cannot calculate log(0)
            tf_norm = 1.0 + math.log(posting.tf) if posting.tf > 0 else 0.0

            # Length normalization: divide by sqrt(doc_length)
            # ensures long documents can't get higher scores just because of their length
            length_norm = math.sqrt(index.doc_lengths[posting.doc_id])

            # Scores for each relevant document is calculated by taking into effect the 
            # above calculated smooth IDF and document length normalized sublinear TF
            scores[posting.doc_id] += idf[term] * (tf_norm / length_norm)

    return dict(scores) # Ensures that modules ingesting the result of this module get a standard python dict regardless of implementation here
