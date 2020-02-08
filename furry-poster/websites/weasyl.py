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

	def validateTags(self,tags):
		return tags.replace(', ',' ')

	def testAuthentication(self):
		page = requests.get('https://www.weasyl.com/messages/notifications', cookies=self.cookie)
		if 'You must be signed in to perform this operation.' in page.text: raise AuthenticationError('Weasyl authentication failed')
	
	def submitStory(self, title, description, tags, story, thumbnail):
		
		s = requests.Session()
		s.cookies = self.cookie

		page = s.get('https://www.weasyl.com/submit/literary')
		token = bs4.BeautifulSoup(page.content,'html.parser').find('input',{'name':'token'})['value']

		uploadFiles = {'submitfile':story, 'thumbfile':thumbnail}
		params = {'token':token,'title':title, 'subtype':2010, 'rating':40,'content':description, 'tags':tags}

		page = s.post('https://www.weasyl.com/submit/literary', data=params, files=uploadFiles)

		if page.status_code != 200: raise WebsiteError("Weasyl submission failed: Code {}".format(page.status_code))

		#extra step for weasyl, confirm the thumbnail
		token = bs4.BeautifulSoup(page.content,'html.parser').find('input',{'name':'token'})['value']
		subID = re.search('thumbnail\?submitid=(\d*)', page.url).group(1)
		params = {'x1':0,'x2':0,'y1':0,'y2':0, 'submitid':subID}

		page = s.post(page.url, data=params)

		print('DEBUG')

if __name__ == '__main__':
	cj = http.cookiejar.MozillaCookieJar('weasylcookies.txt')
	cj.load()
	ws = Weasyl(cj)
	ws.testAuthentication()
	
	#title = input("Enter title: ")
	#description = input("Enter description: ")
	#tags = input("Enter tags: ")
	#directory = input("Enter directory: ")

	#import os
	#for file in os.listdir(directory):
	#	if file.endswith('.txt'): story = directory + '\\' + file
	#	if file.endswith('.png'): thumbnail = directory + '\\' + file
	#print(story)
	#print(thumbnail)
	#input('Press enter to confirm...')

	#ws.submitStory(title, description, tags, open(story, 'r', encoding='utf-8'),
	#open(thumbnail, 'rb'))

	#DEBUG
	ws.submitStory("A Timely Sabotage","This is my half of a trade with hyruzon. Crystal the very-smart-dragoness has made a time loop machine, but one of her colleagues isn't too happy about being outshone.","Dragoness Dragon Scifi Time Loop Orgasms Eggs Laying Feral Oviposition", open(r'C:\Users\Serenical\Dropbox\Stories\Resources\For Others\Trades\Hyruzon\A Timely series\A Timely Sabotage\A Timely SabotageFA.txt','r',encoding='utf-8'), open(r'C:\Users\Serenical\Dropbox\Stories\Resources\For Others\Trades\Hyruzon\A Timely series\A Timely Sabotage\Thumbnail.png', 'rb'))