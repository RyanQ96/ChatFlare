from chatflare.model.base import ModelBase 
from chatflare.prompt.base import PromptTemplate

class BaseChain:
    def __init__(self, model:ModelBase, prompt_template:PromptTemplate, **kwargs):
        self.model = model 
        self.prompt_template = prompt_template  
        self.JSON_MODE = False if 'JSON_MODE' not in kwargs else kwargs['JSON_MODE']

    def __repr__(self):
        return f"BaseChain(model={self.model}, json_mode={self.JSON_MODE}, prompt_template={self.prompt_template})"

    def turn_on_json_mode(self):
        self.JSON_MODE = True

    def predict(self, **kwargs):
        prompt_variables = self.prompt_template.variables
        prompt_kwargs = {k:v for k,v in kwargs.items() if k in prompt_variables}
        outer_kwargs = {k:v for k,v in kwargs.items() if k not in prompt_variables}
        if self.JSON_MODE:
            outer_kwargs['response_format'] = {"type": "json_object"}
        rendered_prompt = self.prompt_template.render(**prompt_kwargs)
        return self.model.predict(
            messages=[
                {
                    "role": "user",
                    "content": rendered_prompt
                }
            ],
            model=self.model.model_name,
            **outer_kwargs
        )
    
    async def apredict(self, **kwargs):
        prompt_variables = self.prompt_template.variables
        prompt_kwargs = {k:v for k,v in kwargs.items() if k in prompt_variables}
        outer_kwargs = {k:v for k,v in kwargs.items() if k not in prompt_variables}
        if self.JSON_MODE:
            outer_kwargs['response_format'] = {"type": "json_object"}
        rendered_prompt = self.prompt_template.render(**prompt_kwargs)
        return await self.model.apredict(
            messages=[
                {
                    "role": "user",
                    "content": rendered_prompt
                }
            ],
            model=self.model.model_name,
            **outer_kwargs
        )


    