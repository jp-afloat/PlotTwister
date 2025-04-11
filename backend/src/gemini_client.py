import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-flash-2.0")

def ask_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text
