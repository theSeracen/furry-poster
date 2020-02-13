"""Module for FurAffinity and an interface for posting stories to it"""

from furryposter.websites.website import Website, AuthenticationError, WebsiteError
from furryposter.utilities import markdownformatter
import bs4
import requests
import http.cookiejar
from typing import TextIO, BinaryIO

class FurAffinity(Website):
	"""Class for a FurAffinity object"""
	def __init__(self):
		Website.__init__(self, 'furaffinity', {'general':0, 'adult':1}, 'bbcode')

	def submitStory(self, title: str, description: str, tags: str, passedRating: str, story: TextIO, thumbnail):
		"""Send story and submit it via POST"""
		
		s = requests.Session()
		s.cookies = self.cookie
		tags = self.validateTags(tags)
		description = markdownformatter.parseStringBBcode(description)

		#type selection
		page = s.post('http://www.furaffinity.net/submit/', data={'part': 2, 'submission_type':'story'})
		if page.status_code != 200: raise WebsiteError('An error has occurred when trying to reach FurAffinity')

		#file upload stage
		key = bs4.BeautifulSoup(page.content, 'html.parser').find('input', {'name':'key'})['value']
		if thumbnail is not None: uploadFiles = {'submission': story, 'thumbnail':thumbnail}
		else: uploadFiles = {'submission':story}
		page = s.post('http://www.furaffinity.net/submit/', data={'part': 3, 'submission_type':'story', 'key':key}, files=uploadFiles)

		if 'Uploaded file has a filesize of 0 bytes' in page.text: raise WebsiteError('One of the uploaded files read as 0 bytes')
		elif 'Error encountered' in page.text: raise WebsiteError('Error encountered with file upload')
		elif page.status_code != 200: raise WebsiteError('The upload page returned with an error')

		#final stage
		cat = bs4.BeautifulSoup(page.content, 'html.parser').find('input', {'name':'cat_duplicate'})['value']
		key = bs4.BeautifulSoup(page.content, 'html.parser').find('input', {'name':'key'})['value']

		#TODO add customisation for hardcoded specifications and categories
		params = {'key': key, 'part':5, 'cat_duplicate':cat, 'submission_type':'story',
			'atype':1, 'species':1, 'gender':0, 'rating': self.ratings[passedRating],
			'title':title, 'message':description,'keywords':tags,
			'scrap': 0}

		page = s.post('https://www.furaffinity.net/submit/story/4', data=params)
		if 'Security code missing or invalid' in page.text or 'view' not in page.url: raise WebsiteError("FurAffinity submission failed")

	def testAuthentication(self):
		"""Test that the user is properly authenticated on the site"""
		#try to get a restricted page and error on bad result
		testpage = requests.get("https://www.furaffinity.net/controls/settings/", cookies=self.cookie)
		if "Please log in!" in testpage.text: raise AuthenticationError("FurAffinity authentication failed")


	def validateTags(self, tags: str) -> str:
		"""Convert the given tag string to a form that is valid on the site"""
		return tags.replace(', ',' ')

if __name__ == "__main__":
	cj = http.cookiejar.MozillaCookieJar("cookies.txt")
	site = FurAffinity()
	site.testSite(cj)
