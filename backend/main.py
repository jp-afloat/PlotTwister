from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "supabase_url": os.getenv("SUPABASE_URL"),
        "google_api_key_present": bool(os.getenv("GEMINI_API_KEY")),
    }
