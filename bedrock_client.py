import boto3
import json

MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
REGION = "us-east-1"

client = boto3.client("bedrock-runtime", region_name=REGION)

def ask_claude(system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
    """Send a message to Claude and return the response text."""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_message}
        ]
    })

    response = client.invoke_model(modelId=MODEL_ID, body=body)
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]