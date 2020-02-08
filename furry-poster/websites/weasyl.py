"""Module for Weasyl support"""
from website import Website, WebsiteError, AuthenticationError
import requests
import bs4
import http.cookiejar
import re

class Weasyl(Website):
	def __init__(self, cookies):
		Website.__init__(self, 'weasyl')
		self.cookie = cookies

	def validateTags(self):
		pass

	def testAuthentication(self):
		pass
	
	def submitStory(self):
		pass

if __name__=='__main__':
	pass