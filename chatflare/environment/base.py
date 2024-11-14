from chatflare.agent.base import BaseAgent
from chatflare.graph.memoryinterface import MemoryInterface

class BaseEnvironment(BaseModel):
    agents: List[BaseAgent] = [] 
    supervisor: BaseAgent = None # role of human
    global_memory_bank: MemoryInterface = None

    class Config: 
        arbitrary_types_allowed = True  

    def registerAgent(self, agent: BaseAgent): 
        """"""
        # raise NotImplementedError
        if agent not in self.agents:
            self.agents.append(agent)
            return True

    def unregisterAgent(self, agent: BaseAgent): 
        """"""
        if agent in self.agents:
            self.agents.remove(agent)
            return True

    def interact(self, agent: BaseAgent, action: str, broadcast: bool = False) -> str: 
        """"""
        raise NotImplementedError

    def broadcast(self, agent: BaseAgent, action: str): 
        """"""
        raise NotImplementedError

    def supervise_on_agents(self, agents: List[BaseAgent], action: str): 
        """directly act on a specific agent"""
        raise NotImplementedError   