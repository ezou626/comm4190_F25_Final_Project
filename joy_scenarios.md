## Scenario 1
### Creating a manageable recipe using only the ingredients the user has in their fridge 
The user will initiate a chat stating they want to cook something but only have a specific set of ingredients. The LLM (acting as a "kitchen assistant") will ask the user to list everything they have available, including items in their fridge and pantry. A critical step is that the LLM will then prompt for common staples that users often forget to list (e.g., "Do you also have basics like salt, pepper, cooking oil, flour, or sugar?"). Once the user confirms the complete list, the LLM will analyze the ingredients and search its knowledge base for a recipe that uses only those items (or a subset). It will then present a recipe with a title, a final ingredient list, and manageable, step-by-step instructions. The user can then ask follow-up questions for clarification (e.g., "How high should the heat be?").

**Step-by-step break down:**
<span style = 'color: #4171bf'>User: "I'm hungry. What can I make with what I have?"</span>
<span style = 'color: #40a33e'>KitchenAssistant: "I can help with that! Please list all the ingredients you have in your fridge and pantry."</span>
<span style = 'color: #4171bf'>User: "Okay, I have two chicken breasts, an onion, a can of black beans, and some shredded cheddar cheese."</span>
<span style = 'color: #40a33e'>KitchenAssistant: "Got it. And do you have common staples like cooking oil, salt, pepper, and any spices (like chili powder or cumin)?"</span>
<span style = 'color: #4171bf'>User: "Yes, I have olive oil, salt, pepper, and chili powder."</span>
<span style = 'color: #40a33e'>KitchenAssistant: Searches for recipes matching ONLY these items.</span>
<span style = 'color: #40a33e'>KitchenAssistant: "Great! You can make a *Quick Chicken and Bean Skillet*. Here's how:..."</span>
<span style = 'color: #4171bf'>User: "How long does that take?"</span>
<span style = 'color: #40a33e'>KitchenAssistant: "This recipe should take about 20-25 minutes from start to finish."</span>
    
**Data**

1. User-Provided Ingredient List: A natural language text input from the user (e.g., "I have 3 eggs, half a loaf of bread, and some milk").
2. User Confirmation of Staples: A follow-up "yes/no" or text list confirming pantry staples (oil, salt, spices, etc.).
3. Implicit LLM Knowledge: The LLM's internal, pre-trained knowledge base of countless recipes, cooking techniques, and ingredient pairings.
4. Parsed Ingredient List: A structured list (like an array) that the LLM creates internally to represent the user's available items. 

Recipe Output: A structured text response for the user, broken down into:

(Recipe Title)
(Formatted Ingredient List)
(Numbered, step-by-step instructions)

**Evaluation**

Simple Test: Give the LLM a classic, simple list (e.g., "eggs, milk, bread, butter"). It should successfully return a recipe for French Toast.

Constraint Test: Give the LLM a list (e.g., "chicken, lettuce, tomatoes, onion") and explicitly state "I do not have oil or any dressing." A successful test means the LLM does not suggest a "simple vinaigrette" (which requires oil) but instead suggests something like a "dry-rubbed chicken salad."

Subset Test: Give the LLM a longer list (e.g., "flour, sugar, eggs, butter, chocolate chips, onions, garlic"). It should be able to identify the "sweet" subset and suggest Chocolate Chip Cookies, correctly ignoring the onions and garlic.

**Possible complications and errors**

Ingredient Hallucination: The most critical failure. The LLM suggests a recipe and adds an ingredient that the user did not list (e.g., "add a splash of lemon juice" when the user never mentioned lemons).

Vague User Input: The user says "some vegetables" or "cheese." The LLM must be programmed to ask for clarification ("What kind of vegetables?" or "What type of cheese?") as this drastically changes the possible recipes.

Incoherent Ingredients: The user provides a list with no logical recipe (e.g., "gummy bears, a can of tuna, and mustard"). The LLM should gracefully state that it cannot find a manageable recipe for that combination, rather than inventing something inedible.


## Scenario 2
### Generating a five day meal prepping plan that focuses on some diet goal like losing weight or bulking up
The user will state their primary fitness or health goal (e.g., "I want a 5-day meal plan to lose weight" or "I need to bulk up"). The LLM, acting as a "Nutrition Planner," will recognize that it needs more information. It will first ask for any dietary restrictions, allergies, or strong dislikes. Next, it will ask the user if they have a specific daily calorie and macro (protein, carbs, fat) target. If the user knows their targets (e.g., "Yes, 2,000 calories and 150g protein"), the LLM uses those numbers. If the user does not know their targets, the LLM will offer to provide an estimate, prompting for key variables (age, weight, height, biological sex, and weekly activity level) to calculate a rough daily need based on their goal (e.g., a caloric deficit for weight loss, a surplus for bulking). Once all constraints are gathered, the LLM will generate a complete 5-day plan. This plan will consist of three parts: A shopping list, organized by grocery store section, "prep day" instructions, and a guide for using the ingredients for breakfast, lunch, dinner, and snacks across five days.


