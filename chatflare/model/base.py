from abc import ABC, abstractmethod 

class ModelBase(ABC): 
    def __init__(self, **kwargs):
        pass

    def __repr__(self):
        return f"{getattr(self, 'model_name', 'unknown_model')}"
    
    @abstractmethod 
    def predict(self, **kwargs):
        pass

    @abstractmethod
    def aprerdict(self, **kwargs):
        pass 
        