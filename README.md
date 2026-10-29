# ChefBot: Domain-Specific RAG Cooking Assistant & FastMCP Server

ChefBot is an intelligent culinary assistant combining Retrieval-Augmented Generation (RAG) with the Model Context Protocol (MCP). It features Hypothetical Document Embeddings (HyDE) for intent-resilient semantic search over structured culinary knowledge, local vector search via ChromaDB, and an extensible FastMCP server that exposes deterministic culinary tools and knowledge resources to MCP-compatible clients such as Claude Desktop.

---

## Architectural Overview

The system operates across two primary interaction layers: an interactive command-line interface (CLI) for direct query-response workflows and a Model Context Protocol (FastMCP) server exposing tools and resources for external agent orchestration.

```
+-------------------------------------------------------------------------------+
|                                  User Client                                  |
|               (Interactive CLI / Claude Desktop via FastMCP)                 |
+---------------------------------------+---------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
+----------------------------------+          +----------------------------------+
|           RAG Pipeline           |          |         FastMCP Server           |
|                                  |          |                                  |
|  1. HyDE Transformation          |          |  Tools:                          |
|     - Generate hypothetical doc  |          |  - find_substitutes              |
|  2. ChromaDB Vector Store        |          |  - calculate_nutrition           |
|     - all-MiniLM-L6-v2 embeddings|          |  - search_recipes                |
|     - Metadata filtering         |          |                                  |
|  3. Context Assembly             |          |  Resource:                       |
|     - Chunk aggregation          |          |  - recipes://categories          |
|  4. Generation                   |          +----------------------------------+
|     - Llama 3.2 (3B parameters)  |
+----------------+-----------------+
                 |
                 v
+----------------------------------+
|      Grounded Response Output    |
+----------------------------------+
```

---

## Technical Specifications

| Component | Specification |
|---|---|
| Language & Runtime | Python 3.11+ |
| Large Language Model | Llama 3.2 (3B parameters) via `ollamafreeapi` |
| Vector Database | ChromaDB (Persistent Client) |
| Embedding Model | `all-MiniLM-L6-v2` (default Chroma embedding function) |
| Retrieval Technique | Hypothetical Document Embeddings (HyDE) |
| Tool Integration | FastMCP (Model Context Protocol standard) |
| Chunking Strategy | Fixed-size sliding window (500 characters, 100 character overlap) |
| Knowledge Base | 21 curated Markdown recipe documents (~73 indexed chunks) |

---

## Key Features

### Hypothetical Document Embeddings (HyDE)
Standard vector similarity search between raw user queries and structured documentation frequently fails on abstract, intent-driven questions (e.g., *"recommend a comforting dinner for a cold rainy night"*). 

ChefBot implements HyDE:
1. **Hypothesis Synthesis:** The LLM generates a short hypothetical recipe excerpt matching the user's intent.
2. **Document-to-Document Vector Matching:** The generated hypothesis is embedded and queried against the ChromaDB vector collection.
3. **Context Injection:** Grounded context chunks are retrieved and injected into the final system prompt.

### Model Context Protocol (FastMCP) Server
ChefBot exposes its domain capabilities through FastMCP, enabling integration into agentic workflows and developer tooling:

- **`find_substitutes(ingredient: str) -> dict`**: Deterministic database covering culinary substitutions across 32+ common ingredients, providing functional alternatives (e.g., vegan binding agents, dairy replacements, acidity adjusters).
- **`calculate_nutrition(ingredients: list[dict]) -> dict`**: Computes aggregate macronutrient profiles (calories, protein, carbohydrates, fat) for ingredient lists with normalized weights.
- **`search_recipes(query: str, category: str = None, difficulty: str = None) -> list[dict]`**: Performs semantic vector search over the knowledge base with optional categorical and difficulty metadata filters.
- **Resource `recipes://categories`**: Exposes structured JSON summarizing available recipe categories and document distribution.

---

## Project Structure

```
chefbot/
├── data/                       # Curated recipe knowledge base (21 Markdown documents)
│   ├── beef_stir_fry.md
│   ├── chicken_tikka_masala.md
│   ├── mushroom_risotto.md
│   ├── shakshuka.md
│   └── ...
├── evaluation/                 # Benchmark evaluation suite
│   ├── evaluate.py             # Automated precision and relevance test harness
│   ├── results.md              # Quantitative analysis and ablation comparisons
│   └── test_queries.json       # 10 golden reference test queries
├── examples/
│   └── demo.md                 # Sample CLI and MCP interaction transcripts
├── mcp_server/
│   ├── __init__.py
│   └── server.py               # FastMCP tool and resource definitions
├── rag/
│   ├── __init__.py
│   ├── indexing.py             # Markdown parsing, metadata extraction, ChromaDB indexing
│   └── retrieval.py            # HyDE hypothesis generation and context-grounded Q&A
├── .env.example                # Environment variable configuration template
├── main.py                     # Interactive CLI REPL
└── requirements.txt            # Python dependencies
```

---

## Setup and Installation

### Prerequisites
- Python 3.11 or higher
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/abdulrahman532/chefbot.git
cd chefbot
```

### 2. Environment Setup

Create and activate an isolated virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Build Vector Index

Parse the raw recipe files, extract metadata attributes (title, category, difficulty, prep time, cook time), chunk documents, and index into ChromaDB:

```bash
python -m rag.indexing
```

This generates the persistent database located at `./chroma_db`.

---

## Usage

### Interactive CLI

Launch the command-line REPL:

```bash
python main.py
```

Available REPL commands:
- `/help` — Display command reference and operational instructions.
- `/hyde on|off` — Toggle HyDE retrieval on or off to evaluate retrieval behavior.
- `/reindex` — Rebuild the ChromaDB vector store from raw documents.
- `/quit` or `/exit` — Terminate the session.

### FastMCP Server Integration

Run the MCP server directly:

```bash
python -m mcp_server.server
```

#### Configuration with Claude Desktop

Add the following definition to your Claude Desktop configuration file (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "chefbot": {
      "command": "/absolute/path/to/chefbot/.venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/absolute/path/to/chefbot"
    }
  }
}
```

---

## Evaluation Benchmark

The system was evaluated using 10 benchmark queries spanning concrete ingredient lookups, abstract meal planning, and multi-constraint substitution tasks.

| Metric | Basic Retrieval | HyDE-Assisted Retrieval |
|---|---|---|
| Top-5 Retrieval Precision | 90% (9/10) | **100% (10/10)** |
| Mean Answer Relevance (Scale 1–5) | 3.8 / 5.0 | **4.7 / 5.0** |
| Abstract Intent Capture | Moderate | **High** |

Detailed evaluation traces and failure analysis are documented in [evaluation/results.md](evaluation/results.md).

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for full details.
