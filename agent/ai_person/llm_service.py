from anthropic import Anthropic
import ollama
import os
import re
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key and LLM choice from environment variables
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
llm_choice = os.getenv("LLM_CHOICE", "anthropic")

def sanitize_llm_response(raw_response: str):
    """
    Sanitize LLM response to handle newlines in JSON strings.
    Only fixes unescaped newlines inside quoted strings.
    """
    if not raw_response or not isinstance(raw_response, str):
        return ""
    
    print(f"Original response length: {len(raw_response)}")
    print(f"Original response: {raw_response}")
    
    # Fix unescaped newlines inside quoted strings
    def fix_string_newlines(match):
        content = match.group(0)
        # Replace unescaped newlines with literal \n inside quoted strings
        fixed = content.replace('\n', '\\n')
        return fixed

    print(f"Sanitized response length: {len(sanitized)}")
    print(f"Sanitized response: {sanitized}")
    
    return sanitized

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