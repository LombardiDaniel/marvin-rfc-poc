from abc import ABCMeta, abstractmethod

class Action(metaclass=ABCMeta):

    def __init__(self, *kwargs):
        pass
    
    @abstractmethod
    def entrypoint(self, *kwargs):
        pass