import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
import base64
import requests
from io import BytesIO
from uuid import uuid4
from src.supabase_client import supabase as sb
load_dotenv()
import asyncio
from uuid import uuid4
from dotenv import load_dotenv


AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")

AZURE_ENDPOINT_DALLE = os.getenv("AZURE_OPENAI_DALLE_ENDPOINT")
AZURE_API_KEY_DALLE = os.getenv("AZURE_OPENAI_DALLE_API_KEY")
AZURE_API_VERSION_DALLE = os.getenv("AZURE_OPENAI_DALLE_API_VERSION", "2023-12-01-preview")
AZURE_DALLE_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DALLE_DEPLOYMENT_NAME")

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

async def generate_game_images(seed_prompt: str, game_id: str) -> list:
    # Step 1: Ask GPT to generate 9 location-based image prompts
    gpt_prompt = f"""
    Based on this world-building prompt: "{seed_prompt}", generate 9 short and vivid image prompts, each describing a unique location in the world.

    These should be visually distinct and immersive, suitable for DALL·E 3 to render. Return a JSON list of prompts.
    """

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": gpt_prompt}],
        temperature=0.8,
        response_format={ "type": "json_object" },
    )

    image_data = json.loads(response.choices[0].message.content.strip())

    # Handle structured response: {"prompts": [{"description": "...", "location": "..."}, ...]}
    if "prompts" not in image_data or len(image_data["prompts"]) != 9:
        raise ValueError("Expected 9 image prompts in 'prompts' field from GPT.")

    image_prompts = [item["description"] for item in image_data["prompts"]]

    # Step 2: Generate image for each prompt
    dalle_client = AzureOpenAI(
        api_key=AZURE_API_KEY_DALLE,
        api_version=AZURE_API_VERSION_DALLE,
        azure_endpoint=AZURE_ENDPOINT_DALLE,
    )

    results = []
    grid_positions = [(x, y) for y in range(3) for x in range(3)]  # (0,0) to (2,2)

    for i, prompt in enumerate(image_prompts):
        # Generate image from DALL·E
        dalle_response = dalle_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        image_url = dalle_response.data[0].url

        # Download image
        img_data = requests.get(image_url).content
        filename = f"{uuid4()}.png"

        # Upload to Supabase Storage
        path = f"games/{game_id}/{filename}"
        sb.storage.from_("game-images").upload(path, img_data, {"content-type": "image/png"})

        # Get public URL
        public_url = sb.storage.from_("game-images").get_public_url(path)

        results.append({
            "prompt": prompt,
            "image_url": public_url,
            "grid_position": {"x": grid_positions[i][0], "y": grid_positions[i][1]}
        })

    return results

if __name__ == "__main__":
    load_dotenv()

    # === Test 1: Basic text completion ===
    test_text_prompt = "tell me a joke."
    try:
        reply = ask_azure_openai(test_text_prompt)
        print("\n✅ Azure OpenAI (Text Completion) Response:\n")
        print(reply)
    except Exception as e:
        print("\n❌ Error communicating with Azure OpenAI (Text):")
        print(e)

    # === Test 2: Generate game image grid ===
    test_seed_prompt = "In the mystical realm of Eldoria, ancient ruins hum with forgotten magic and airships patrol the skies."
    test_game_id = str(uuid4())

    print(f"\n🧪 Generating image grid for test game: {test_game_id}")

    try:
        results = asyncio.run(generate_game_images(test_seed_prompt, test_game_id))
        print("\n✅ DALL·E Image Grid Generation Results:\n")
        print(json.dumps(results, indent=2))
    except Exception as e:
        print("\n❌ Error during image generation:")
        print(e)
