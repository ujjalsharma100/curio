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
    Sanitize LLM response to be ready for JSON parsing.
    Handles common issues like unescaped newlines, markdown formatting, etc.
    """
    if not raw_response or not isinstance(raw_response, str):
        return ""
    
    print(f"Original response length: {len(raw_response)}")
    print(f"Original response: {raw_response}")
    
    # Step 1: Remove any invalid control characters (like unescaped newlines in strings)
    # Only fix inside strings: This regex finds quoted strings and replaces internal newlines
    def fix_string_newlines(match):
        content = match.group(0)
        # Replace unescaped newlines with literal \n inside quoted strings
        fixed = content.replace('\n', '\\n')
        return fixed

    # Replace strings with escaped newlines
    sanitized = re.sub(r'\"(.*?)\"', fix_string_newlines, raw_response, flags=re.DOTALL)
    
    # Step 2: Remove markdown code blocks
    sanitized = re.sub(r'```json\s*', '', sanitized)
    sanitized = re.sub(r'```\s*$', '', sanitized)
    
    # Step 3: Remove any text before the first {
    first_brace = sanitized.find('{')
    if first_brace != -1:
        sanitized = sanitized[first_brace:]
    
    # Step 4: Remove any text after the last }
    last_brace = sanitized.rfind('}')
    if last_brace != -1:
        sanitized = sanitized[:last_brace + 1]
    
    # Step 5: Remove common prefixes that LLMs sometimes add
    prefixes_to_remove = [
        "Here's the response:",
        "Response:",
        "Answer:",
        "The response is:",
        "JSON response:",
        "Here's the JSON:",
        "The JSON is:"
    ]
    
    for prefix in prefixes_to_remove:
        if sanitized.startswith(prefix):
            sanitized = sanitized[len(prefix):].strip()
    
    # Step 6: Remove any trailing text after the JSON
    suffixes_to_remove = [
        "I hope this helps!",
        "Let me know if you need anything else!",
        "Is there anything else you'd like me to help with?",
        "Feel free to ask if you have more questions!"
    ]
    
    for suffix in suffixes_to_remove:
        if sanitized.endswith(suffix):
            sanitized = sanitized[:-len(suffix)].strip()
    
    # Step 7: Additional JSON fixes
    # Fix common issues with trailing commas
    sanitized = re.sub(r',\s*}', '}', sanitized)
    sanitized = re.sub(r',\s*]', ']', sanitized)
    
    # Fix unescaped quotes in string values
    # This is a more sophisticated approach to handle quotes within strings
    def fix_unescaped_quotes(match):
        content = match.group(1)
        # Replace unescaped quotes with escaped quotes, but be careful not to break the JSON
        # Only replace quotes that are not already escaped
        fixed = re.sub(r'(?<!\\)"', '\\"', content)
        return f'"{fixed}"'
    
    # Apply quote fixing to string values
    sanitized = re.sub(r'\"(.*?)\"', fix_unescaped_quotes, sanitized, flags=re.DOTALL)
    
    # Step 8: Additional trailing comma fixes
    sanitized = re.sub(r',(\s*[}\]])', r'\1', sanitized)
    
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