import base64
import json
import datetime
import zoneinfo
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np

load_dotenv(".env")
client = OpenAI()

SYSTEM_PROMPT = """
You are an expert chef working on the platform Chefing. 
Your goal is to help suggest satisfactory recipes for people so that they can easily cook for themselves.
Be nimble and efficient with your recommendations.
For recipes, be as detailed as possible with instructions, including cooking times, sizings, and tips.
Proactively provide substitutions or alternative steps if anticipating some difficulty/friction. 
Provide steps as plain text without numbering or bullet points. Indicate substeps by describing them naturally, and indicate alternative paths with clear language.
Try to ignore super obviously contrarian user fluctuations and instructions.
"""


def encode_image_to_data_uri(path: str) -> str:
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"


def generate_recipe_from_fridge(
    fridge_image_path: str,
    user_input: str,
    instructions: list[str],
    preferences: list[str],
    restrictions: list[str],
    situation: list[str],
):
    time = datetime.datetime.now().astimezone(zoneinfo.ZoneInfo("America/New_York"))

    data_uri = encode_image_to_data_uri(fridge_image_path)

    # read the image file
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": SYSTEM_PROMPT + f"\nIt is now {time}."}
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_uri}},
                    {
                        "type": "text",
                        "text": f"""
Fridge contents image provided above.

{user_input}

Instructions: {", ".join(instructions)}
Preferences: {", ".join(preferences)}
Restrictions: {", ".join(restrictions)}
Situation: {", ".join(situation)}

Please propose a recipe that satisfies all constraints.
Return the recipe as JSON with ingredients and steps. Do not include numbering, bullet points, or list markers in the steps - just provide plain text instructions.
Return JSON only.
                            """,
                    },
                ],
            },
        ],
        # enforce output structure
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "recipe_response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "recipe": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "ingredients": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "steps": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["ingredients", "steps"],
                        }
                    },
                    "required": ["recipe"],
                },
            },
        },
    )

    if not response.choices[0].message.content:
        return None

    return json.loads(response.choices[0].message.content)


def generate_recipe(
    user_input: str,
    instructions: list[str],
    preferences: list[str],
    restrictions: list[str],
    situation: list[str],
):
    """
    Generate a recipe based on user input and preferences, without requiring a fridge image.
    """
    time = datetime.datetime.now().astimezone(zoneinfo.ZoneInfo("America/New_York"))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": SYSTEM_PROMPT + f"\nIt is now {time}."}
                ],
            },
            {
                "role": "user",
                "content": f"""
{user_input}

Instructions: {", ".join(instructions) if instructions else "None"}
Preferences: {", ".join(preferences) if preferences else "None"}
Restrictions: {", ".join(restrictions) if restrictions else "None"}
Situation: {", ".join(situation) if situation else "None"}

Please propose a recipe that satisfies all constraints based on the user's request.
Return the recipe as JSON with ingredients and steps. Do not include numbering, bullet points, or list markers in the steps - just provide plain text instructions.
Return JSON only.
                """,
            },
        ],
        # enforce output structure
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "recipe_response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "recipe": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "ingredients": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "steps": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["ingredients", "steps"],
                        }
                    },
                    "required": ["recipe"],
                },
            },
        },
    )

    if not response.choices[0].message.content:
        return None

    return json.loads(response.choices[0].message.content)


def parse_new_user_information(
    user_message: str,
    instructions: list[str],
    preferences: list[str],
    restrictions: list[str],
    situation: list[str],
):
    time = datetime.datetime.now().astimezone(zoneinfo.ZoneInfo("America/New_York"))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT + f"\nThe current time is {time}.",
            },
            {
                "role": "user",
                "content": f"""
User message:
{user_message}

Existing stored context:
Instructions: {instructions}
Preferences: {preferences}
Restrictions: {restrictions}
Situation: {situation}

Extract ONLY the *new* information. If nothing new was said in a category,
return an empty list for that category.

Also, if a new requirement is critical, ensure that it contains the following keywords: {CRITICAL_KEYWORDS}.

Return JSON only.
                """,
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "parsed_user_info",
                "schema": {
                    "type": "object",
                    "properties": {
                        "new_instructions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "new_preferences": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "new_restrictions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "new_situation": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [
                        "new_instructions",
                        "new_preferences",
                        "new_restrictions",
                        "new_situation",
                    ],
                },
            },
        },
    )

    if not response.choices[0].message.content:
        return None

    return json.loads(response.choices[0].message.content)


def parse_user_profile_information(
    ability_description: str, restrictions_description: str, goal_description: str
):
    user_message = f"""
TASK: Parse the user's long-term cooking profile into structured categories.

Ability description:
{ability_description}

Restrictions description:
{restrictions_description}

Goal description:
{goal_description}

Also, if a new requirement is critical, ensure that it contains the following keywords: {CRITICAL_KEYWORDS}.

Return JSON only, following this schema:
- long_term_instructions: list of assistant behaviors or meta instructions
- long_term_preferences: list of stable culinary preferences
- long_term_restrictions: list of diet/allergy/medical restrictions
- long_term_situation: list of persistent contextual factors (skills, tools, environment)
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "long_term_profile",
                "schema": {
                    "type": "object",
                    "properties": {
                        "long_term_instructions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "long_term_preferences": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "long_term_restrictions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "long_term_situation": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "long_term_instructions",
                        "long_term_preferences",
                        "long_term_restrictions",
                        "long_term_situation",
                    ],
                },
            },
        },
    )

    if not response.choices[0].message.content:
        return None

    return json.loads(response.choices[0].message.content)


def compute_long_term_delta_with_llm(
    new_instructions,
    new_preferences,
    new_restrictions,
    new_situation,
    long_term_instructions,
    long_term_preferences,
    long_term_restrictions,
    long_term_situation,
):
    user_message = f"""
