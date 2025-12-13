from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import os
import shutil
import uuid
import json
from lib import (
    generate_recipe_from_fridge,
    parse_new_user_information,
    parse_user_profile_information,
    compute_long_term_delta_with_llm,
    update_profile_with_similarity,
    update_long_term_from_feedback,
)

DB_PATH = "database.db"
UPLOAD_DIR = "uploads"
USER_ID = "demo-user"  # Single user demonstrator

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Chefing API", version="1.0.0")

# Allow CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models ---
class ProfileRequest(BaseModel):
    ability_description: str
    restrictions_description: str
    goal_description: str


class FeedbackRequest(BaseModel):
    made_status: str
    rating: int
    comments: str
    recipe: dict


# --- DB SETUP ---
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Chat history table
    c.execute("""
    CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        message TEXT NOT NULL,
        response TEXT NOT NULL,
        has_image BOOLEAN DEFAULT 0,
        image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # User profile table (long-term data)
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        user_id TEXT PRIMARY KEY,
        long_term_instructions TEXT DEFAULT '[]',
        long_term_preferences TEXT DEFAULT '[]',
        long_term_restrictions TEXT DEFAULT '[]',
        long_term_situation TEXT DEFAULT '[]',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Recipe feedback table
    c.execute("""
    CREATE TABLE IF NOT EXISTS recipe_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        recipe_name TEXT,
        recipe_data TEXT,
        made_status TEXT,
        rating INTEGER,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()


init_db()


# --- Helper Functions ---
def get_user_profile(user_id: str = USER_ID) -> dict:
    """Get user profile from database, return default if not exists."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "long_term_instructions": json.loads(row["long_term_instructions"]),
            "long_term_preferences": json.loads(row["long_term_preferences"]),
            "long_term_restrictions": json.loads(row["long_term_restrictions"]),
            "long_term_situation": json.loads(row["long_term_situation"]),
        }
    else:
        # Return empty profile
        return {
            "long_term_instructions": [],
            "long_term_preferences": [],
            "long_term_restrictions": [],
            "long_term_situation": [],
        }


def update_user_profile(
    user_id: str,
    long_term_instructions: List[str],
    long_term_preferences: List[str],
    long_term_restrictions: List[str],
    long_term_situation: List[str],
):
    """Update or create user profile in database."""
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """
        INSERT OR REPLACE INTO user_profile 
        (user_id, long_term_instructions, long_term_preferences, 
         long_term_restrictions, long_term_situation, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (
            user_id,
            json.dumps(long_term_instructions),
            json.dumps(long_term_preferences),
            json.dumps(long_term_restrictions),
            json.dumps(long_term_situation),
        ),
    )
    conn.commit()
    conn.close()


# --- API ENDPOINTS ---

@app.get("/")
def root():
    return {"message": "Chefing API", "version": "1.0.0"}


@app.post("/api/profile")
async def create_or_update_profile(profile: ProfileRequest):
    """
    Initialize or update user profile from form data.
    This parses the user's ability, restrictions, and goals into structured long-term data.
    """
    try:
        # Parse profile information
        parsed = parse_user_profile_information(
            profile.ability_description,
            profile.restrictions_description,
            profile.goal_description,
        )
        
        if not parsed:
            raise HTTPException(status_code=500, detail="Failed to parse profile")
        
        # Update database
        update_user_profile(
            USER_ID,
            parsed["long_term_instructions"],
            parsed["long_term_preferences"],
            parsed["long_term_restrictions"],
            parsed["long_term_situation"],
        )
        
        return JSONResponse({
            "success": True,
            "profile": parsed,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profile")
def get_profile():
    """Get current user profile (long-term data)."""
    profile = get_user_profile(USER_ID)
    return JSONResponse(profile)


@app.post("/api/chat")
async def chat(
    user_message: str = Form(...),
    fridge_image: Optional[UploadFile] = File(None),
):
    """
    Main chat endpoint. Handles both recipe generation (with fridge image) 
    and information parsing (without image).
    
    - If fridge_image is provided: generates a recipe based on fridge contents
    - If no image: parses new information from user message
    
    Automatically retrieves relevant long-term data using embeddings.
    Updates long-term profile if new persistent information is detected.
    """
    try:
        # Get current user profile
        profile = get_user_profile(USER_ID)
        
        # Retrieve relevant context using embeddings
        relevant_context = update_profile_with_similarity(
            user_message,
            profile["long_term_instructions"],
            profile["long_term_preferences"],
            profile["long_term_restrictions"],
            profile["long_term_situation"],
            top_k=5,
        )
        
        # Save image if provided
        image_path = None
        if fridge_image:
            ext = os.path.splitext(fridge_image.filename)[-1] or ".jpg"
            image_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{ext}")
            with open(image_path, "wb") as f:
                shutil.copyfileobj(fridge_image.file, f)
        
        # Process based on whether image is provided
        if image_path:
            # Generate recipe from fridge
            result = generate_recipe_from_fridge(
                image_path,
                user_message,
                relevant_context["instructions"],
                relevant_context["preferences"],
                relevant_context["restrictions"],
                relevant_context["situation"],
            )
            
            if not result:
                raise HTTPException(status_code=500, detail="Failed to generate recipe")
            
            response_data = result
        else:
            # Parse new information from user message
            parsed = parse_new_user_information(
                user_message,
                relevant_context["instructions"],
                relevant_context["preferences"],
                relevant_context["restrictions"],
                relevant_context["situation"],
            )
            
            if not parsed:
                raise HTTPException(status_code=500, detail="Failed to parse user information")
            
            # Determine which new info should be long-term
            delta = compute_long_term_delta_with_llm(
                parsed["new_instructions"],
                parsed["new_preferences"],
                parsed["new_restrictions"],
                parsed["new_situation"],
                profile["long_term_instructions"],
                profile["long_term_preferences"],
                profile["long_term_restrictions"],
                profile["long_term_situation"],
            )
            
            if delta:
                # Update long-term profile
                new_instructions = profile["long_term_instructions"] + delta.get("new_long_term_instructions", [])
                new_preferences = profile["long_term_preferences"] + delta.get("new_long_term_preferences", [])
                new_restrictions = profile["long_term_restrictions"] + delta.get("new_long_term_restrictions", [])
                new_situation = profile["long_term_situation"] + delta.get("new_long_term_situation", [])
                
                update_user_profile(
                    USER_ID,
                    new_instructions,
                    new_preferences,
                    new_restrictions,
                    new_situation,
                )
            
            response_data = {
                "parsed_info": parsed,
                "long_term_updates": delta if delta else {},
            }
        
        # Store chat in database
        conn = get_db()
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO chat (user_id, message, response, has_image, image_path)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                USER_ID,
                user_message,
                json.dumps(response_data),
                1 if image_path else 0,
                image_path,
            ),
        )
        conn.commit()
        conn.close()
        
        return JSONResponse(response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit feedback on a recipe. This updates the long-term profile
    based on user feedback (rating, comments, made status).
    """
    try:
        # Get current profile
        profile = get_user_profile(USER_ID)
        
        # Update long-term data from feedback
        # Note: function expects 'requirements' parameter but we use 'comments'
        updated = update_long_term_from_feedback(
            feedback.made_status,
            feedback.rating,
            feedback.comments,  # passed as 'requirements' parameter
            feedback.recipe,
            profile["long_term_instructions"],
            profile["long_term_preferences"],
            profile["long_term_restrictions"],
            profile["long_term_situation"],
        )
        
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to process feedback")
        
        # Merge updates with existing profile
        new_instructions = profile["long_term_instructions"] + updated.get("long_term_instructions", [])
        new_preferences = profile["long_term_preferences"] + updated.get("long_term_preferences", [])
        new_restrictions = profile["long_term_restrictions"] + updated.get("long_term_restrictions", [])
        new_situation = profile["long_term_situation"] + updated.get("long_term_situation", [])
        
        # Update database
        update_user_profile(
            USER_ID,
            new_instructions,
            new_preferences,
            new_restrictions,
            new_situation,
        )
        
        # Store feedback in database
        conn = get_db()
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO recipe_feedback 
            (user_id, recipe_name, recipe_data, made_status, rating, comments)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                USER_ID,
                feedback.recipe.get("name", ""),
                json.dumps(feedback.recipe),
                feedback.made_status,
                feedback.rating,
                feedback.comments,
            ),
        )
        conn.commit()
        conn.close()
        
        return JSONResponse({
            "success": True,
            "updates": updated,
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
def get_history(limit: int = 50):
    """
    Get chat history for the user.
    Returns messages in reverse chronological order (newest first).
    """
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """
        SELECT id, message, response, has_image, image_path, created_at
        FROM chat 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
        """,
        (USER_ID, limit),
    )
    rows = c.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "id": row["id"],
            "message": row["message"],
            "response": json.loads(row["response"]),
            "has_image": bool(row["has_image"]),
            "image_path": row["image_path"],
            "created_at": row["created_at"],
        })
    
    return JSONResponse(history)


@app.get("/api/feedback/history")
def get_feedback_history(limit: int = 20):
    """Get feedback history for the user."""
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """
        SELECT id, recipe_name, recipe_data, made_status, rating, comments, created_at
        FROM recipe_feedback 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
        """,
        (USER_ID, limit),
    )
    rows = c.fetchall()
    conn.close()
    
    feedback = []
    for row in rows:
        feedback.append({
            "id": row["id"],
            "recipe_name": row["recipe_name"],
            "recipe": json.loads(row["recipe_data"]),
            "made_status": row["made_status"],
            "rating": row["rating"],
            "comments": row["comments"],
            "created_at": row["created_at"],
        })
    
    return JSONResponse(feedback)
