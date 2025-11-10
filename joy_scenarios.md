The idea pitch (short 100-150 word overview of the project idea)
Description of the target users
More detailed summary of what the application will do 
What data (from users, web, other sources, etc) will be needed
What is the role of LLMs
How your product will differ from both existing non-LLM powered systems in the domain and from just using a general purpose LLM for the task (e.g. Gemini, Claude or ChatGPT)

3. Each group member should create TWO USAGE SCENARIOS for the product. A usage scenario consists of:

Short description - e.g. 'Capturing my network of friends and family through chat interaction'

Narrative of scenario - e.g. 'The user will engage in a chat conversation with MyNetGPT and be prompted to talk about recent social interactions, activities and situations they have done with their friends and family. The LLM will build up a list of names from these chats and ask follow up questions about them. In the background the app is constructing an ego network where nodes are the names of the friends (with attributes for features like how long you've known them, how strong the relationship is, what the individual likes/dislikes, how often you see them etc) and edges between the nodes based on imputing relationships like "A knows B", "A socializes with C" etc. from the chat history'

Step by step break down of the interaction - you can do this with bullet points and/or a Mermaid Sequence Diagram
Data description - what data is:
Needed for the app/LLM to engage and complete this scenario (be specific about the type of data, how it will be provided to the LLM etc)
Created as a result of the interaction, e.g. as a result of the 'tell me about your social interactions' scenario, a data structure (i.e. a network data structure) will be built and updated 

Evaluation - how will you test whether the application has successfully completed the scenario and what possible complications, errors should you consider (e.g. what happens if the input from the user is unexpected or adversarial etc)


## Scenario 1
#### Creating a manageable recipe using only the ingredients the user has in their fridge 
The user will initiate a chat stating they want to cook something but only have a specific set of ingredients. The LLM (acting as a "kitchen assistant") will ask the user to list everything they have available, including items in their fridge and pantry. A critical step is that the LLM will then prompt for common staples that users often forget to list (e.g., "Do you also have basics like salt, pepper, cooking oil, flour, or sugar?"). Once the user confirms the complete list, the LLM will analyze the ingredients and search its knowledge base for a recipe that uses only those items (or a subset). It will then present a recipe with a title, a final ingredient list, and manageable, step-by-step instructions. The user can then ask follow-up questions for clarification (e.g., "How high should the heat be?").

**Step-by-step break down:**
    User: "I'm hungry. What can I make with what I have?"
    KitchenAssistant: "I can help with that! Please list all the ingredients you have in your fridge and pantry."
    User: "Okay, I have two chicken breasts, an onion, a can of black beans, and some shredded cheddar cheese."
    KitchenAssistant: "Got it. And do you have common staples like cooking oil, salt, pepper, and any spices (like chili powder or cumin)?"
    User: "Yes, I have olive oil, salt, pepper, and chili powder."
    KitchenAssistant: Searches for recipes matching ONLY these items.)
    KitchenAssistant: "Great! You can make a *Quick Chicken and Bean Skillet*. Here's how:..."
    User: "How long does that take?"
    KitchenAssistant: "This recipe should take about 20-25 minutes from start to finish."
    
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
#### Generating a five day meal prepping plan that focuses on some diet goal like losing weight or bulking up
