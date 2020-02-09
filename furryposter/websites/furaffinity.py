"""Module for FurAffinity and an interface for posting stories to it"""

from furryposter.websites.website import Website, AuthenticationError, WebsiteError
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
		
		s = requests.Session()
		s.cookies = self.cookie
		tags = self.validateTags(tags)

		#type selection
		page = s.post('http://www.furaffinity.net/submit/', data={'part': 2, 'submission_type':'story'})
		key = bs4.BeautifulSoup(page.content, 'html.parser').find('input', {'name':'key'})['value']

		#file upload stage
		uploadFiles = {'submission': story, 'thumbnail':thumbnail}
		page = s.post('http://www.furaffinity.net/submit/', data={'part': 3, 'submission_type':'story', 'key':key}, files=uploadFiles)
		if 'Error encountered' in page.text: raise WebsiteError('Error encounted with file upload')

		#final stage
		cat = bs4.BeautifulSoup(page.content, 'html.parser').find('input', {'name':'cat_duplicate'})['value']
		key = bs4.BeautifulSoup(page.content, 'html.parser').find('input', {'name':'key'})['value']

		#TODO add customisation for hardcoded specifications and categories
		params = {'key': key, 'part':5, 'cat_duplicate':cat, 'submission_type':'story',
			'atype':1, 'species':1, 'gender':0, 'rating': 1,
			'title':title, 'message':description,'keywords':tags,
			'scrap': 0}

		page = s.post('https://www.furaffinity.net/submit/story/4', data=params)
		if 'Security code missing or invalid' in page.text or 'view' not in page.url: raise WebsiteError("FurAffinity submission failed")

	def testAuthentication(self):
		"""Test that the user is properly authenticated on the site"""
		#try to get a restricted page and error on bad result
		testpage = requests.get("https://www.furaffinity.net/controls/settings/", cookies=self.cookie)
		if "Please log in!" in testpage.text: raise AuthenticationError("FurAffinity authentication failed")


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
