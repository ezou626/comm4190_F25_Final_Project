from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import os
import shutil
import uuid
import json
from lib import (
    generate_recipe_from_fridge,
    generate_recipe,
    detect_recipe_request,
    generate_conversation_title,
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
    
    # Conversations table
    c.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        title TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Chat history table (now linked to conversations)
    c.execute("""
    CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        user_id TEXT NOT NULL,
        message TEXT NOT NULL,
        response TEXT NOT NULL,
        has_image BOOLEAN DEFAULT 0,
        image_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
    )
    """)
    
    # Add conversation_id column if it doesn't exist (migration)
    try:
        # Check if column exists
        c.execute("PRAGMA table_info(chat)")
        columns = [row[1] for row in c.fetchall()]
        if 'conversation_id' not in columns:
            c.execute("ALTER TABLE chat ADD COLUMN conversation_id INTEGER")
            # Migrate existing messages to a default conversation
            c.execute("""
                INSERT INTO conversations (user_id, title, created_at, updated_at)
                SELECT DISTINCT user_id, 'Chat 1', MIN(created_at), MAX(created_at)
                FROM chat
                WHERE conversation_id IS NULL
                GROUP BY user_id
            """)
            c.execute("""
                UPDATE chat 
                SET conversation_id = (SELECT id FROM conversations WHERE user_id = chat.user_id LIMIT 1)
                WHERE conversation_id IS NULL
            """)
    except sqlite3.OperationalError:
        pass  # Column already exists or migration failed
    
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

# Define static directory path
static_dir = os.path.join(os.path.dirname(__file__), "static")

# Root route - serve frontend if available, otherwise return API info
@app.get("/")
async def root():
    if os.path.exists(static_dir):
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
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


class ProfileUpdate(BaseModel):
    """Direct profile update request."""
    long_term_instructions: List[str]
    long_term_preferences: List[str]
    long_term_restrictions: List[str]
    long_term_situation: List[str]


@app.put("/api/profile")
def update_profile_directly(profile_update: ProfileUpdate):
    """
    Directly update user profile with provided data.
    This allows users to edit their profile manually.
    """
    try:
        update_user_profile(
            USER_ID,
            profile_update.long_term_instructions,
            profile_update.long_term_preferences,
            profile_update.long_term_restrictions,
            profile_update.long_term_situation,
        )
        
        return JSONResponse({
            "success": True,
            "profile": {
                "long_term_instructions": profile_update.long_term_instructions,
                "long_term_preferences": profile_update.long_term_preferences,
                "long_term_restrictions": profile_update.long_term_restrictions,
                "long_term_situation": profile_update.long_term_situation,
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(
    user_message: str = Form(...),
    fridge_image: Optional[UploadFile] = File(None),
    conversation_id: Optional[str] = Form(None),
):
    """
    Main chat endpoint. Handles recipe generation and information parsing.
    
    - If fridge_image is provided: generates a recipe based on fridge contents
    - If no image but recipe requested: generates a recipe based on preferences
    - Otherwise: parses new information from user message
    
    Automatically retrieves relevant long-term data using embeddings.
    Updates long-term profile if new persistent information is detected.
    Creates a new conversation if conversation_id is not provided.
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
        
        # Check if user is requesting a recipe (using LLM to detect implied requests)
        is_recipe_request = detect_recipe_request(user_message)
        
        # Process based on whether image is provided or recipe is requested
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
        elif is_recipe_request:
            # Generate recipe without image
            result = generate_recipe(
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
        
        # Get or create conversation
        conn = get_db()
        c = conn.cursor()
        
        conv_id = None
        if conversation_id:
            try:
                conv_id = int(conversation_id)
                # Verify conversation exists and belongs to user
                c.execute("SELECT id FROM conversations WHERE id = ? AND user_id = ?", (conv_id, USER_ID))
                if not c.fetchone():
                    raise HTTPException(status_code=404, detail="Conversation not found")
            except (ValueError, TypeError):
                conv_id = None
        
        if not conv_id:
            # Create new conversation with LLM-generated title
            title = generate_conversation_title(user_message)
            c.execute(
                """
                INSERT INTO conversations (user_id, title, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (USER_ID, title),
            )
            conv_id = c.lastrowid
        
        # Check if this is the first message and title needs to be generated
        c.execute(
            "SELECT title, (SELECT COUNT(*) FROM chat WHERE conversation_id = ?) as msg_count FROM conversations WHERE id = ?",
            (conv_id, conv_id)
        )
        row = c.fetchone()
        if row and row[1] == 0 and (not row[0] or row[0] == "New Chat"):
            # First message - generate a proper title
            new_title = generate_conversation_title(user_message)
            c.execute(
                "UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_title, conv_id)
            )
        else:
            # Just update the timestamp
            c.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conv_id,)
            )
        
        # Store chat message in database
        c.execute(
            """
            INSERT INTO chat (conversation_id, user_id, message, response, has_image, image_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                conv_id,
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


@app.get("/api/conversations")
def get_conversations():
    """
    Get all conversations for the user.
    Returns conversations ordered by most recently updated.
    """
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """
        SELECT id, title, created_at, updated_at,
               (SELECT COUNT(*) FROM chat WHERE conversation_id = conversations.id) as message_count
        FROM conversations 
        WHERE user_id = ? 
        ORDER BY updated_at DESC
        """,
        (USER_ID,),
    )
    rows = c.fetchall()
    conn.close()
    
    conversations = []
    for row in rows:
        conversations.append({
            "id": row["id"],
            "title": row["title"] or f"Chat {row['id']}",
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "message_count": row["message_count"],
        })
    
    return JSONResponse(conversations)


@app.post("/api/conversations")
def create_conversation():
    """
    Create a new conversation.
    """
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO conversations (user_id, title, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        """,
        (USER_ID, "New Chat"),
    )
    conversation_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return JSONResponse({
        "id": conversation_id,
        "title": "New Chat",
        "created_at": None,
        "updated_at": None,
        "message_count": 0,
    })


@app.get("/api/conversations/{conversation_id}/messages")
def get_conversation_messages(conversation_id: int, limit: int = 100):
    """
    Get messages for a specific conversation.
    Returns messages in chronological order (oldest first).
    """
    conn = get_db()
    c = conn.cursor()
    
    # Verify conversation exists and belongs to user
    c.execute("SELECT id FROM conversations WHERE id = ? AND user_id = ?", (conversation_id, USER_ID))
    if not c.fetchone():
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    c.execute(
        """
        SELECT id, message, response, has_image, image_path, created_at
        FROM chat 
        WHERE conversation_id = ? AND user_id = ?
        ORDER BY created_at ASC 
        LIMIT ?
        """,
        (conversation_id, USER_ID, limit),
    )
    rows = c.fetchall()
    conn.close()
    
    messages = []
    for row in rows:
        messages.append({
            "id": row["id"],
            "message": row["message"],
            "response": json.loads(row["response"]),
            "has_image": bool(row["has_image"]),
            "image_path": row["image_path"],
            "created_at": row["created_at"],
        })
    
    return JSONResponse(messages)


@app.get("/api/history")
def get_history(limit: int = 50):
    """
    Get chat history for the user (deprecated - use /api/conversations/{id}/messages instead).
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


@app.post("/api/reset")
def reset_demo():
    """
    Reset the demo by clearing all database tables.
    This will delete all chat history, user profile, and feedback data.
    """
    try:
        conn = get_db()
        c = conn.cursor()
        
        # Clear all tables (CASCADE will handle chat messages)
        c.execute("DELETE FROM conversations")
        c.execute("DELETE FROM chat")
        c.execute("DELETE FROM user_profile")
        c.execute("DELETE FROM recipe_feedback")
        
        conn.commit()
        conn.close()
        
        return JSONResponse({
            "success": True,
            "message": "Demo reset successfully. All data has been cleared."
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset demo: {str(e)}")


# Serve uploaded images
@app.get("/uploads/{filename:path}")
async def serve_upload(filename: str):
    """Serve uploaded fridge images."""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")


# Serve static files from the static directory (static_dir already defined above)
if os.path.exists(static_dir):
    # Mount static assets (JS, CSS, images, etc.) - this must be before the catch-all route
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    # Serve static files like vite.svg
    @app.get("/vite.svg")
    async def serve_vite_svg():
        svg_path = os.path.join(static_dir, "vite.svg")
        if os.path.exists(svg_path):
            return FileResponse(svg_path)
        raise HTTPException(status_code=404)
    
    # Serve index.html for all non-API routes (SPA routing)
    # This must be the LAST route to catch all unmatched paths
    # FastAPI matches routes in order, so more specific routes above will match first
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Explicitly exclude API routes, uploads, assets, and vite.svg
        # These should have been handled by more specific routes above
        if (full_path.startswith("api/") or 
            full_path.startswith("uploads/") or 
            full_path.startswith("assets/") or
            full_path == "vite.svg" or
            full_path == ""):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for SPA routing (any other path)
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Frontend not built")
