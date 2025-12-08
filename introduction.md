## Blurb
Chefing is an intelligent, AI-powered kitchen assistant designed to transform home cooking into a personalized, effortless experience. By learning your taste preferences, dietary requirements, time constraints, and evolving habits, it creates recipes tailored precisely to your needs. Chefing’s voice-guided interface provides clear, step-by-step instructions, sets timers automatically, and recommends substitutions when ingredients are missing or unsuitable. The platform also emphasizes sustainability by reducing food waste through creative use of leftovers and generating adaptive grocery lists that encourage intentional shopping. With its ability to adjust to your lifestyle and support you throughout the cooking process, Chefing turns everyday meal preparation into a seamless collaboration — empowering you to cook efficiently, eat thoughtfully, and enjoy a smarter, more sustainable kitchen experience.

## Users
Chefing's primary target users are individuals and families who actively cook at home but seek to optimize the process for convenience, health, and sustainability. This audience includes health concious eaters, novice home cooks, and those with several allergies/sensitivities.

## A more detailed introduction
Chefing functions as a real-time, personalized AI Sous-Chef with three primary feature pillars:

1. Dynamic Recipe Generation: Chefing utilizes advanced AI to generate a unique recipe on demand. This recipe is simultaneously optimized against multiple live constraints: the user’s full taste profile, current dietary goals, specific time limits, and the exact ingredients (including quantities and expiration dates) currently on hand in the user's pantry/fridge.

2. Voice-Guided Real-Time Assistance: Through a voice-assisted interface, the application provides detailed, step-by-step cooking instructions, automatically manages and sets timers for each cooking step, and offers context-aware support.

3. Sustainability and Inventory Management: Chefing actively tracks user inventory (input via text, voice, or image recognition) to prioritize ingredients nearing expiration, automatically generating recipes specifically designed to minimize food waste by utilizing leftovers and near-expired items. It generates grocery lists based on planned meals, current stock, and purchasing history to promote intentional, waste-free shopping.

## Data
Chefing will need user input such as taste preferences, known allergies, specific nutritional goals (e.g., macros), skill level, and historical recipe ratings/feedback. And with inventory data from live tracking of all ingredients currently in the user's kitchen, including estimated quantities and monitored expiration dates. This is updated through manual input, image recognition (fridge/pantry scan), or integration with grocery APIs. And lastly, Chefing will need to know how much of a chef the user is. 

## Using LLMs
LLMs essentially power Chefing, enabling functionalities that move it far beyond simple recommendation tools. The LLM serves as a creative recipe generator, synthesizing novel, high-quality recipes from scratch by expertly combining constraints like inventory, diet, and time. It also underpins the Natural Language Interaction, allowing for a hands-free, conversational interface where users can ask complex, open-ended questions during cooking (e.g., "Can I use smoked paprika instead of sweet?") and receive accurate, contextual guidance. And most importantly, the LLM allows the system to interpret and act on language commands, such as "Make a dinner that's gluten-free, uses up the leftover chicken, and feels like comfort food". 

## Scenarios for Chefing
#### 1. Eric
- Adjusting to cooking skill levels to provide simpler recipes for beginners so that they don’t spend too much time and lose interest
- Retrieval from various data sources using RAG to get higher-quality recommendations

#### 2. Joy
- Creating a manageable recipe using only the ingredients the user has in their fridge 
- Generating a five day meal prepping plan that focuses on some diet goal like losing weight or bulking up

#### 3. Parsa
- Make the most of whatever tools you’ve got (e.g. air fryer, rice cooker). Chefing tweaks the recipe and timing so it still comes out delicious.
- Notices what’s about to expire and gives you ideas to use it up. Less waste, more flavor, smarter cooking.
