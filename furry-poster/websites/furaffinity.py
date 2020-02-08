"""Module for FurAffinity and an interface for posting stories to it"""

from website import Website
from websiteerrors import AuthenticationError, WebsiteError
import bs4
import requests
import http.cookiejar

class FurAffinity(Website):
	"""Class for a FurAffinity object"""
	def __init__(self, cookies):
		Website.__init__(self, 'furaffinity')
		self.cookie = cookies

	def submitStory(self, title, description, tags, story, thumbnail):
		"""Send story and submit it via POST"""
		#this is the set data to select story type
		params = {'part': 5, 'submission_type':'story', 'submission': story, 'thumbnail': thumbnail, 'title': title, 'message':description, 'keywords': description, 'scrap':0, 'rating': 2}
		submit = requests.post('https://www.furaffinity.net/submit/story/4', cookies=self.cookie, data=params)
		if 'Security code missing or invalid' in submit.text: raise WebsiteError("FurAffinity submission failed")


	def testAuthentication(self):
		"""Test that the user is properly authenticated on the site"""
		#try to get a restricted page and error on bad result
		testpage = requests.get("https://www.furaffinity.net/controls/settings/", cookies=self.cookies)
		if "Please log in!" in testpage.content: raise AuthenticationError("FurAffinity authentication failed")


	def validateTags(self, tags):
		"""Convert the given tag string to a form that is valid on the site"""
		return tags.replace(', ',' ')

if __name__ == "__main__":
	cj = http.cookiejar.MozillaCookieJar("cookies.txt")
	cj.load()
	fa = FurAffinity(cj)
	
	
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

	fa.submitStory(title, description, tags, open(story, 'r', encoding='utf-8'), open(thumbnail, 'rb'))