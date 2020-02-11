"""Contains abstract Website class for creating proper website interfaces to a real website, with errors for module/website related issues"""

from abc import ABC, abstractmethod
from typing import TextIO, BinaryIO, Dict

class WebsiteError(Exception): pass

class AuthenticationError(WebsiteError):pass

class Website(ABC):
	def __init__(self, name: str, ratings: Dict[str, int], preferredFormat: str = 'markdown'):
		self.name = name
		self.preferredFormat = preferredFormat
		self.ratings = ratings

	@abstractmethod
	def submitStory(self, title: str, description: str, tags: str, rating: str, story: TextIO, thumbnail):
		"""Send story and submit it via website mechanisms"""
		pass

	@abstractmethod
	def testAuthentication(self):
		"""Test that the user is properly authenticated on the site"""
		pass

	@abstractmethod
	def validateTags(self, tags: str) -> str:
		"""Convert the given tag string to a form that is valid on the site"""
		pass