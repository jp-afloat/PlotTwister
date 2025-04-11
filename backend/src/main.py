from fastapi import FastAPI
from dotenv import load_dotenv
#from src.supabase_client import fetch_data_from_table
#from src.llama_index_setup import build_index_from_docs
#from src.gemini_client import ask_gemini
import os
from src.azure_openai_client import ask_azure_openai

# Load environment variables
load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "supabase_url": os.getenv("SUPABASE_URL"),
        "google_api_key_present": bool(os.getenv("GEMINI_API_KEY")),
    }

'''
@app.get("/ask")
def ask_question(
    question: str = "What can you tell me about this data?",
    model_provider: str = "azure",  # or "azure"
):
    data = fetch_data_from_table("your_table_name_here")
    if not data:
        return {"error": "No data found in Supabase."}

    query_engine = build_index_from_docs(data)
    result = query_engine.query(question)
    summary = str(result)

    if model_provider == "azure":
        response = ask_azure_openai(f"Here's a summary of some data: {summary}\nCan you give more insights?")
    elif model_provider == "google":
        response = ask_gemini(f"Here's a summary of some data: {summary}\nCan you give more insights?")
    else:
        return {"error": f"Unknown model provider '{model_provider}'"}

    return {
        "llamaindex_summary": summary,
        f"{model_provider}_insights": response
    }
    '''
