import uuid 

class BaseTask: 
    def __init__(self):
        pass 
  
# DEFAULT_IN_CRITERIA = "Studies that investigate pediatric populations diagnosed with ADHD and treated with MPH; studies must report side effects and changes in symptoms. Exclude studies focusing on adults or without explicit side effect reporting." 
DEFAULT_IN_CRITERIA = ""

class SRTask(BaseTask): 
    def __init__(self, research_query=None, in_criteria=None, user_specified_requirement = None, summarization_requirement=None):
        self._TASK_TYPE = "SR_TASK"
        self.research_query = research_query
        self.user_specified_requirement = user_specified_requirement
        self.in_criteria = in_criteria or DEFAULT_IN_CRITERIA
        self.summarization_requirement = summarization_requirement

    @property 
    def TASK_TYPE(self):
        return self._TASK_TYPE

    @property 
    def detailed_research_query(self):
        query = self.research_query or ""   
        if self.user_specified_requirement:
            query += f" With detailed requirement: {self.user_specified_requirement}"
        return query
    
    @property 
    def detailed_inclusion_exclusion_criteria(self):
        _criteria = "" 
        if self.in_criteria: 
            _criteria += f"Inclusion/Exclusion Criteria: {self.in_criteria}"
        else: 
            _criteria += "No detailed inclusion/exclusion criteria specified."
        return _criteria

    
    def to_dict(self):
        return {
            "research_query": self.research_query,
            "in_criteria": self.in_criteria,
            "user_specified_requirement": self.user_specified_requirement,
            "summarization_requirement": self.summarization_requirement,
        }

    def __repr__(self):
        return f"SRTask(research_query={self.research_query}, in_criteria={self.in_criteria}, user_specified_requirement={self.user_specified_requirement}, summarization_requirement={self.summarization_requirement}) "

    