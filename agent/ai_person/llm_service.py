from anthropic import Anthropic
import ollama
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key and LLM choice from environment variables
anthorpic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
llm_choice = os.getenv("LLM_CHOICE", "anthropic")

def get_response_from_llm(prompt: str) -> str:
    if llm_choice == 'anthropic':
        return get_response_from_anthropic(prompt=prompt)
    elif llm_choice == 'ollama':
        return get_response_from_ollama(prompt=prompt)
    elif llm_choice == 'openai':
        return get_response_from_openai(prompt=prompt)

def get_response_from_anthropic(prompt: str) -> str:
    try:
        print("prompt:\n" + prompt)
        # Call Claude API
        message = anthorpic_client.messages.create(
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
        # Null check for message and its content
        response_text = None
        if message and hasattr(message, 'content') and message.content and isinstance(message.content, list) and len(message.content) > 0 and hasattr(message.content[0], 'text'):
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
        # Null check for response and its structure
        response_text = None
        if response and 'message' in response and response['message'] and 'content' in response['message']:
            response_text = response['message']['content']
        else:
            print("Warning: No valid response from Ollama LLM.")
            response_text = "[No valid response from LLM]"
        print("response_text:\n" + response_text)
        return response_text
    except Exception as e:
        print(e)

def get_response_from_openai(prompt: str) -> str:
    try:
        print("prompt:\n" + prompt)
        
        # Call OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        print("llm response: \n")
        print(response)
        
        # Extract response text with null checks
        response_text = None
        if (
            response
            and hasattr(response, "choices")
            and isinstance(response.choices, list)
            and len(response.choices) > 0
            and hasattr(response.choices[0], "message")
            and response.choices[0].message
            and hasattr(response.choices[0].message, "content")
            and response.choices[0].message.content
        ):
            response_text = response.choices[0].message.content
        else:
            print("Warning: No valid response from OpenAI LLM.")
            response_text = "[No valid response from LLM]"
        
        return response_text
        
    except Exception as e:
        print(e)
        return f"[Error: {str(e)}]"