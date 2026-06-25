"""FastMCP server for ChefBot - Recipe & Cooking AI Assistant.

Provides tools for ingredient substitution, nutrition calculation,
and recipe search, plus a resource exposing recipe categories.
"""

import os
import re
import glob
from fastmcp import FastMCP

mcp = FastMCP(
    "ChefBot",
    instructions=(
        "ChefBot is a cooking and recipe AI assistant. Use the provided tools "
        "to find ingredient substitutions, calculate nutrition information, "
        "and search the recipe knowledge base."
    ),
)


# ── Ingredient Substitution Database ─────────────────────────

SUBSTITUTIONS = {
    "butter": ["coconut oil", "margarine", "applesauce (in baking)", "Greek yogurt (in baking)"],
    "eggs": ["flax egg (1 tbsp ground flax + 3 tbsp water)", "chia egg (1 tbsp chia + 3 tbsp water)", "mashed banana (1/4 cup per egg)", "unsweetened applesauce (1/4 cup per egg)"],
    "milk": ["almond milk", "oat milk", "soy milk", "coconut milk"],
    "heavy cream": ["coconut cream", "cashew cream", "silken tofu blended smooth", "milk + melted butter (3/4 cup milk + 1/3 cup butter)"],
    "all-purpose flour": ["almond flour", "oat flour", "coconut flour (use 1/3 amount)", "whole wheat flour"],
    "soy sauce": ["coconut aminos", "tamari (gluten-free)", "Worcestershire sauce", "liquid aminos"],
    "sugar": ["honey (reduce liquid in recipe)", "maple syrup", "stevia", "coconut sugar"],
    "brown sugar": ["white sugar + 1 tbsp molasses per cup", "coconut sugar", "maple syrup"],
    "olive oil": ["avocado oil", "coconut oil", "vegetable oil", "grapeseed oil"],
    "vegetable oil": ["olive oil", "coconut oil", "avocado oil", "melted butter"],
    "garlic": ["garlic powder (1/8 tsp per clove)", "garlic flakes", "shallots"],
    "onion": ["shallots", "leeks", "onion powder (1 tsp per small onion)", "scallions"],
    "lemon juice": ["lime juice", "white wine vinegar", "apple cider vinegar"],
    "parmesan cheese": ["pecorino romano", "nutritional yeast (vegan)", "aged asiago"],
    "mozzarella cheese": ["provolone", "Monterey Jack", "white cheddar"],
    "feta cheese": ["goat cheese", "ricotta salata", "queso fresco"],
    "cream cheese": ["mascarpone", "Greek yogurt", "ricotta"],
    "buttermilk": ["milk + 1 tbsp lemon juice (let sit 5 min)", "milk + 1 tbsp vinegar", "plain yogurt thinned with milk"],
    "yogurt": ["sour cream", "coconut yogurt (dairy-free)", "buttermilk"],
    "sour cream": ["Greek yogurt", "coconut cream", "cashew cream"],
    "chicken broth": ["vegetable broth", "mushroom broth", "water + bouillon cube"],
    "beef broth": ["mushroom broth", "vegetable broth + soy sauce", "red wine + water"],
    "white wine": ["chicken broth + splash of vinegar", "white grape juice", "dry vermouth"],
    "red wine": ["beef broth + splash of vinegar", "grape juice", "cranberry juice"],
    "cornstarch": ["arrowroot powder", "tapioca starch", "all-purpose flour (use 2x amount)"],
    "baking powder": ["1/4 tsp baking soda + 1/2 tsp cream of tartar per tsp"],
    "vanilla extract": ["maple extract", "almond extract (use less)", "vanilla bean paste"],
    "honey": ["maple syrup", "agave nectar", "corn syrup"],
    "rice": ["quinoa", "cauliflower rice", "couscous", "bulgur wheat"],
    "pasta": ["zucchini noodles", "spaghetti squash", "rice noodles", "shirataki noodles"],
    "bread crumbs": ["crushed crackers", "rolled oats", "crushed cornflakes", "almond meal"],
    "tomato paste": ["tomato sauce (use 3x amount, reduce liquid)", "ketchup (in a pinch)", "sun-dried tomatoes blended"],
}


# ── Nutrition Database (per 100g) ────────────────────────────

