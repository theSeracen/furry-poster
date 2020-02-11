"""Module for SoFurry and an interface for posting stories to it"""

from furryposter.websites.website import Website, WebsiteError, AuthenticationError
import requests
import bs4
import http.cookiejar
import re
from typing import TextIO, BinaryIO

class SoFurry(Website):
	def __init__(self, cookies):
		Website.__init__(self, 'sofurry', {'general':0, 'adult':1})
		self.cookie = cookies

	def submitStory(self, title: str, description: str, tags: str, passedRating: str, story: TextIO, thumbnail):
		"""Send story and submit it via POST"""
		s = requests.Session()
		s.cookies = self.cookie
		tags = self.validateTags(tags)
		#sofurry requires text to be submitted, not a story file
		story = ''.join(story.readlines())

		page = s.get('https://www.sofurry.com/upload/details?contentType=0')
		secret = bs4.BeautifulSoup(page.content,'html.parser').find('input',{'name':'UploadForm[P_id]'})['value']
		token = re.search("site_csrf_token_value = \'(.*)\'", page.text).group(1)

		params = {'UploadForm[P_id]': secret, 'UploadForm[P_title]':title, 'UploadForm[textcontent]':story,
			'UploadForm[contentLevel]': self.ratings[passedRating], 'UploadForm[description]':description, 'UploadForm[formtags]':tags,
			'YII_CSRF_TOKEN':token, 'save':'publish'}

		if thumbnail is not None :uploadFiles = {'UploadForm[binarycontent_5]':thumbnail}
		else: uploadFiles = None

		page = s.post('https://www.sofurry.com/upload/details?contentType=0', files=uploadFiles, data=params)
		if page.status_code != 200: raise WebsiteError('SoFurry story upload failed')

	def testAuthentication(self):
		
		testpage = requests.get("https://sofurry.com/upload", cookies=self.cookie)
		if 'Access Denied' in testpage.text: raise AuthenticationError("SoFurry authentication failed")

	def validateTags(self, tags: str) -> str:
		#no validation needed for SoFurry; accepts CSV
		return tags

if __name__ == '__main__':
	cj = http.cookiejar.MozillaCookieJar('sofurrycookies.txt')
	cj.load()
	sf = SoFurry(cj)
	sf.testAuthentication()
	
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

	sf.submitStory(title, description, tags, open(story, 'r', encoding='utf-8'), open(thumbnail, 'rb'))