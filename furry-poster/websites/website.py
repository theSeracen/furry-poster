"""Abstract Website class for creating proper website interfaces to a real website"""

from abc import ABC, abstractmethod

class Website(ABC):
    def __init__(self, name, csvTags=false):
        self.name = name
        self.csvTags = csvTags

    @abstractmethod
    def submitStory(self):
        pass

    @abstractmethod
    def testAuthentication(self):
        pass

    @abstractmethod
    def validateTags(self):
        pass