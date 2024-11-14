"""deprecated module, move to task.py"""

import asyncio
from abc import abstractmethod, ABC 


class BaseAction(ABC):
    def __init__(self, action_name, runnable, **kwargs):
        self.action_name = action_name 
        self.runnable = runnable
        
    @property
    def action_variables(self):
        return self.runnable.variables

    @abstractmethod
    async def arun(self, graph_state, **kwargs):
        pass

    @abstractmethod
    def run(self, graph_state, **kwargs):
        pass
    