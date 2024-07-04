import os 
import asyncio
from openai import OpenAI, AsyncOpenAI

from chatflare.model.base import ModelBase

class OpenAI(ModelBase):
    def __init__(self, model_name="gpt-4o", **kwargs):
        self.model_name = model_name 
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def predict(self, **kwargs): 
        if 'model_name' not in kwargs: 
            kwargs['model_name'] = self.model_name

        return self.client.chat.completions.create(
            **kwargs
        )

    async def aprerdict(self, **kwargs): 
        if 'model_name' not in kwargs: 
            kwargs['model_name'] = self.model_name
            
        return await self.aclient.chat.completions.create(
            **kwargs
        )