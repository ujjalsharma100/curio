from anthropic import Anthropic
import ollama
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key and LLM choice from environment variables
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
llm_choice = os.getenv("LLM_CHOICE", "anthropic")

def get_response_from_llm(prompt: str) -> str:
    if llm_choice == 'anthropic':
        return get_response_from_anthropic(prompt=prompt)
    elif llm_choice == 'ollama':
        return get_response_from_ollama(prompt=prompt)

def get_response_from_anthropic(prompt: str) -> str:
    try:
        print("prompt:\n" + prompt)
        # Call Claude API
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,  # Increased for multiple responses
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        print("llm response: \n")
        print(message)
        response_text = message.content[0].text.strip()
        print("response_text:\n" + response_text)
        return response_text

    except Exception as e:
        print(e)

def get_response_from_ollama(prompt: str) -> str:
    try:
        print("prompt:\n" + prompt)
        
        response = ollama.chat(model="llama3.1", messages=[{"role": "user", "content": prompt}])
        
        print("llm response: \n")
        print(response)
        response_text = response['message']['content']
        print("response_text:\n" + response_text)
        return response_text
    except Exception as e:
        print(e)