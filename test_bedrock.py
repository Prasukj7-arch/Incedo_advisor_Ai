import boto3
import json

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

prompt = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 20,
    "messages": [
        {
            "role": "user",
            "content": "Say hello from AWS Bedrock in one sentence."
        }
    ]
}

response = bedrock.invoke_model(
    modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    body=json.dumps(prompt)
)

response_body = json.loads(response["body"].read())

print(response_body["content"][0]["text"])