NUTRITION_DB = {
    "chicken breast": {"calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6},
    "chicken thigh": {"calories": 209, "protein": 26.0, "carbs": 0.0, "fat": 10.9},
    "chicken": {"calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6},
    "ground beef": {"calories": 250, "protein": 26.0, "carbs": 0.0, "fat": 15.0},
    "beef sirloin": {"calories": 207, "protein": 28.0, "carbs": 0.0, "fat": 10.0},
    "beef": {"calories": 250, "protein": 26.0, "carbs": 0.0, "fat": 15.0},
    "salmon": {"calories": 208, "protein": 20.0, "carbs": 0.0, "fat": 13.0},
    "shrimp": {"calories": 99, "protein": 24.0, "carbs": 0.2, "fat": 0.3},
    "tofu": {"calories": 76, "protein": 8.0, "carbs": 1.9, "fat": 4.8},
    "egg": {"calories": 155, "protein": 13.0, "carbs": 1.1, "fat": 11.0},
    "rice": {"calories": 130, "protein": 2.7, "carbs": 28.0, "fat": 0.3},
    "pasta": {"calories": 131, "protein": 5.0, "carbs": 25.0, "fat": 1.1},
    "spaghetti": {"calories": 131, "protein": 5.0, "carbs": 25.0, "fat": 1.1},
    "bread": {"calories": 265, "protein": 9.0, "carbs": 49.0, "fat": 3.2},
    "flour": {"calories": 364, "protein": 10.0, "carbs": 76.0, "fat": 1.0},
    "sugar": {"calories": 387, "protein": 0.0, "carbs": 100.0, "fat": 0.0},
    "butter": {"calories": 717, "protein": 0.9, "carbs": 0.1, "fat": 81.0},
    "olive oil": {"calories": 884, "protein": 0.0, "carbs": 0.0, "fat": 100.0},
    "milk": {"calories": 42, "protein": 3.4, "carbs": 5.0, "fat": 1.0},
    "heavy cream": {"calories": 340, "protein": 2.1, "carbs": 2.8, "fat": 36.0},
    "cream": {"calories": 340, "protein": 2.1, "carbs": 2.8, "fat": 36.0},
    "cheese": {"calories": 402, "protein": 25.0, "carbs": 1.3, "fat": 33.0},
    "parmesan": {"calories": 431, "protein": 38.0, "carbs": 4.1, "fat": 29.0},
    "mozzarella": {"calories": 280, "protein": 28.0, "carbs": 3.1, "fat": 17.0},
    "feta": {"calories": 264, "protein": 14.0, "carbs": 4.1, "fat": 21.0},
    "yogurt": {"calories": 59, "protein": 10.0, "carbs": 3.6, "fat": 0.4},
    "potato": {"calories": 77, "protein": 2.0, "carbs": 17.0, "fat": 0.1},
    "onion": {"calories": 40, "protein": 1.1, "carbs": 9.3, "fat": 0.1},
    "garlic": {"calories": 149, "protein": 6.4, "carbs": 33.0, "fat": 0.5},
    "tomato": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
    "carrot": {"calories": 41, "protein": 0.9, "carbs": 10.0, "fat": 0.2},
    "broccoli": {"calories": 34, "protein": 2.8, "carbs": 7.0, "fat": 0.4},
    "spinach": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4},
    "bell pepper": {"calories": 31, "protein": 1.0, "carbs": 6.0, "fat": 0.3},
    "mushroom": {"calories": 22, "protein": 3.1, "carbs": 3.3, "fat": 0.3},
    "avocado": {"calories": 160, "protein": 2.0, "carbs": 8.5, "fat": 14.7},
    "banana": {"calories": 89, "protein": 1.1, "carbs": 23.0, "fat": 0.3},
    "apple": {"calories": 52, "protein": 0.3, "carbs": 14.0, "fat": 0.2},
    "lemon": {"calories": 29, "protein": 1.1, "carbs": 9.3, "fat": 0.3},
    "chickpeas": {"calories": 164, "protein": 8.9, "carbs": 27.0, "fat": 2.6},
    "black beans": {"calories": 132, "protein": 8.9, "carbs": 24.0, "fat": 0.5},
    "kidney beans": {"calories": 127, "protein": 8.7, "carbs": 23.0, "fat": 0.5},
    "peanuts": {"calories": 567, "protein": 26.0, "carbs": 16.0, "fat": 49.0},
    "chocolate": {"calories": 546, "protein": 5.0, "carbs": 60.0, "fat": 31.0},
    "honey": {"calories": 304, "protein": 0.3, "carbs": 82.0, "fat": 0.0},
    "coconut milk": {"calories": 230, "protein": 2.3, "carbs": 6.0, "fat": 24.0},
}

# Unit conversion to grams
UNIT_TO_GRAMS = {
    "g": 1, "gram": 1, "grams": 1,
    "kg": 1000, "kilogram": 1000,
    "cup": 240, "cups": 240,
    "tbsp": 15, "tablespoon": 15, "tablespoons": 15,
    "tsp": 5, "teaspoon": 5, "teaspoons": 5,
    "oz": 28.35, "ounce": 28.35, "ounces": 28.35,
    "lb": 453.6, "pound": 453.6, "pounds": 453.6,
    "ml": 1,
    "piece": 100, "pieces": 100,
    "slice": 30, "slices": 30,
    "clove": 5, "cloves": 5,
}


def _parse_ingredient_string(ingredient_str: str) -> tuple[float, str]:
    """Parse an ingredient string to extract quantity in grams and ingredient name."""
    ingredient_str = ingredient_str.strip().lower()

    # Try matching "200g chicken breast" or "2 cups rice"
    match = re.match(
        r'^([\d.]+)\s*'
        r'(g|gram|grams|kg|kilogram|cup|cups|tbsp|tablespoon|tablespoons|'
        r'tsp|teaspoon|teaspoons|oz|ounce|ounces|lb|pound|pounds|ml|'
        r'piece|pieces|slice|slices|clove|cloves)\s+(.+)$',
        ingredient_str,
    )

    if match:
        quantity = float(match.group(1))
        unit = match.group(2)
        name = match.group(3).strip()
        grams = quantity * UNIT_TO_GRAMS.get(unit, 100)
        return grams, name

    # Default: assume 100g
    return 100.0, ingredient_str


def _find_nutrition(ingredient_name: str) -> dict | None:
    """Find nutrition data for an ingredient using fuzzy matching."""
    ingredient_name = ingredient_name.lower().strip()

    # Direct match
    if ingredient_name in NUTRITION_DB:
        return NUTRITION_DB[ingredient_name]

    # Partial match
    for key, val in NUTRITION_DB.items():
        if key in ingredient_name or ingredient_name in key:
            return val

    return None


# ── Tools ────────────────────────────────────────────────────

@mcp.tool()
def find_substitutes(ingredient: str) -> str:
    """Find common cooking substitutions for an ingredient.

    Given an ingredient name, returns a list of suitable alternatives
    that can be used as replacements in recipes.

    Args:
        ingredient: The ingredient to find substitutes for (e.g., 'butter', 'eggs').

    Returns:
        Formatted string listing available substitutions.
    """
    if not ingredient or not ingredient.strip():
        return "Error: Please provide an ingredient name."

    ingredient = ingredient.strip().lower()

    # Direct match
    if ingredient in SUBSTITUTIONS:
        subs = SUBSTITUTIONS[ingredient]
        lines = [f"Substitutes for '{ingredient}':"]
        for i, sub in enumerate(subs, 1):
            lines.append(f"  {i}. {sub}")
        return "\n".join(lines)

    # Partial match
    matches = []
    for key in SUBSTITUTIONS:
        if ingredient in key or key in ingredient:
            matches.append(key)

    if matches:
        lines = [f"No exact match for '{ingredient}', but found related ingredients:"]
        for key in matches:
            subs = SUBSTITUTIONS[key]
            lines.append(f"\nSubstitutes for '{key}':")
            for i, sub in enumerate(subs, 1):
                lines.append(f"  {i}. {sub}")
        return "\n".join(lines)

    return (
        f"No substitutions found for '{ingredient}'. "
        f"Available ingredients: {', '.join(sorted(SUBSTITUTIONS.keys()))}"
    )


@mcp.tool()
def calculate_nutrition(ingredients: list[str]) -> str:
    """Calculate estimated nutritional information for a list of ingredients.

    Parses ingredient strings (with quantities and units) and returns
    a per-ingredient breakdown plus totals for calories, protein, carbs, and fat.

    Args:
        ingredients: List of ingredient strings, e.g. ['200g chicken breast', '1 cup rice'].

    Returns:
        Formatted string with nutritional breakdown.
    """
    if not ingredients:
        return "Error: Please provide at least one ingredient."

    results = []
    totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
    not_found = []

    for ing_str in ingredients:
        grams, name = _parse_ingredient_string(ing_str)
        nutrition = _find_nutrition(name)

        if nutrition is None:
            not_found.append(name)
            continue

        # Scale nutrition from per-100g to actual amount
        scale = grams / 100.0
        item = {
            "ingredient": ing_str,
            "grams": grams,
            "calories": round(nutrition["calories"] * scale, 1),
            "protein": round(nutrition["protein"] * scale, 1),
            "carbs": round(nutrition["carbs"] * scale, 1),
            "fat": round(nutrition["fat"] * scale, 1),
        }
        results.append(item)

        for key in totals:
            totals[key] += item[key]

    # Format output
    lines = ["Nutritional Breakdown:", "=" * 50]

    for item in results:
        lines.append(
            f"\n{item['ingredient']} ({item['grams']:.0f}g):\n"
            f"  Calories: {item['calories']:.0f} kcal\n"
            f"  Protein:  {item['protein']:.1f}g\n"
            f"  Carbs:    {item['carbs']:.1f}g\n"
            f"  Fat:      {item['fat']:.1f}g"
        )

    lines.append("\n" + "=" * 50)
    lines.append(
        f"TOTALS:\n"
        f"  Calories: {totals['calories']:.0f} kcal\n"
        f"  Protein:  {totals['protein']:.1f}g\n"
        f"  Carbs:    {totals['carbs']:.1f}g\n"
        f"  Fat:      {totals['fat']:.1f}g"
    )

    if not_found:
        lines.append(f"\nNote: Could not find nutrition data for: {', '.join(not_found)}")

    return "\n".join(lines)


@mcp.tool()
def search_recipes(
    query: str,
    category: str = None,
    difficulty: str = None,
    max_results: int = 5,
) -> str:
    """Search the recipe knowledge base.

    Searches for recipes matching the query using semantic vector search.
    Optionally filter results by category or difficulty level.

    Args:
        query: Search query (e.g., 'quick Italian dinner', 'easy dessert').
        category: Optional filter by category (e.g., 'Italian', 'Dessert', 'Asian').
        difficulty: Optional filter by difficulty (e.g., 'Easy', 'Medium', 'Hard').
        max_results: Maximum number of results to return (default 5).

    Returns:
        Formatted string with matching recipes.
    """
    if not query or not query.strip():
        return "Error: Please provide a search query."

    try:
        from rag.indexing import get_collection
        collection = get_collection()
    except Exception as e:
        return f"Error: Recipe index not available. Please run indexing first. ({e})"

    # Build where filter for metadata
    where_filter = None
    conditions = []
    if category:
        conditions.append({"category": {"$eq": category}})
    if difficulty:
        conditions.append({"difficulty": {"$eq": difficulty}})

    if len(conditions) == 1:
        where_filter = conditions[0]
    elif len(conditions) > 1:
        where_filter = {"$and": conditions}

    try:
        results = collection.query(
            query_texts=[query],
            n_results=max_results,
            where=where_filter,
        )
    except Exception:
        # Retry without filter if filter causes issues
        results = collection.query(
            query_texts=[query],
            n_results=max_results,
        )

    if not results["documents"][0]:
        return "No recipes found matching your query."

    # Format results, deduplicating by recipe title
    seen_titles = set()
    lines = [f"Search results for '{query}':"]
    count = 0

    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        title = meta.get("title", "Unknown")
        if title in seen_titles:
            continue
        seen_titles.add(title)
        count += 1

        category_str = meta.get("category", "")
        difficulty_str = meta.get("difficulty", "")
        prep = meta.get("prep_time", "")
        cook = meta.get("cook_time", "")
        snippet = doc[:150].replace("\n", " ") + "..."

        lines.append(
            f"\n{count}. {title}\n"
            f"   Category: {category_str} | Difficulty: {difficulty_str}\n"
            f"   Prep: {prep} | Cook: {cook}\n"
            f"   {snippet}"
        )

    return "\n".join(lines)


# ── Resources ────────────────────────────────────────────────

@mcp.resource("recipes://categories")
def get_recipe_categories() -> str:
    """Get a summary of all recipe categories in the knowledge base.

    Returns a formatted summary showing each category and the number
    of recipes in it, along with recipe titles.
    """
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    if not os.path.exists(data_dir):
        data_dir = "data"  # fallback to relative path

    categories: dict[str, list[str]] = {}

    for filepath in sorted(glob.glob(os.path.join(data_dir, "*.md"))):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse category and title
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        cat_match = re.search(r'## Category:\s*(.+)$', content, re.MULTILINE)

        title = title_match.group(1).strip() if title_match else os.path.basename(filepath)
        category = cat_match.group(1).strip() if cat_match else "Uncategorized"

        if category not in categories:
            categories[category] = []
        categories[category].append(title)

    # Format output
    lines = [
        "ChefBot Recipe Categories",
        "=" * 40,
        f"Total recipes: {sum(len(v) for v in categories.values())}",
        f"Total categories: {len(categories)}",
        "",
    ]

    for cat in sorted(categories.keys()):
        recipes = categories[cat]
        lines.append(f"{cat} ({len(recipes)} recipes):")
        for recipe in recipes:
            lines.append(f"  - {recipe}")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
