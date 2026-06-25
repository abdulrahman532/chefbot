# ChefBot 🍳 — Domain-Specific AI Cooking Assistant

A Retrieval-Augmented Generation (RAG) cooking assistant with MCP tool capabilities, built as a course project demonstrating RAG, prompt engineering, and tool-augmented LLM systems.

## Demo Video

> **[▶️ Watch the demo on YouTube](https://youtube.com/YOUR_UNLISTED_LINK_HERE)**

---

## Domain: Recipe & Cooking

ChefBot is a domain-specific AI assistant for **recipes and cooking**. This domain is well-suited for RAG + tools because:

- **Rich structured data**: Recipes have clear structure (ingredients, instructions, nutrition, times) that benefits from metadata-aware retrieval.
- **Natural tool use cases**: Ingredient substitution, nutrition calculation, and recipe search are practical actions that go beyond simple Q&A.
- **Diverse query types**: Users ask for specific recipes, general recommendations, cooking techniques, dietary alternatives, and nutritional info — testing the system's versatility.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    User Query                        │
└──────────────────────┬──────────────────────────────┘
                       │
              ┌────────▼────────┐
              │   main.py CLI   │
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────────┐
         │             │                 │
    ┌────▼────┐  ┌─────▼──────┐   ┌─────▼──────┐
    │  HyDE   │  │  ChromaDB  │   │ MCP Server │
    │ (Gemini)│  │ Vector DB  │   │ (FastMCP)  │
    └────┬────┘  └─────┬──────┘   └─────┬──────┘
         │             │                 │
         └──────┬──────┘          ┌──────┴──────┐
                │                 │  Tools:     │
         ┌──────▼──────┐         │ • substitute│
         │  Retrieved  │         │ • nutrition │
         │  Retrieved  │         │ • search    │
         └──────┬──────┘         │ Resource:   │
                │                │ • categories│
         ┌──────▼──────┐         └─────────────┘
         │OllamaFreeAPI│
         │ Generation  │
         └──────┬──────┘
                │
         ┌──────▼──────┐
         │   Answer    │
         └─────────────┘
```

**Key Components:**
- **RAG Pipeline** (`rag/`): Fixed-size chunking with overlap → ChromaDB vector store → HyDE-enhanced retrieval → OllamaFreeAPI generation
- **MCP Server** (`mcp_server/`): FastMCP server with 3 tools + 1 resource
- **CLI** (`main.py`): Interactive command-line interface

---

## Advanced RAG Technique: HyDE

This project implements **HyDE (Hypothetical Document Embeddings)** as the advanced retrieval technique:

1. Given a user query, the LLM generates a **hypothetical recipe excerpt** that would answer the question
2. This hypothetical document is used as the search query against ChromaDB
3. This improves retrieval by matching **document-to-document** rather than **query-to-document**

HyDE is particularly effective for abstract queries like *"something warm and comforting for a cold evening"* where direct keyword matching would fail.

---

## Setup Instructions

### Prerequisites
- Python 3.11+

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/chefbot.git
cd chefbot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### Build the Index

```bash
python -m rag.indexing
```

This processes the 21 recipe documents and creates the ChromaDB vector store (~73 chunks).

### Run the Assistant

```bash
python main.py
```

**CLI Commands:**
| Command | Description |
|---------|-------------|
| `/help` | Show help |
| `/hyde on\|off` | Toggle HyDE retrieval |
| `/reindex` | Rebuild the recipe index |
| `/quit` | Exit |

### Run the MCP Server

```bash
python -m mcp_server.server
```

For Claude Desktop, add to your MCP config:
```json
{
  "mcpServers": {
    "chefbot": {
      "command": "/path/to/chefbot/.venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/chefbot"
    }
  }
}
```

---

## Project Structure

```
chefbot/
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
├── main.py                    # Interactive CLI entry point
├── data/                      # 21 recipe markdown documents
│   ├── spaghetti_bolognese.md
│   ├── chicken_tikka_masala.md
│   ├── ... (21 files total)
├── rag/
│   ├── __init__.py
│   ├── indexing.py            # Document loading, chunking, ChromaDB indexing
│   └── retrieval.py           # HyDE retrieval + Gemini generation
├── mcp_server/
│   ├── __init__.py
│   └── server.py              # FastMCP server (3 tools + 1 resource)
├── evaluation/
│   ├── test_queries.json      # 10 test questions
│   └── results.md             # Evaluation results & analysis
└── examples/
    └── demo.md                # 3 example interactions
```

---

## MCP Tools & Resources

| Type | Name | Description |
|------|------|-------------|
| 🔧 Tool | `find_substitutes(ingredient)` | Find cooking substitutions for an ingredient (30+ ingredients) |
| 🔧 Tool | `calculate_nutrition(ingredients)` | Estimate nutrition for a list of ingredients with quantities |
| 🔧 Tool | `search_recipes(query, category?, difficulty?)` | Semantic search over the recipe knowledge base |
| 📦 Resource | `recipes://categories` | Summary of all recipe categories with counts |

---

## Technologies Used

- **LLM**: `llama3.2:3b` via `ollamafreeapi` (No API keys required)
- **Vector DB**: ChromaDB (local, with default all-MiniLM-L6-v2 embeddings)
- **MCP Framework**: FastMCP 3.x
- **Language**: Python 3.11+

---

## Evaluation Summary

- **Retrieval Precision (Top-5)**: 100% (10/10 test queries)
- **Average Answer Relevance**: 4.7 / 5.0
- **HyDE vs Basic**: HyDE improved relevance on abstract queries by ~1 point

See [evaluation/results.md](evaluation/results.md) for full analysis including failure cases and improvement suggestions.

---

## License

This project was created as a course assignment. For educational purposes only.
