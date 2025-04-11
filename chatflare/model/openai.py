import os
import asyncio
from openai import OpenAI, AsyncOpenAI

from chatflare.model.base import ModelBase
from dotenv import load_dotenv
from datetime import datetime

class ChatOpenAI(ModelBase):
    def __init__(self, model_name="gpt-4o-mini", **kwargs):
        self.model_name = model_name
        if os.getenv('OPENAI_API_KEY') is None:
            load_dotenv('/app/.env')
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def predict(self, **kwargs):
        """
        """
        if 'model' not in kwargs:
            kwargs['model'] = self.model_name

        
        response = self.client.chat.completions.create(**kwargs)

        # get token usage from response
        usage_info = response.usage
        if usage_info:  
            prompt_tokens = usage_info.prompt_tokens
            completion_tokens = usage_info.completion_tokens
            total_tokens = usage_info.total_tokens
            

            with open("log-tokens.txt", "a", encoding="utf-8") as f:
                f.write(
                    f"{datetime.now()}, " 
                    f"[SYNC] Model: {kwargs['model']}, "
                    f"Prompt tokens: {prompt_tokens}, "
                    f"Completion tokens: {completion_tokens}, "
                    f"Total tokens: {total_tokens}\n"
                )

        
        if 'return_full_response' not in kwargs or kwargs['return_full_response'] == False:
            return response.choices[0].message.content
        else:
            return response

    async def apredict(self, **kwargs):
        """
        """
        if 'model' not in kwargs:
            kwargs['model'] = self.model_name

        response = await self.aclient.chat.completions.create(**kwargs)
        
        usage_info = response.usage
        if usage_info:
            print("get usage info")
            prompt_tokens = usage_info.prompt_tokens
            completion_tokens = usage_info.completion_tokens
            total_tokens = usage_info.total_tokens
            
            with open("log-tokens.txt", "a", encoding="utf-8") as f:
                f.write(
                    f"{datetime.now()}, " 
                    f"[ASYNC] Model: {kwargs['model']}, "
                    f"Prompt tokens: {prompt_tokens}, "
                    f"Completion tokens: {completion_tokens}, "
                    f"Total tokens: {total_tokens}\n"
                )

        if 'return_full_response' not in kwargs or kwargs['return_full_response'] == False:
            return response.choices[0].message.content
        else:
            return response