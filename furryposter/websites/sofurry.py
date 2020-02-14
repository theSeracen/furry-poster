"""Module for SoFurry and an interface for posting stories to it"""

from furryposter.websites.website import Website, WebsiteError, AuthenticationError
import requests
import bs4
import http.cookiejar
import re
import json
import io
from furryposter.story import Story
from typing import TextIO, BinaryIO, List, Dict

class SoFurry(Website):
	def __init__(self):
		Website.__init__(self, 'sofurry', {'general':0, 'adult':1}, 'bbcode')

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

	def crawlGallery(self, user: str) -> List[str]:
		s = requests.Session()
		s.cookies = self.cookie

		user = json.loads(s.get('http://api2.sofurry.com/std/getUserProfile', params = {'username': user}).content)
		page = 1
		subs = []
		while True:
			js = json.loads(s.get('https://api2.sofurry.com/browse/user/stories?uid={}&format=json&&stories-page={}'.format(user['userID'], page), params = {'from': 'all time'}).content)
			subs.extend(js['items'])
			if len(js['items']) < 30: break
			page += 1
		subs.reverse()
		return subs

	def parseSubmission(self, sub: Dict) -> Story:
		subExtra = json.loads(requests.get('http://api2.sofurry.com/std/getSubmissionDetails', params = {'id':sub['id']}).content)
		story = Story('bbcode', sub['title'], sub['description'], sub['tags'])
		content = requests.get(subExtra['contentSourceUrl']).content.decode(encoding='utf-8')
		content = re.sub(r'<br.*?>', '\n', content)
		story.loadContent(io.StringIO(content))
		if subExtra['thumbnailSourceUrl'] is not None: story.loadThumbnail('default', io.BytesIO(requests.get(subExtra['thumbnailSourceUrl']).content))
		return story

	def validateTags(self, tags: str) -> str:
		#no validation needed for SoFurry; accepts CSV
		return tags

if __name__ == '__main__':
	cj = http.cookiejar.MozillaCookieJar('sofurrycookies.txt')
	site = SoFurry()
	#site.testSite(cj)
	cj.load()
	site.load(cj)
	for sub in site.crawlGallery('seracen'):
		site.parseSubmission(sub)
