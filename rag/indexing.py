"""Document processing and ChromaDB indexing for ChefBot.

This module handles loading recipe markdown files, chunking them,
and indexing them into a ChromaDB vector store for retrieval.
"""

import os
import re
import glob
import chromadb


def parse_recipe_metadata(content: str) -> dict:
    """Extract metadata from a recipe markdown file."""
    metadata = {"title": "", "category": "", "difficulty": "", "prep_time": "", "cook_time": ""}
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if title_match:
        metadata["title"] = title_match.group(1).strip()
    cat_match = re.search(r'## Category:\s*(.+)$', content, re.MULTILINE)
    if cat_match:
        metadata["category"] = cat_match.group(1).strip()
    diff_match = re.search(r'## Difficulty:\s*(.+)$', content, re.MULTILINE)
    if diff_match:
        metadata["difficulty"] = diff_match.group(1).strip()
    prep_match = re.search(r'## Prep Time:\s*(.+)$', content, re.MULTILINE)
    if prep_match:
        metadata["prep_time"] = prep_match.group(1).strip()
    cook_match = re.search(r'## Cook Time:\s*(.+)$', content, re.MULTILINE)
    if cook_match:
        metadata["cook_time"] = cook_match.group(1).strip()
    return metadata


def chunk_document(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """Split text into fixed-size chunks with overlap."""
    if not text or not text.strip():
        return []
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks


def load_documents(data_dir: str = "data") -> list[dict]:
    """Load all recipe markdown files from the data directory."""
    documents = []
    md_files = sorted(glob.glob(os.path.join(data_dir, "*.md")))
    if not md_files:
        print(f"Warning: No .md files found in '{data_dir}'")
        return documents
    for filepath in md_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        metadata = parse_recipe_metadata(content)
        documents.append({"filename": os.path.basename(filepath), "content": content, "metadata": metadata})
    return documents


def index_documents(data_dir: str = "data", db_path: str = "./chroma_db") -> chromadb.Collection:
    """Load, chunk, and index all recipe documents into ChromaDB."""
    print(f"Loading documents from '{data_dir}'...")
    documents = load_documents(data_dir)
    if not documents:
        raise ValueError(f"No documents found in '{data_dir}'")
    print(f"Loaded {len(documents)} recipe files.")
    client = chromadb.PersistentClient(path=db_path)
    try:
        client.delete_collection("recipes")
        print("Deleted existing 'recipes' collection.")
    except Exception:
        pass
    collection = client.create_collection(name="recipes", metadata={"description": "ChefBot recipe knowledge base"})
    all_chunks, all_ids, all_metadatas = [], [], []
    for doc in documents:
        chunks = chunk_document(doc["content"])
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc['filename']}::chunk_{i}"
            chunk_metadata = {
                "source": doc["filename"], "chunk_index": i,
                "title": doc["metadata"]["title"], "category": doc["metadata"]["category"],
                "difficulty": doc["metadata"]["difficulty"],
                "prep_time": doc["metadata"]["prep_time"], "cook_time": doc["metadata"]["cook_time"],
            }
            all_chunks.append(chunk)
            all_ids.append(chunk_id)
            all_metadatas.append(chunk_metadata)
    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        end = min(i + batch_size, len(all_chunks))
        collection.add(documents=all_chunks[i:end], ids=all_ids[i:end], metadatas=all_metadatas[i:end])
    print(f"Indexed {len(all_chunks)} chunks from {len(documents)} recipes.")
    return collection


def get_collection(db_path: str = "./chroma_db") -> chromadb.Collection:
    """Get the existing recipes collection from ChromaDB."""
    client = chromadb.PersistentClient(path=db_path)
    try:
        return client.get_collection("recipes")
    except Exception as e:
        raise ValueError("Recipe collection not found. Run indexing first.") from e


if __name__ == "__main__":
    print("=" * 60)
    print("ChefBot - Document Indexing")
    print("=" * 60)
    collection = index_documents()
    print(f"\nCollection stats:")
    print(f"  Total chunks: {collection.count()}")
    results = collection.query(query_texts=["Italian pasta recipe"], n_results=3)
    print(f"\nTest query 'Italian pasta recipe' returned {len(results['documents'][0])} results:")
    for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        print(f"  {i+1}. [{meta['title']}] {doc[:80]}...")
