"""RAG retrieval and generation module for ChefBot.

This module implements retrieval-augmented generation with HyDE
(Hypothetical Document Embeddings) as the advanced RAG technique.
"""

import os
from google import genai
from google.genai import types
from rag.indexing import get_collection


# ── Prompt Templates ─────────────────────────────────────────

SYSTEM_PROMPT = """You are ChefBot, a knowledgeable and friendly cooking assistant.

Your expertise covers recipes, cooking techniques, ingredient substitutions,
nutritional information, and meal planning. You answer questions based on
the recipe knowledge base provided to you as context.

Guidelines:
- Answer based on the provided context whenever possible.
- If the context contains relevant recipe information, reference specific
  recipes by name and provide accurate details (ingredients, steps, times).
- If the context does not contain enough information to fully answer the
  question, say so honestly and provide what general cooking knowledge you can.
- Be encouraging and supportive — cooking should be fun!
- When listing ingredients or steps, use clear formatting.
- Include helpful tips when relevant (e.g., "For extra flavor, try...").
"""

HYDE_PROMPT = """You are a recipe writer. Given the following cooking question,
write a short hypothetical recipe or cooking guide paragraph (100-150 words)
that would perfectly answer this question. Write it as if it were an excerpt
from a recipe document. Do NOT say "here is a hypothetical document" — just
write the content directly.

Question: {query}

Hypothetical recipe excerpt:"""

QA_PROMPT = """Based on the following recipe context, answer the user's question.

Context from recipe knowledge base:
---
{context}
---

User question: {query}

Provide a helpful, detailed answer based on the context above:"""


# ── LLM Configuration ────────────────────────────────────────

def _get_client() -> genai.Client:
    """Get a configured Gemini client.

    Returns:
        Configured genai.Client instance.

    Raises:
        EnvironmentError: If GEMINI_API_KEY is not set.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY environment variable is not set. "
            "Get a key at https://aistudio.google.com/apikey and add it "
            "to your .env file."
        )
    return genai.Client(api_key=api_key)


MODEL_NAME = "gemini-2.0-flash"


# ── Retrieval Functions ──────────────────────────────────────

def retrieve_basic(
    query: str,
    collection,
    n_results: int = 5,
) -> list[dict]:
    """Basic vector similarity search against the recipe collection.

    Args:
        query: The user's search query.
        collection: ChromaDB collection to search.
        n_results: Number of results to return.

    Returns:
        List of dicts with keys: document, metadata, distance.
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "document": doc,
            "metadata": meta,
            "distance": dist,
        })

    return chunks


def generate_hyde_document(query: str) -> str:
    """Generate a hypothetical document using HyDE technique.

    Uses the LLM to generate a hypothetical recipe excerpt that would
    answer the query. This hypothetical document is then used as the
    search query, improving retrieval by matching document-to-document
    rather than query-to-document.

    Args:
        query: The user's original question.

    Returns:
        Generated hypothetical document text.
    """
    client = _get_client()
    prompt = HYDE_PROMPT.format(query=query)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return response.text


def retrieve_hyde(
    query: str,
    collection,
    n_results: int = 5,
) -> list[dict]:
    """HyDE-enhanced retrieval.

    First generates a hypothetical document that would answer the query,
    then uses that document as the search query for better semantic matching.

    Args:
        query: The user's original question.
        collection: ChromaDB collection to search.
        n_results: Number of results to return.

    Returns:
        List of dicts with keys: document, metadata, distance.
    """
    # Step 1: Generate hypothetical document
    hyde_doc = generate_hyde_document(query)

    # Step 2: Use hypothetical document as search query
    results = collection.query(
        query_texts=[hyde_doc],
        n_results=n_results,
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "document": doc,
            "metadata": meta,
            "distance": dist,
        })

    return chunks


# ── Generation ───────────────────────────────────────────────

def generate_response(query: str, context_chunks: list[dict]) -> str:
    """Generate a response using retrieved context and the LLM.

    Args:
        query: The user's original question.
        context_chunks: List of retrieved chunk dicts with document and metadata.

    Returns:
        Generated answer string.
    """
    client = _get_client()

    # Build context string from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(context_chunks, 1):
        source = chunk["metadata"].get("title", chunk["metadata"].get("source", "unknown"))
        context_parts.append(f"[Source: {source}]\n{chunk['document']}")

    context_str = "\n\n".join(context_parts)

    prompt = QA_PROMPT.format(context=context_str, query=query)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=1024,
        ),
    )
    return response.text


# ── Main Ask Function ────────────────────────────────────────

def ask(
    query: str,
    collection=None,
    use_hyde: bool = True,
    n_results: int = 5,
) -> dict:
    """Main RAG function: retrieve relevant context and generate an answer.

    Args:
        query: The user's question about cooking/recipes.
        collection: ChromaDB collection. If None, loads from default path.
        use_hyde: Whether to use HyDE for retrieval (default True).
        n_results: Number of context chunks to retrieve.

    Returns:
        Dict with keys: query, answer, sources, method.
    """
    if collection is None:
        collection = get_collection()

    # Retrieve relevant chunks
    method = "hyde" if use_hyde else "basic"
    try:
        if use_hyde:
            chunks = retrieve_hyde(query, collection, n_results)
        else:
            chunks = retrieve_basic(query, collection, n_results)
    except Exception as e:
        # Fall back to basic retrieval if HyDE fails
        if use_hyde:
            print(f"HyDE retrieval failed ({e}), falling back to basic retrieval.")
            chunks = retrieve_basic(query, collection, n_results)
            method = "basic (fallback)"
        else:
            raise

    # Generate response
    answer = generate_response(query, chunks)

    # Collect unique sources
    sources = []
    seen = set()
    for chunk in chunks:
        title = chunk["metadata"].get("title", "")
        source_file = chunk["metadata"].get("source", "")
        key = title or source_file
        if key and key not in seen:
            seen.add(key)
            sources.append({
                "title": title,
                "file": source_file,
                "category": chunk["metadata"].get("category", ""),
            })

    return {
        "query": query,
        "answer": answer,
        "sources": sources,
        "method": method,
    }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("=" * 60)
    print("ChefBot - RAG Retrieval Test")
    print("=" * 60)

    test_query = "How do I make a creamy Italian pasta dish?"
    print(f"\nQuery: {test_query}")
    print("-" * 40)

    result = ask(test_query)

    print(f"Method: {result['method']}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nSources:")
    for src in result["sources"]:
        print(f"  - {src['title']} ({src['category']})")
