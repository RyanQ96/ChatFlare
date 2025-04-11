from chatflare.graph.workflow import BaseWorkflow
from chatflare.graph.base import GraphTraverseThread
import uuid 

class BaseAgent:
    """ Base class for all agents """
    def __init__(self, agent_id:str=None, agent_name: str=None, workflow: BaseWorkflow=None, environment=None, thread=None): 
        """"""
        self.agent_id = agent_id or "IRAgent-" + str(uuid.uuid4())[:4]
        self.agent_name: str = agent_name
        self.workflow: BaseWorkflow = workflow.bind_to_agent(self) if workflow is not None else None
        self.environment = environment 
        self.active_thread = thread
        self.threads = {} 
        if thread is not None:
            self.threads[thread.thread_id] = thread
        
    def register_workflow(self, workflow: BaseWorkflow):    
        self.workflow = workflow.bind_to_agent(self)
        
    def register_environment(self, environment):
        self.environment = environment
        
    ## TODO: Implement start of the workflow interface on agent, connect to workflow 
    def start_workflow(self):
        pass

    def register_thread(self, thread: GraphTraverseThread):
        self.active_thread = thread
        self.threads[thread.thread_id] = thread
    
    def __repr__(self):
        return f"{getattr(self, 'agent_name', 'unknown_agent')}"
    
    
    
    