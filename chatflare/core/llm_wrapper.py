from chatflare.model.base import ModelBase 
from chatflare.prompt.base import PromptTemplate
# import tenacity
import json

class BaseChain:
    def __init__(self, model:ModelBase, prompt_template:PromptTemplate, **kwargs):
        self.model = model 
        self.prompt_template = prompt_template  
        self.JSON_MODE = False if 'JSON_MODE' not in kwargs else kwargs['JSON_MODE']
        
        if 'json_mode' in kwargs and kwargs['json_mode']:
            self.turn_on_json_mode()
    
    def __repr__(self):
        return f"BaseChain(model={self.model}, json_mode={self.JSON_MODE}, prompt_template={self.prompt_template.variables})"

    @property
    def variables(self):
        if self.prompt_template:
            return self.prompt_template.variables
        return []
    
    def turn_on_json_mode(self):
        self.JSON_MODE = True

    def predict(self, **kwargs):
        prompt_variables = self.prompt_template.variables
        prompt_kwargs = {k:v for k,v in kwargs.items() if k in prompt_variables}
        outer_kwargs = {k:v for k,v in kwargs.items() if k not in prompt_variables}
        if 'llama' in self.model.model_name: 
            rendered_prompt = self.prompt_template.render_llama(**prompt_kwargs)
            return self.model.predict(
                body=json.dumps({
                    'prompt': rendered_prompt, 
                    'max_gen_len': 4096, 
                    'temperature': 0.1, 
                    'top_p': 0.9, 
                }).encode('utf-8'),
            )
        else:
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
                temperature=0.2, 
                **outer_kwargs
            )

    # @tenacity.retry(
    #     stop=tenacity.stop_after_attempt(2),
    #     wait=tenacity.wait_none(),  # No waiting time between retries
    #     retry=tenacity.retry_if_exception_type(ValueError),
    #     before_sleep=lambda retry_state: print(
    #         f"ValueError occurred: {retry_state.outcome.exception()}, retrying..."),
    #     # Default value when all retries are exhausted
    #     retry_error_callback=lambda retry_state: 0
    # )
    async def apredict(self, **kwargs):
        prompt_variables = self.prompt_template.variables
        prompt_kwargs = {k:v for k,v in kwargs.items() if k in prompt_variables}
        outer_kwargs = {k:v for k,v in kwargs.items() if k not in prompt_variables and k != "debug"}
        if 'llama' in self.model.model_name:
            rendered_prompt = self.prompt_template.render_llama(**prompt_kwargs)
            output = await self.model.apredict(
                body=json.dumps({
                    'prompt': rendered_prompt, 
                    'max_gen_len': 8192, 
                    'temperature': 0.1, 
                    'top_p': 0.9, 
                }).encode('utf-8'),
            )
            if self.JSON_MODE:
                return json.loads(output)
            return output
            
        else: 
            if self.JSON_MODE:
                outer_kwargs['response_format'] = {"type": "json_object"}
            rendered_prompt = self.prompt_template.render(**prompt_kwargs)
            output = await self.model.apredict(
                messages=[
                    {
                        "role": "user",
                        "content": rendered_prompt
                    }
                ],
                model=self.model.model_name,
                temperature=0, 
                **outer_kwargs
            )
            
            if "debug" in kwargs and kwargs["debug"]:
                print(f"logging: apredict output: {output}")
            
            if self.JSON_MODE:
                return json.loads(output)
            return output


    