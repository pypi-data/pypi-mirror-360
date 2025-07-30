from abc import ABC, abstractmethod

class BaseHttpAuth(ABC):

    @abstractmethod
    def login(username, password):
        ...