**Step-by-step break down:**
<span style = 'color: #4171bf'>User: "I need a 5-day meal prep plan to help me lose weight."</span>
<span style = 'color: #40a33e'>NutritionPlanner: "I can definitely build that for you. First, do you have any food allergies, dietary restrictions (like vegan, gluten-free), or strong dislikes (like mushrooms or cilantro)?"</span>
<span style = 'color: #4171bf'>User: "I'm not allergic to anything, but I hate olives."</span>
<span style = 'color: #40a33e'>NutritionPlanner: "Got it, no olives! Do you have a specific daily calorie or macro target you're aiming for?"</span>
<span style = 'color: #4171bf'>User: "No, I have no idea. Can you help with that?"</span>
<span style = 'color: #40a33e'>NutritionPlanner: "Sure! To estimate your targets for weight loss, I just need your age, weight, height, biological sex, and typical weekly activity level."</span>
<span style = 'color: #4171bf'>User: "I'm 30, 190 lbs, 5'10", male, and I work a desk job but go to the gym 3 times a week."</span>
<span style = 'color: #40a33e'>NutritionPlanner-: "Thanks. Based on that, I'd suggest a target of around 2,100 calories per day for sustainable weight loss. Does that sound manageable?"</span>
<span style = 'color: #4171bf'>User: "Yes, that sounds perfect."</span>
<span style = 'color: #40a33e'>NutritionPlanne: "Excellent. Here is your 5-Day Weight Loss Meal Prep Plan: *Shopping List:* 3 bell peppers, 2 onions, 1 bag of spinach... *Protein:* 5 lbs chicken breast, 1 dozen eggs... *Pantry:* 1 bag quinoa, olive oil... *Sunday Prep Instructions (Approx. 2 hours):* Cook 3 cups of dry quinoa... *Daily Assembly Plan:* (D1) Breakfast is 3 scrambled eggs with spinach. Lunch is a Quinoa bowl with 6oz sliced chicken, 1/2 cup chopped peppers..."</span>

**Data**

1. User Goal: (Text) The primary goal (e.g., "lose weight," "bulk up," "keto," "vegetarian").
2. User Restrictions: (Text/List) A list of allergies ("peanuts," "shellfish"), dislikes ("mushrooms"), and diets ("gluten-free").
3. User Profile (Conditional): (Numeric/Text) Age, weight (lbs/kg), height (ft/cm), biological sex, and activity level (e.g., "sedentary," "lightly active," "very active"). This is only needed if the user does not provide their own targets.
4. User Targets (Conditional): (Numeric) Daily calories, protein (g), carbs (g), fat (g).

Shopping List: A categorized list of all ingredients needed.
Prep Instructions: A numbered list of bulk cooking tasks.
Daily Plan: A 5-day schedule, with each day broken down into "Breakfast," "Lunch," "Dinner," and "Snacks," specifying the meal and assembly steps.

**Evaluation**

Goal Adherence Test: Give the LLM a "bulking" goal with a 3,500-calorie target. The sum of the calories from all daily meals in the generated plan should be reasonably close (e.g., within 100-200 calories) of 3,500.

Restriction Adherence Test (Critical): Give the LLM a "peanut allergy" restriction. The entire generated plan (shopping list and recipes) must be scanned to ensure it contains no peanuts, peanut butter, or peanut oil. Success is 100% compliance.

Efficiency Test: Does the plan reuse ingredients? A successful "prep" plan will have "cooked quinoa" in the prep steps and then use that quinoa for 3-4 lunches. A failed plan would suggest cooking quinoa from scratch every day.

Completeness Test: Does the output contain all three required components: Shopping List, Prep Instructions, and Daily Assembly Plan?

**Possible complications and errors**

Nutritional Miscalculation: The LLM miscalculates the TDEE or the total calories of the suggested meals, causing the plan to fail the user's goal (e.g., a "weight loss" plan that is 3,000 calories).

Unrealistic Plan: The LLM suggests a prep plan that takes 8 hours to cook or requires niche, expensive ingredients (e.g., "saffron and fresh truffles") for a standard plan.

Boring/Repetitive Plan: The LLM suggests the exact same breakfast, lunch, and dinner for all 5 days. While efficient, it's a poor user experience. A good plan should have some variety (e.g., same base, different sauces/spices).

Vague User Input: The user says, "I want to eat better." The LLM must be programmed to probe for a more specific, measurable goal (e.g., "What does 'better' mean to you? Are you looking to lose weight, gain muscle, or just add more vegetables?").