import os 
import asyncio
from openai import OpenAI, AsyncOpenAI

from chatflare.model.base import ModelBase

class ChatOpenAI(ModelBase):
    def __init__(self, model_name="gpt-4o", **kwargs):
        self.model_name = model_name 
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def predict(self, **kwargs): 
        if 'model' not in kwargs: 
            kwargs['model'] = self.model_name

        return self.client.chat.completions.create(
            **kwargs
        ).choices[0].message.content

    async def aprerdict(self, **kwargs): 
        if 'model' not in kwargs: 
            kwargs['model'] = self.model_name
            
        return await self.aclient.chat.completions.create(
            **kwargs
        ).choices[0].message.content