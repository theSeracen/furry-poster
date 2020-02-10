"""Module for Weasyl support"""
from furryposter.websites.website import Website, WebsiteError, AuthenticationError
import requests
import bs4
import http.cookiejar
import re
from typing import TextIO, BinaryIO

class Weasyl(Website):
	def __init__(self, cookies):
		Website.__init__(self, 'weasyl')
		self.cookie = cookies

	def validateTags(self,tags: str) -> str:
		return tags.replace(', ',' ')

	def testAuthentication(self):
		page = requests.get('https://www.weasyl.com/messages/notifications', cookies=self.cookie)
		if 'You must be signed in to perform this operation.' in page.text: raise AuthenticationError('Weasyl authentication failed')
	
	def submitStory(self, title: str, description: str, tags: str, story: TextIO, thumbnail):
		
		s = requests.Session()
		s.cookies = self.cookie
		tags = self.validateTags(tags)

		page = s.get('https://www.weasyl.com/submit/literary')
		token = bs4.BeautifulSoup(page.content,'html.parser').find('input',{'name':'token'})['value']

		if thumbnail is not None: uploadFiles = {'submitfile':story, 'coverfile':thumbnail}
		else: uploadFiles = {'submitfile':story, 'coverfile': ''.encode('utf-8')}

		params = {'token':token,'title':title, 'subtype':2010, 'rating':40,'content':description, 'tags':tags}

		page = s.post('https://www.weasyl.com/submit/literary', data=params, files=uploadFiles)

		if page.status_code != 200: raise WebsiteError("Weasyl submission failed: Code {}".format(page.status_code))
		if thumbnail is not None:
			#extra step for weasyl, confirm the thumbnail
			token = bs4.BeautifulSoup(page.content,'html.parser').find('input',{'name':'token'})['value']
			subID = re.search('thumbnail\?submitid=(\d*)', page.url).group(1)
			params = {'x1':0,'x2':0,'y1':0,'y2':0, 'submitid':subID, 'token':token}

			page = s.post(page.url, data=params)
			if page.status_code != 200 or '/submissions/' not in page.url: raise WebsiteError("Weasyl thumbnail confirmation failed: Code {}".format(page.status_code))

if __name__ == '__main__':
	cj = http.cookiejar.MozillaCookieJar('weasylcookies.txt')
	cj.load()
	ws = Weasyl(cj)
	ws.testAuthentication()
	
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

	ws.submitStory(title, description, tags, open(story, 'r', encoding='utf-8'), None)