from abc import ABC, abstractmethod 

class ModelBase(ABC): 
    def __init__(self, **kwargs):
        pass
    
    @abstractmethod 
    def predict(self, **kwargs):
        pass

    @abstractmethod
    def aprerdict(self, **kwargs):
        pass 
        