from abc import ABC, abstractclassmethod

class LoggingHandlerInstance(ABC): 
    """Need to have async methods for logging and alogging to avoid blocking the main thread"""
    def __init__(self, **kwargs):
        pass

    @abstractclassmethod
    def log(self, **kwargs):
        pass

    @abstractclassmethod
    def alog(self, **kwargs):
        pass