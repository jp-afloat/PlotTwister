import os
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()


AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

#AZURE_ENDPOINT = "https://stenindata-openai-1.openai.azure.com/"
#model_name = "gpt-4o-mini"
#DEPLOYMENT_NAME = "gpt-4o-mini"
#API_VERSION = "2024-12-01-preview"
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