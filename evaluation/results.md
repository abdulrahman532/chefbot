# ChefBot Evaluation Results

## Evaluation Methodology

Each of the 10 test queries was evaluated on two dimensions:

1. **Answer Relevance** (1-5 scale): How well the generated answer addresses the user's question
   - 5: Perfect, comprehensive answer with accurate details
   - 4: Good answer, mostly relevant with minor omissions
   - 3: Acceptable, partially addresses the question
   - 2: Weak, mostly irrelevant or inaccurate
   - 1: Completely irrelevant

2. **Retrieval Precision**: Whether the expected source document was retrieved in the top-5 results
   - ✅ Hit: Expected document retrieved
   - ❌ Miss: Expected document not retrieved

## Results Summary

| # | Query | Expected Source | Retrieved? | Relevance (1-5) | Method |
|---|-------|----------------|------------|-----------------|--------|
| 1 | How do I make spaghetti bolognese? | spaghetti_bolognese.md | ✅ | 5 | HyDE |
| 2 | What's a good easy dessert recipe? | chocolate_brownies.md | ✅ | 5 | HyDE |
| 3 | How long does it take to cook chicken tikka masala? | chicken_tikka_masala.md | ✅ | 5 | HyDE |
| 4 | What ingredients do I need for guacamole? | guacamole.md | ✅ | 5 | HyDE |
| 5 | Can you suggest a vegetarian meal? | vegetarian_chili.md | ✅ | 4 | HyDE |
| 6 | What's the nutritional information for caesar salad? | caesar_salad.md | ✅ | 5 | HyDE |
| 7 | How do I make a creamy Italian pasta dish? | chicken_alfredo.md | ✅ | 5 | HyDE |
| 8 | What's a good breakfast recipe with eggs? | shakshuka.md | ✅ | 4 | HyDE |
| 9 | How do I caramelize onions for French onion soup? | french_onion_soup.md | ✅ | 5 | HyDE |
| 10 | What Asian recipes do you have? | pad_thai.md | ✅ | 4 | HyDE |

### Aggregate Metrics
- **Retrieval Precision (Top-5)**: 10/10 = **100%**
- **Average Answer Relevance**: 4.7 / 5.0
- **HyDE vs Basic Comparison**: HyDE consistently retrieved more semantically relevant chunks, particularly for abstract queries like "creamy Italian pasta dish" where basic retrieval sometimes prioritized keyword overlap over semantic meaning.

## HyDE vs Basic Retrieval Comparison

For queries 5, 7, and 10, we compared HyDE and basic retrieval:

| Query | Basic Precision | HyDE Precision | Basic Relevance | HyDE Relevance |
|-------|----------------|----------------|-----------------|----------------|
| Can you suggest a vegetarian meal? | ✅ | ✅ | 3 | 4 |
| How do I make a creamy Italian pasta dish? | ✅ | ✅ | 4 | 5 |
| What Asian recipes do you have? | ✅ | ✅ | 3 | 4 |

**Key Finding**: HyDE shows the greatest improvement on abstract/conceptual queries where the user's phrasing doesn't directly match document keywords. By generating a hypothetical answer first, HyDE creates a document-like embedding that better matches the actual recipe documents in the vector space.

## Failure Cases & Analysis

### Failure Case 1: Cross-Recipe Queries
**Query**: "What can I make with chicken, cream, and garlic?"
**Issue**: The system retrieves individual recipe chunks that mention these ingredients separately but struggles to synthesize across recipes. The retrieval returns chunks from Chicken Tikka Masala (has chicken and cream) and Chicken Alfredo (has chicken, cream, and garlic), but the generated answer sometimes focuses on only one recipe rather than listing all options.
**Potential Improvement**: Implement a re-ranking step that scores retrieved chunks based on how many of the query's key ingredients they mention, then aggregate by recipe title before generation.

### Failure Case 2: Quantity/Scaling Questions
**Query**: "How do I make shakshuka for 8 people?"
**Issue**: The RAG system retrieves the correct shakshuka recipe but the original recipe serves ~2-4 people. The LLM attempts to scale ingredients but sometimes makes arithmetic errors (e.g., doubling some but not others). The system has no built-in scaling logic.
**Potential Improvement**: Add a dedicated `scale_recipe` MCP tool that programmatically parses ingredient quantities and multiplies them by the requested factor, then feed the scaled recipe to the LLM for natural language formatting.

## Potential Improvements

1. **Hybrid Search**: Combine vector similarity with BM25 keyword search to improve retrieval for queries containing specific recipe names or ingredient terms.
2. **Re-ranking**: Add a cross-encoder re-ranker (e.g., using a small model) between retrieval and generation to better score relevance.
3. **Recipe-Level Retrieval**: Instead of returning individual chunks, group chunks by recipe and return complete recipes for better context during generation.
4. **Query Classification**: Classify incoming queries (recipe lookup vs. technique vs. recommendation) and use different retrieval strategies for each.
5. **User Preference Memory**: Store user dietary preferences and allergies to personalize recommendations over time.
