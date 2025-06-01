import os
from typing import List
from anthropic import Anthropic
import json

# Initialize Anthropic client
# Note: Set ANTHROPIC_API_KEY in environment variables
client = Anthropic(api_key="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")

def create_prompt(updates: List[str]) -> str:
    """Creates a prompt for Claude to convert multiple news updates into conversational messages."""
    updates_text = "\n".join([f"{i+1}. {update}" for i, update in enumerate(updates)])
    return f"""You are a helpful assistant that converts news updates into personalized, conversational messages.
            Your task is to rewrite the following list of news updates as if you're sharing them with a friend in casual text messages.
            The list of messages are messages that someone would be sending in text chat to convey the information that the list of updates have.
            Make the messages sound natural, conversational, and engaging. Add appropriate emojis if relevant.

            News updates:
            {updates_text}

            Respond with a JSON array of strings, where each string is a conversational message.
            Example format:
            [
                "Hey bro",
                "Just heard that so and so happened!",
                "OMG, you won't believe what happened! this and this !",
                "Interesting study came out today - this happended."
            ]

            Respond with ONLY the JSON array, nothing else."""

def personalize_updates(updates: List[str]) -> List[str]:
    """
    Converts a list of news updates into personalized, conversational messages using Claude.
    Makes a single API call to process all updates at once.
    
    Args:
        updates (List[str]): List of news updates to be personalized
        
    Returns:
        List[str]: List of personalized conversational messages
    """
    if not updates:
        return []
        
    try:
        # Create the prompt for all updates
        prompt = create_prompt(updates)
        
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

        print(message)
        
        # Extract and parse the JSON response
        response_text = message.content[0].text.strip()
        print(response_text)
        personalized_messages = json.loads(response_text)
        print(personalized_messages)
        return personalized_messages
            
    except Exception as e:
        print(f"Error while personalizing updates: {str(e)}")
        # Return original updates if API call fails
        return []
