# Mini-Search-Engine

This project is an exploration of the building blocks behind text search: tokenization, indexing, relevance scoring (specifically TF-IDF), and a command-line interface. It searches local plain-text files and uses only the Python standard library.

## Usage

To execute a search query, you need to build an inverted index from the collection of files to search (a.k.a. the corpus), in this case a directory of `.txt` files.

```bash
python cli.py build corpus/ data/index.json
```

The index is saved as JSON. Its parent directory is created if it does not already exist. The command prints the number of documents indexed.

To execute a search on the saved index:

```bash
python cli.py query data/index.json programming
```

By default, the search prints up to five results. Use `--k` to choose a different positive number of results:

```bash
python cli.py query data/index.json "grand prix" --k 3
```

Each result shows its relevance score followed by the document ID, which is the filename without the `.txt` extension. The CLI prints matching document IDs and scores, not document text or snippets.

For command and argument details:

```bash
python cli.py --help
python cli.py build --help
python cli.py query --help
```

### Input and search behavior

- The corpus must be an existing directory containing at least one `.txt` file directly inside it; files in subdirectories are not included.
- All files handled by the project (be it corpus documents or saved indexes) are read (and written) as UTF-8.
- Queries must contain non-whitespace text.
- The index path must point to an existing `.json` file.
- Text is lowercased and split into runs of ASCII letters and digits. Configured stopwords and one-character tokens are discarded.
- Multiword queries score documents for their distinct terms; they are not exact-phrase searches. Repeating a query term does not increase its weight.
- Terms that are unknown or removed during tokenization produce no results. 
- `--k` (when specified) must be greater than zero.

## How ranking works

The engine stores an inverted index, meaning it maps each term to the documents containing it and its frequency in each document. For a query, it combines smoothed inverse document frequency with sublinear term frequency with document-length normalization, then returns the highest-scoring matches.

## Testing

The project has a test suite containing 54 test cases across 5 files, testing both edge cases and expected behaviours. 

Run the test suite with:

```bash
python run_tests.py
```

## Project structure

- `cli.py` — command-line interface for interacting with the project. It handles both building indexes and querying them.
- `search/` — search engine implementation:
  - `tokenizer.py` — lowercases and filters text into searchable tokens.
  - `index.py` — stores, saves, and loads the inverted index.
  - `scorer.py` — calculates TF-IDF relevance scores.
  - `engine.py` — builds and owns an index from a corpus and returns ranked results.
- `corpus/` — sample `.txt` documents gathered from Wikipedia with the help of [Wikipedia Text Extractor](https://wikitext.eluni.co).
- `data/` — serialized index data.
- `tests/` — unit tests for the CLI and search modules.
- `run_tests.py` — helper that discovers and runs the test suite.
