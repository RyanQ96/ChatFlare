"""deprecated module, move to task.py"""

import asyncio
from ABC import abstractmethod, ABC 


class ActionBase(ABC):
    def __init__(self, action_name, runnable, **kwargs):
        self.action_name = action_name 
        self.runnable = runnable

    @abstractmethod
    async def arun(self, **kwargs):
        pass

    @abstractmethod
    def run(self, **kwargs):
        pass
    