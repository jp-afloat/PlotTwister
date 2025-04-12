from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from uuid import uuid4
import json
import os

from src.supabase_client import supabase as sb
from src.azure_openai_client import generate_initial_game
from fastapi import HTTPException
from src.azure_openai_client import generate_game_images

# Load environment variables
load_dotenv()

# === Pydantic Models ===
class StartGameRequest(BaseModel):
    user_id: str
    seed_prompt: str

class MoveRequest(BaseModel):
    user_id: str
    game_id: str
    direction: str

class ImageGenRequest(BaseModel):
    game_id: str
    seed_prompt: str    

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "supabase_url": os.getenv("SUPABASE_URL"),
        "google_api_key_present": bool(os.getenv("GEMINI_API_KEY")),
    }




# === Game Start ===
@app.post("/start_game")
async def start_game(req: StartGameRequest):
    game_id = str(uuid4())
    ai_response = await generate_initial_game(req.seed_prompt)
    print(ai_response)
    game_data = ai_response
    print("win condition")
    print(game_data["win_condition"])
    print(game_data["lose_conditions"])

    # Store game
    sb.table("games").insert({
        "id": game_id,
        "user_id": req.user_id,
        "seed_prompt": req.seed_prompt,
        "win_condition": game_data["win_condition"],
        "lose_conditions": game_data["lose_conditions"]
    }).execute()

    # Store characters
    for char in game_data["characters"]:
        sb.table("characters").insert({
            "id": str(uuid4()),
            "game_id": game_id,
            "name": char["name"],
            "backstory": char["backstory"],
            "motivation": char["motivation"],
            "location_x": char["location"][0],
            "location_y": char["location"][1],
        }).execute()

    # Store first location
    sb.table("locations").insert({
        "id": str(uuid4()),
        "game_id": game_id,
        "x": 0,
        "y": 0,
        "description": game_data["intro"],
        "image_url": "https://via.placeholder.com/512",
        "events": [],
        "characters": [],
        "visited": True
    }).execute()

    # Store player state
    sb.table("player_state").insert({
        "id": str(uuid4()),
        "user_id": req.user_id,
        "game_id": game_id,
        "pos_x": 0,
        "pos_y": 0,
        "history": []
    }).execute()

    return {
        "game_id": game_id,
        "intro": game_data["intro"],
        "image_url": "https://via.placeholder.com/512",
        "start_position": {"x": 0, "y": 0}
    }


@app.post("/generate_game_images")
async def generate_images_for_game(req: ImageGenRequest):
    try:
        images = await generate_game_images(req.seed_prompt, req.game_id)

        # Store each image entry into `map_images` table
        for img in images:
            sb.table("map_images").insert({
                "id": str(uuid4()),
                "game_id": req.game_id,
                "prompt": img["prompt"],
                "image_url": img["image_url"],
                "grid_x": img["grid_position"]["x"],
                "grid_y": img["grid_position"]["y"],
                "location": img.get("location", None)  # Optional if added
            }).execute()

        return {
            "status": "success",
            "game_id": req.game_id,
            "images": images
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



