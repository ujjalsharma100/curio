from anthropic import Anthropic

client = Anthropic(api_key="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")

def get_response_from_llm(prompt: str) -> str:
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