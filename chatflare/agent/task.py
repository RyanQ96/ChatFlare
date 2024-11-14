import uuid 

class BaseTask: 
    def __init__(self):
        pass 
   
   
class SRTask(BaseTask): 
    def __init__(self, research_query=None, in_criteria=None, summarization_requirement=None):
        self._TASK_TYPE = "SR_TASK"
        self.research_query = research_query
        self.in_criteria = in_criteria
        self.summarization_requirement = summarization_requirement

    @property 
    def TASK_TYPE(self):
        return self._NODE_TYPE

    def __repr__(self):
        return f"SRTask(research_query={self.research_query})"

    