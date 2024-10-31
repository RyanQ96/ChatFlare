from chatflare.graph.workflow import BaseWorkflow

import uuid 

class BaseAgent:
    """ Base class for all agents """
    def __init__(self, agent_name: str=None, workflow: BaseWorkflow=None, environment=None): 
        """"""
        self.agent_id = str(uuid.uuid4())
        self.agent_name: str = agent_name
        self.workflow: BaseWorkflow = workflow.bind_to_agent(self) if workflow is not None else None
        self.environment = environment 
        
    def register_workflow(self, workflow: BaseWorkflow):    
        self.workflow = workflow.bind_to_agent(self)
        
    def register_environment(self, environment):
        self.environment = environment
        
    ## TODO: Implement start of the workflow interface on agent, connect to workflow 
    def start_workflow(self):
        pass
    
    # def 
    
     
    def __repr__(self):
        return f"{getattr(self, 'agent_name', 'unknown_agent')}"
    
    
    
    