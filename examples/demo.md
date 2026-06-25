# ChefBot - Example Interactions

Below are three example interactions demonstrating different capabilities of ChefBot.

---

## Example 1: Recipe Lookup with RAG

This demonstrates the core RAG functionality — asking about a specific recipe and getting detailed information retrieved from the knowledge base.

```
You: How do I make spaghetti bolognese?

[Retrieving with HyDE...]

ChefBot: Here's how to make a delicious Classic Spaghetti Bolognese!

**Prep Time:** 15 mins | **Cook Time:** 45 mins | **Difficulty:** Medium

**Ingredients:**
- 400g spaghetti
- 500g ground beef
- 1 medium onion, finely chopped
- 2 garlic cloves, minced
- 1 carrot, finely chopped
- 1 celery stalk, finely chopped
- 400g canned crushed tomatoes
- 2 tbsp tomato paste
- 100ml red wine (optional)
- 1 tsp dried oregano
- Salt and black pepper to taste
- 2 tbsp olive oil
- Grated parmesan cheese for serving

**Instructions:**
1. Heat olive oil in a large pan over medium heat. Add onion, garlic, carrot,
   and celery. Cook until soft (approx. 5 minutes).
2. Add the ground beef and cook until browned, breaking it up with a spoon.
3. Pour in the red wine (if using) and simmer until reduced by half.
4. Stir in the tomato paste, crushed tomatoes, dried oregano, salt, and pepper.
5. Reduce heat to low, cover, and simmer for 35-40 minutes, stirring occasionally.
6. Meanwhile, cook the spaghetti in boiling salted water according to package instructions.
7. Drain spaghetti and serve with the Bolognese sauce spooned over the top.
   Garnish with grated parmesan.

**Tip:** For extra flavor, let the sauce simmer even longer — the flavors develop
beautifully over time!

📚 Sources (hyde):
   • Classic Spaghetti Bolognese [Italian]
   • Creamy Chicken Alfredo [Italian]
```

---

## Example 2: Ingredient Substitution (MCP Tool Usage)

This demonstrates the `find_substitutes` MCP tool being used to find alternatives for a cooking ingredient.

```
> Tool call: find_substitutes(ingredient="eggs")

Substitutes for 'eggs':
  1. flax egg (1 tbsp ground flax + 3 tbsp water)
  2. chia egg (1 tbsp chia + 3 tbsp water)
  3. mashed banana (1/4 cup per egg)
  4. unsweetened applesauce (1/4 cup per egg)
```

And a nutrition calculation example:

```
> Tool call: calculate_nutrition(ingredients=["200g chicken breast", "1 cup rice", "2 tbsp olive oil"])

Nutritional Breakdown:
==================================================

200g chicken breast (200g):
  Calories: 330 kcal
  Protein:  62.0g
  Carbs:    0.0g
  Fat:      7.2g

1 cup rice (240g):
  Calories: 312 kcal
  Protein:  6.5g
  Carbs:    67.2g
  Fat:      0.7g

2 tbsp olive oil (30g):
  Calories: 265 kcal
  Protein:  0.0g
  Carbs:    0.0g
  Fat:      30.0g

==================================================
TOTALS:
  Calories: 907 kcal
  Protein:  68.5g
  Carbs:    67.2g
  Fat:      37.9g
```

---

## Example 3: Conversational Query with HyDE Enhancement

This demonstrates a more abstract query where HyDE's hypothetical document generation improves retrieval quality by matching semantic meaning rather than keywords.

```
You: I want something warm and comforting for a cold evening, maybe with cheese on top

[Retrieving with HyDE...]

ChefBot: For a cozy, comforting meal on a cold evening, I'd highly recommend
the Classic French Onion Soup! 🧅

This rich and warming soup features deeply caramelized onions simmered in
beef broth, topped with toasted baguette and melted Gruyère cheese — the
perfect cold-weather comfort food.

**Key highlights:**
- **Prep Time:** 15 mins | **Cook Time:** 1 hour
- The caramelization process (45 minutes to 1 hour) is what makes this soup
  special — it transforms ordinary onions into something incredibly sweet
  and flavorful
- Topped with a thick layer of bubbly, golden Gruyère cheese under the broiler

**Pro tip:** Use high-quality beef broth for the best results, and don't rush
the caramelization — patience is the secret ingredient here!

Another great cheesy option is the Creamy Mushroom Risotto, which features
½ cup of grated parmesan stirred in at the end for a rich, creamy finish.

📚 Sources (hyde):
   • Classic French Onion Soup [Soup]
   • Creamy Mushroom Risotto [Italian]
   • Classic Margherita Pizza [Italian]
```

**Why HyDE helped here:** The user didn't mention any specific recipe, dish name, or cuisine. The query is purely about a *feeling* ("warm", "comforting", "cold evening", "cheese on top"). HyDE first generates a hypothetical document about warm, cheesy comfort food, which semantically matches against the French Onion Soup document much better than a direct keyword search on the original query would.

---

## ReAct Pattern Demonstration

ChefBot implements a basic ReAct (Reasoning + Acting) pattern when processing queries through the MCP server. Here's how the reasoning chain works:

```
User: I'm making pad thai but I'm allergic to peanuts. What can I use instead?

Thought: The user needs a substitute for peanuts in pad thai. I should:
  1. First search for the pad thai recipe to understand the context
  2. Then find substitutes for peanuts

Action: search_recipes(query="pad thai")
Observation: Found "Authentic Pad Thai" - uses 1/4 cup crushed roasted peanuts
  as garnish.

Action: find_substitutes(ingredient="peanuts")
Observation: No direct peanut substitution in database.

Thought: Peanuts are used as a garnish in pad thai. Common alternatives for
  peanut allergies include cashews, sunflower seeds, or toasted coconut.
  I can provide this general knowledge.

Response: In the Authentic Pad Thai recipe, peanuts are used as a garnish
  topping (1/4 cup crushed roasted peanuts). For a peanut-free version,
  you can substitute with:
  - Crushed roasted cashews (closest texture and flavor)
  - Toasted sunflower seeds (nut-free option)
  - Toasted sesame seeds
  - Toasted coconut flakes

  The rest of the recipe (rice noodles, tofu, shrimp, tamarind sauce)
  is naturally peanut-free, so no other changes needed!
```
