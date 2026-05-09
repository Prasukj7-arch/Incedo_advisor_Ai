import boto3
import json

MODEL_ID = "us.meta.llama3-1-8b-instruct-v1:0"
REGION = "us-east-1"

client = boto3.client("bedrock-runtime", region_name=REGION)

def ask_llama(system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
    """Send a message to Llama and return the response text."""

    # Llama uses a specific prompt format with special tokens
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system_prompt}
<|eot_id|><|start_header_id|>user<|end_header_id|>
{user_message}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    body = json.dumps({
        "prompt": prompt,
        "max_gen_len": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9
    })

    response = client.invoke_model(modelId=MODEL_ID, body=body)
    result = json.loads(response["body"].read())
    return result["generation"].strip()