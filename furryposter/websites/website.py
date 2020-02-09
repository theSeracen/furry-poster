"""Contains abstract Website class for creating proper website interfaces to a real website, with errors for module/website related issues"""

from abc import ABC, abstractmethod

class WebsiteError(Exception): pass

class AuthenticationError(WebsiteError):pass

class Website(ABC):
	def __init__(self, name):
		self.name = name

	@abstractmethod
	def submitStory(self, title, description, tags, story, thumbnail):
		"""Send story and submit it via website mechanisms"""
		pass

	@abstractmethod
	def testAuthentication(self):
		"""Test that the user is properly authenticated on the site"""
		pass

	@abstractmethod
	def validateTags(self):
		"""Convert the given tag string to a form that is valid on the site"""
		pass