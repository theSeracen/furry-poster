"""Contains abstract Website class for creating proper website interfaces to a real website, with errors for module/website related issues"""

from abc import ABC, abstractmethod
from typing import TextIO, BinaryIO, Dict, List
from furryposter.story import Story

class WebsiteError(Exception): pass

class AuthenticationError(WebsiteError):pass

class Website(ABC):
	def __init__(self, name: str, ratings: Dict[str, int], preferredFormat: str = 'markdown'):
		self.name = name
		self.preferredFormat = preferredFormat
		self.ratings = ratings
		self.cookiesRegex = r'^(master)?(cookies?)?\.txt'

	def load(self, cookiesLoc):
		cj = http.cookiejar.MozillaCookieJar(cookiesLoc)
		cj.load()
		self.cookie = cj
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
	
	@abstractmethod
	def crawlGallery(self, user: str) -> List[str]:
		pass

	@abstractmethod
	def parseSubmission(self, url: str) -> Story:
		pass

	def testSite(self):
		self.testAuthentication()
		
		title = input("Enter title: ")
		description = input("Enter description: ")
		tags = input("Enter tags: ")
		directory = input("Enter directory: ")
	
		import os
		for file in os.listdir(directory):
			if file.endswith('.txt'): story = directory + '\\' + file
			if file.endswith('.png'): thumbnail = directory + '\\' + file
		print(story)
		print(thumbnail)
		input('Press enter to confirm...')
	
		self.submitStory(title, description, tags, open(story, 'r', encoding='utf-8'), open(thumbnail, 'rb'))
		