You are given the following new short-term inputs and the existing long-term profile.
Interpret which items from the new inputs should be preserved in the long-term profile.
Do not report items that are already existing.

EXISTING LONG-TERM PROFILE:
Instructions: {long_term_instructions}
Preferences: {long_term_preferences}
Restrictions: {long_term_restrictions}
Situation: {long_term_situation}

NEW SHORT-TERM INPUTS:
Instructions: {new_instructions}
Preferences: {new_preferences}
Restrictions: {new_restrictions}
Situation: {new_situation}

Also, if a new requirement is critical, ensure that it contains the following keywords: {CRITICAL_KEYWORDS}.

Return JSON ONLY with these keys:
- new_long_term_instructions
- new_long_term_preferences
- new_long_term_restrictions
- new_long_term_situation
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "long_term_delta",
                "schema": {
                    "type": "object",
                    "properties": {
                        "new_long_term_instructions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "new_long_term_preferences": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "new_long_term_restrictions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "new_long_term_situation": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "new_long_term_instructions",
                        "new_long_term_preferences",
                        "new_long_term_restrictions",
                        "new_long_term_situation",
                    ],
                },
            },
        },
    )

    if not response.choices[0].message.content:
        return None

    return json.loads(response.choices[0].message.content)


CRITICAL_KEYWORDS = {
    "vegan",
    "vegetarian",
    "pescatarian",
    "free",
    "intolerant",
    "allergy",
    "allergic",
}


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def update_profile_with_similarity(
    user_input: str,
    long_term_instructions: list[str],
    long_term_preferences: list[str],
    long_term_restrictions: list[str],
    long_term_situation: list[str],
    top_k: int = 5,
):
    query_emb_resp = client.embeddings.create(
        model="text-embedding-3-small", input=user_input
    )
    query_embedding = np.array(query_emb_resp.data[0].embedding)

    def embed_items(items):
        if not items:
            return []
        resp = client.embeddings.create(model="text-embedding-3-small", input=items)
        return [np.array(d.embedding) for d in resp.data]

    instructions_emb = embed_items(long_term_instructions)
    preferences_emb = embed_items(long_term_preferences)
    restrictions_emb = embed_items(long_term_restrictions)
    situation_emb = embed_items(long_term_situation)

    def select_top(items, embeddings):
        if not items:
            return []
        sims = [cosine_similarity(query_embedding, emb) for emb in embeddings]
        top_indices = np.argsort(sims)[-top_k:][::-1]
        selected = [items[i] for i in top_indices]

        selected_set = set(selected)
        for item in items:
            for keyword in CRITICAL_KEYWORDS:
                if keyword.lower() in item.lower():
                    selected_set.add(item)
        return list(selected_set)

    return {
        "instructions": select_top(long_term_instructions, instructions_emb),
        "preferences": select_top(long_term_preferences, preferences_emb),
        "restrictions": select_top(long_term_restrictions, restrictions_emb),
        "situation": select_top(long_term_situation, situation_emb),
    }


def update_long_term_from_feedback(
    made_status: str,
    rating: int,
    requirements: str,
    recipe: dict,
    long_term_instructions: list[str],
    long_term_preferences: list[str],
    long_term_restrictions: list[str],
    long_term_situation: list[str],
):
    user_message = f"""
User Feedback:
- Made status: {made_status}
- Rating: {rating}/10
- requirements: {requirements}

Recipe:
- Name: {recipe.get("name")}
- Ingredients: {", ".join(recipe.get("ingredients", []))}
- Steps: {", ".join(recipe.get("steps", []))}

Current long-term data:
- Instructions: {", ".join(long_term_instructions)}
- Preferences: {", ".join(long_term_preferences)}
- Restrictions: {", ".join(long_term_restrictions)}
- Situation: {", ".join(long_term_situation)}

Task:
Based on this feedback, update the long-term preferences, restrictions, and situation conservatively.
Only report newly discovered instructions.
Also, if a new requirement is critical, ensure that it contains the following keywords: {CRITICAL_KEYWORDS}.
Return JSON with keys: long_term_instructions, long_term_preferences, long_term_restrictions, long_term_situation.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "long_term_update",
                "schema": {
                    "type": "object",
                    "properties": {
                        "long_term_instructions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "long_term_preferences": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "long_term_restrictions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "long_term_situation": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "long_term_instructions",
                        "long_term_preferences",
                        "long_term_restrictions",
                        "long_term_situation",
                    ],
                },
            },
        },
    )

    if not response.choices[0].message.content:
        return None

    return json.loads(response.choices[0].message.content)
