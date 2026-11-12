import argparse
from pathlib import Path

from search import SearchEngine, InvertedIndex

# =====================
# ARGUMENT VALIDATORS
# =====================

def valid_corpus(value: str) -> Path:
    """Ensure the corpus directory exists, is a directory and contains searchable files."""
    path = Path(value)

    if not path.exists():
        raise argparse.ArgumentTypeError(
            f"Corpus directory does not exist: {path}"
        )

    if not path.is_dir():
        raise argparse.ArgumentTypeError(
            f"Corpus path must be a directory: {path}"
        )

    if not any(path.glob("*.txt")):
        raise argparse.ArgumentTypeError(
            f"Corpus directory msut contain at least 1 .txt file to search: {path}"
        )

    return path


def valid_output(value: str) -> Path:
    """Ensure the output path points to a file, not a directory."""
    path = Path(value)

    if path.exists() and path.is_dir():
        raise argparse.ArgumentTypeError(
            f"Output path must be a file, not a directory: {path}"
        )

    if not path.exists() and path.suffix != ".json":
        raise argparse.ArgumentTypeError(
            f"Output path must be a .json file: {path}"
        )

    return path


def valid_index(value: str) -> Path:
    """Ensure the index file exists."""
    path = Path(value)

    if not path.exists():
        raise argparse.ArgumentTypeError(
            f"Index file does not exist: {path}"
        )

    if not path.is_file() or (path.is_file() and path.suffix != ".json"):
        raise argparse.ArgumentTypeError(
            f"Index path must be a .json file: {path}"
        )

    return path


def positive_int(value: str) -> int:
    """Ensure the user provides a positive integer."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Must be an integer."
        )
    if number <= 0:
        raise argparse.ArgumentTypeError(
            "Must be greater than zero."
        )
    return number


def valid_query(value: str) -> str:
    """Ensure the search query isn't empty."""
    if not value.strip():
        raise argparse.ArgumentTypeError(
            "Search query cannot be empty."
        )
    return value


# =====================
# MAIN CLI
# =====================

def main() -> None:
    # Create arg parser and set up expected commands and their arguments
    parser = argparse.ArgumentParser(
        prog="minisearch",
        description="A search engine implementation in Python",
        epilog="""
    Examples:
        python cli.py build corpus/ data/index.json
        python cli.py query data/index.json programming
        python cli.py query data/index.json "grand prix" --k 3
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter # needed so the examples show up properly in different lines
    )
    command_parser = parser.add_subparsers(
        dest="cmd", 
        required=True
    )

    # BUILD COMMAND
    build_parser = command_parser.add_parser(
        "build",
        help="Build and persist and index from the current state of the corpus directory"
    )
    build_parser.add_argument(
        "corpus",
        type=valid_corpus,
        help="Directory containing the searchable .txt documents"
    )
    build_parser.add_argument(
        "out",
        type=valid_output,
        help="Desired save location and name for the index .json file"
    )

    # QUERY COMMAND
    query_parser = command_parser.add_parser(
        "query",
        help="Execute a search for a passed query with an existing index"
    )
    query_parser.add_argument(
        "index",
        type=valid_index,
        help="Path to an existing search index .json file"
    )
    query_parser.add_argument(
        "query",
        type=valid_query,
        help="Query to seach for"
    )
    query_parser.add_argument(
        "--k",
        type=positive_int,
        default=5,
        help="Number of search results to display, defaults to 5"
    )

    # parse arguments and execute the specified command (validation handled by parser through the custom types above)
    args = parser.parse_args()
    if args.cmd == "build":
        engine = SearchEngine.from_corpus(args.corpus)
        args.out.parent.mkdir(parents=True, exist_ok=True) # ensures the output file's parent exist, creates them if not
        engine.index.save(args.out)
        print(f"indexed {engine.index.doc_count} documents")
    elif args.cmd == "query":
        engine = SearchEngine(InvertedIndex.load(args.index))
        results = engine.search(args.query, k=args.k)
        if not results:
            print("No results found for this query.")
        else:
            for doc_id, score in results:
                print(f"{score:5.4f}  {doc_id}") # score formating: float of total 5 digits, 4 after the decimal


if __name__ == "__main__":
    main()
