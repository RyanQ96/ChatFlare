import os
import asyncio
from openai import OpenAI, AsyncOpenAI

from chatflare.model.base import ModelBase
from dotenv import load_dotenv
from datetime import datetime

import boto3 
import aioboto3
import json



def extract_json_content(text):
    """
    Extract the content inside a JSON blob surrounded by ```json and ```.
    
    Args:
        text (str): The input string containing the JSON blob.
    
    Returns:
        str: The extracted JSON content, or None if not found.
    """
    import re
    # Define the regex pattern to extract content between ```json and ```
    pattern = r"```json\n(.*?)```"
    
    # Use re.DOTALL to match across multiple lines
    match = re.search(pattern, text, re.DOTALL)
    
    # Return the matched group or None if no match is found
    return match.group(1) if match else None


class LlamaBedrock:
    def __init__(self, model_name="meta.llama3-3-70b-instruct-v1:0", **kwargs):
        self.model_name = model_name
        if os.getenv('AWS_ACCESS_KEY_ID') is None:
            ## check if there is an /app/bedrock.env file
            if os.path.exists('/app/bedrock.env'):
                load_dotenv('/app/bedrock.env')
            else:
                load_dotenv('bedrock.env')

    def predict(self, **kwargs):
        if 'modelId' not in kwargs:
            kwargs['modelId'] = self.model_name
        kwargs["contentType"] = "application/json" 
        kwargs["accept"] = "application/json" 
        
        client = boto3.client("bedrock-runtime", region_name="us-east-2")
        
        response = client.invoke_model(**kwargs)
        
        response_content = response['body'].read().decode('utf-8')
        response_obj = json.loads(response_content)
        
        if "prompt_token_count" in response_obj and "generation_token_count" in response_obj:
            prompt_tokens = response_obj["prompt_token_count"]
            completion_tokens = response_obj["generation_token_count"]
            total_tokens = prompt_tokens + completion_tokens
            with open("log-tokens.txt", "a", encoding="utf-8") as f:
                f.write(
                    f"{datetime.now()}, " 
                    f"[ASYNC] Model: {kwargs['modelId']}, "
                    f"Prompt tokens: {prompt_tokens}, "
                    f"Completion tokens: {completion_tokens}, "
                    f"Total tokens: {total_tokens}\n"
                )
        
        json_blob = extract_json_content(response_obj['generation'])
        return json_blob

    async def apredict(self, **kwargs):
        if 'modelId' not in kwargs:
            kwargs['modelId'] = self.model_name
        kwargs["contentType"] = "application/json" 
        kwargs["accept"] = "application/json" 
        session = aioboto3.Session()
        async with session.client("bedrock-runtime", region_name="us-east-2") as client:
            response = await client.invoke_model(**kwargs)
            response_content = await response['body'].read()
            response_obj = json.loads(response_content)
            if "prompt_token_count" in response_obj and "generation_token_count" in response_obj:
                prompt_tokens = response_obj["prompt_token_count"]
                completion_tokens = response_obj["generation_token_count"]
                total_tokens = prompt_tokens + completion_tokens
                with open("log-tokens.txt", "a", encoding="utf-8") as f:
                    f.write(
                        f"{datetime.now()}, " 
                        f"[ASYNC] Model: {kwargs['modelId']}, "
                        f"Prompt tokens: {prompt_tokens}, "
                        f"Completion tokens: {completion_tokens}, "
                        f"Total tokens: {total_tokens}\n"
                    )
            print(response_obj)
            json_blob = extract_json_content(response_obj['generation']) or response_obj['generation']
            print(json_blob)
            return json_blob
        return None