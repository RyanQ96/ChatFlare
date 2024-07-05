import string

class PromptTemplate:
    """
    A class to represent a prompt template.

    Example usage: 
        .. code-block:: python
            from chatflare.prompt.base import PromptTemplate 
            template = "Hello {name}, how are you?"
            prompt = PromptTemplate(template)
            print(prompt.render(name="John"))
            # Output: Hello John, how are you?
    """
    def __init__(self, template, **kwargs):
        self.template = template
        self._variables = self._get_variables()

    def __repr__(self):
        return f"PromptTemplate(variables={self.variables}, template={self.template[:1000]})"

    def _get_variables(self):
        if self.template:
            formatter = string.Formatter() 
            return [field for _, field, _, _ in formatter.parse(self.template) if field]
    
    @property 
    def variables(self):
        return self._variables 

    def render(self, **kwargs):
        return self.template.format(**kwargs)

    def render_autofill(self, **kwargs):
        for variable in self._variables:
            if variable not in kwargs:
                kwargs[variable] = ''
        return self.template.format(**kwargs)

    
    


    
