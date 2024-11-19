from typing import Callable, Union
from .action import BaseAction 
import uuid 

ActionOrFunction = Union[Callable, BaseAction] 


class TaskNode: 
    def __init__(self, task_name=None, action:ActionOrFunction=None):
        self._NODE_TYPE = "TASK_NODE"
        self.task_name = task_name
        self.node_name = f"{task_name.capitalize()}-{str(uuid.uuid4())[:4]}"
        self.action = action

    @property 
    def NODE_TYPE(self):
        return self._NODE_TYPE

    def __repr__(self):
        return f"TaskNode(task_name={self.task_name})"

    def __call__(self, thread): 
        output = self.action(thread)
        graph_state.update_state(output)
        return output 

    def setup_task(self, task_func: ActionOrFunction): 
        """
        Setup the task function for the node, auto-check input parameter required
        """
        self.task_func = task_func

class RouteNode: 
    def __init__(self, source_node=None, outer_edges=[], leverage_llm=False):
        self._NODE_TYPE = "ROUTE_NODE"
        self.node_name = f"RouteNode-{str(uuid.uuid4())[:4]}"
        self.source_node = source_node
        self.outer_edges = outer_edges
        self.leverage_llm = leverage_llm
    
    @property 
    def NODE_TYPE(self):
        return self._NODE_TYPE

    def __repr__(self):
        return f"RouteNode(source_node={self.source_node})"

    def add_target_node(self, edge, runnable, priority=0):
        if edge not in self.outer_edges:
            self.outer_edges.append(edge)

class LLMTaskNode(TaskNode):
    def __init__(self, task_name=None, action: BaseAction=None):
        super().__init__(task_name=task_name, action=action)
        self._NODE_TYPE = "LLM_TASK_NODE"

    def __repr__(self):
        return f"LLMTaskNode(task_name={self.task_name})"
    
    def setup_task(self, action: BaseAction): 
        """
        Setup the task function for the node, auto-check input parameter required
        """
        self.action = action

    def predict(self, thread): 
        output = self.action.run(thread)
        thread.graph_state.update_state(output)
        return output

    async def __call__(self, thread): 
        output = await self.action.arun(thread)
        thread.graph_state.update_state(output)
        return output

    @classmethod
    def from_action(cls, action: BaseAction):
        return cls(task_name=action.action_name, action=action)

        
class HumanInstructionNode(TaskNode):
    def __init__(self, task_name=None, action: BaseAction=None):
        super().__init__(task_name=task_name, action=action)
        self._NODE_TYPE = "HUMAN_INSTRUCTION_NODE"

    def __repr__(self):
        return f"HumanInstructionNode(task_name={self.task_name})"
    
    def setup_task(self, action: BaseAction): 
        """
        Setup the task function for the node, auto-check input parameter required
        """
        self.action = action

    async def __call__(self, thread): 
        output = await self.action.arun(thread)
        thread.graph_state.update_state(output)
        return output

    @classmethod
    def from_action(cls, action: BaseAction):
        return cls(task_name=action.action_name, action=action)

