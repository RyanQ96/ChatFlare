from chatflare.graph.base import BaseGraph


class BaseWorkflow(BaseGraph):
    def __init__(self):
        super().__init__()
        self.agent = None # host agent of the task 

    def __repr__(self):
        return f"BaseTask(...TO BE IMPLEMENTED...)"
    
    def commit(self):
        pass

    def rollback(self):
        pass

    def sync_with_branch(self):
        pass
    
    def bind_to_agent(self, agent):
        self.agent = agent 
        return self