import uuid 

class BaseTask: 
    def __init__(self):
        pass 
   
   
class SRTask(BaseTask): 
    def __init__(self, research_query=None, in_criteria=None, user_specified_requirement = None, summarization_requirement=None):
        self._TASK_TYPE = "SR_TASK"
        self.research_query = research_query
        self.user_specified_requirement = user_specified_requirement
        self.in_criteria = in_criteria
        self.summarization_requirement = summarization_requirement

    @property 
    def TASK_TYPE(self):
        return self._TASK_TYPE

    @property 
    def detailed_research_query(self):
        query = self.research_query    
        if self.user_specified_requirement:
            query += f" With detailed requirement: {self.user_specified_requirement}"
        return query

    def __repr__(self):
        return f"SRTask(research_query={self.research_query}, in_criteria={self.in_criteria}, user_specified_requirement={self.user_specified_requirement}, summarization_requirement={self.summarization_requirement}) "

    