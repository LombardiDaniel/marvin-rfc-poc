import abc

class Storage(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @abc.abstractmethod
    def upload(self, items_list=[]):
        pass

    @abc.abstractmethod
    def download(self, items_list=[]):
        pass
