import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()


AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")

client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version=API_VERSION,
    azure_endpoint=AZURE_ENDPOINT,
)

def ask_azure_openai(prompt: str) -> str:
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content


async def generate_initial_game(seed_prompt: str) -> dict:
    prompt = f"""
    You are a world-building AI. Create:
    1. An intro scene
    2. A win condition
    3. Two lose conditions
    4. Three characters (name, backstory, motivation, location as x,y)

    Based on this prompt: "{seed_prompt}"

    Return only raw JSON:
    {{
      "intro": "...",
      "win_condition": "...",
      "lose_conditions": ["...", "..."],
      "characters": [
        {{
          "name": "...",
          "backstory": "...",
          "motivation": "...",
          "location": [x, y]
        }}
      ]
    }}
    """

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        response_format={ "type": "json_object" },

    )

    # This is the raw text the model returns
    raw_output = response.choices[0].message.content.strip()

    # Now force it to be valid JSON
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        import re
        from ast import literal_eval

        # Fallback fix: try to extract JSON block
        match = re.search(r'\{.*\}', raw_output, re.DOTALL)
        if match:
            cleaned = match.group(0)
            return json.loads(cleaned)

        raise ValueError("Could not parse model output into JSON")



# ✅ Test directly
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    test_prompt = "tell me a joke."
    try:
        reply = ask_azure_openai(test_prompt)
        print("\n✅ Azure OpenAI Response:\n")
        print(reply)
    except Exception as e:
        print("\n❌ Error communicating with Azure OpenAI:")
        print(e)