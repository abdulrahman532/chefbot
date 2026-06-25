"""Automated evaluation script for ChefBot.

Runs the 10 test queries and measures retrieval precision.
Requires GEMINI_API_KEY to be set for full evaluation (with answer generation).
Can run retrieval-only evaluation without an API key.
"""

import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rag.indexing import get_collection, index_documents


def evaluate_retrieval():
    """Evaluate retrieval precision on the 10 test queries."""
    # Load test queries
    queries_path = os.path.join(os.path.dirname(__file__), "test_queries.json")
    with open(queries_path, "r") as f:
        test_queries = json.load(f)

    # Ensure index exists
    try:
        collection = get_collection()
    except ValueError:
        print("Building index first...")
        collection = index_documents()

    print("=" * 70)
    print("ChefBot Retrieval Evaluation")
    print("=" * 70)
    print(f"Total test queries: {len(test_queries)}")
    print(f"Index size: {collection.count()} chunks")
    print()

    hits = 0
    total = len(test_queries)

    for tq in test_queries:
        query = tq["query"]
        expected = tq["expected_source"]

        # Basic retrieval (no API key needed)
        results = collection.query(
            query_texts=[query],
            n_results=5,
        )

        # Check if expected source is in top-5
        retrieved_sources = set()
        for meta in results["metadatas"][0]:
            retrieved_sources.add(meta.get("source", ""))

        hit = expected in retrieved_sources
        if hit:
            hits += 1

        status = "✅ HIT" if hit else "❌ MISS"
        print(f"Q{tq['id']:2d}: {status} | {query}")
        print(f"      Expected: {expected}")
        print(f"      Retrieved: {', '.join(sorted(retrieved_sources))}")
        print()

    precision = hits / total * 100
    print("=" * 70)
    print(f"Retrieval Precision (Top-5): {hits}/{total} = {precision:.0f}%")
    print("=" * 70)

    print("\nRunning full evaluation with answer generation...")
    from rag.retrieval import ask

    for tq in test_queries[:3]:  # Run first 3
        result = ask(tq["query"], collection=collection, use_hyde=True)
        print(f"\nQ: {tq['query']}")
        print(f"A: {result['answer'][:200]}...")
        print(f"Method: {result['method']}")
        print(f"Sources: {[s['title'] for s in result['sources']]}")


if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    evaluate_retrieval()
