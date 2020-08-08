"""Module for Weasyl support"""
import http.cookiejar
import io
import json
import re
from typing import BinaryIO, Dict, List, TextIO

import bs4
import requests
from furryposter.story import Story
from furryposter.websites.website import (AuthenticationError, Website,
                                          WebsiteError)


class Weasyl(Website):
    def __init__(self):
        Website.__init__(self, 'weasyl', {'general': 10, 'adult': 40})
        self.cookiesRegex = r'^(weasyl|ws)?(cookies?)?\.txt'

    def validateTags(self, tags: str) -> str:
        return tags.replace(', ', ' ')

    def testAuthentication(self):
        page = requests.get(
            'https://www.weasyl.com/messages/notifications',
            cookies=self.cookie)
        if page.status_code != 200 or 'You must be signed in to perform this operation.' in page.text:
            raise AuthenticationError('Weasyl authentication failed')

    def submitStory(
            self,
            title: str,
            description: str,
            tags: str,
            passedRating: str,
            story: TextIO,
            thumbnail):

        s = requests.Session()
        s.cookies = self.cookie
        tags = self.validateTags(tags)

        page = s.get('https://www.weasyl.com/submit/literary')
        token = bs4.BeautifulSoup(
            page.content, 'html.parser').find('input', {'name': 'token'})['value']

        if thumbnail is not None:
            uploadFiles = {'submitfile': story, 'coverfile': thumbnail}
        else:
            uploadFiles = {'submitfile': story, 'coverfile': ''.encode('utf-8')}

        params = {
            'token': token,
            'title': title,
            'subtype': 2010,
            'rating': self.ratings[passedRating],
            'content': description,
            'tags': tags}

        page = s.post('https://www.weasyl.com/submit/literary', data=params, files=uploadFiles)

        if page.status_code != 200:
            raise WebsiteError(
                "Weasyl submission failed: Code {}".format(
                    page.status_code))

        if thumbnail is not None:
            # extra step for weasyl, confirm the thumbnail
            token = bs4.BeautifulSoup(page.content, 'html.parser').find('input', {'name': 'token'})['value']
            subID = re.search(r'thumbnail\?submitid=(\d*)', page.url).group(1)
            params = {
                'x1': 0,
                'x2': 0,
                'y1': 0,
                'y2': 0,
                'submitid': subID,
                'token': token}

            page = s.post(page.url, data=params)
            if page.status_code != 200 or '/submissions/' not in page.url:
                raise WebsiteError(
                    "Weasyl thumbnail confirmation failed: Code {}".format(
                        page.status_code))

    def crawlGallery(self, user: str) -> List[str]:
        self.testAuthentication()
        s = requests.Session()
        s.cookies = self.cookie

        subs = []
        pass_params = {}

        while True:
            submission_json = json.loads(
                s.get('http://weasyl.com/api/users/{}/gallery'.format(user),
                      params=pass_params).content)
            subs.extend(submission_json['submissions'])

            if submission_json['nextid'] is None:
                break
            pass_params = {'nextid': submission_json['nextid']}

        subs = list(filter(lambda x: x['subtype'] == 'literary', subs))

        return subs

    def parseSubmission(self, json_submission: Dict) -> Story:
        sub = json.loads(requests.get(
            'http://weasyl.com/api/submissions/{}/view'.format(json_submission['submitid']), cookies=self.cookie).content)

        title = json_submission['title']
        description = self._parse_description(sub['description'])
        tags = ', '.join(sub['tags'])
        content = requests.get(
            sub['media']['submission'][0]['url']).content.decode(encoding='utf-8', errors='ignore')

        thumbnail = None
        if 'cover' in sub['media']:
            thumbnail = requests.get(sub['media']['cover'][0]['url']).content
        elif 'thumbnail-source' in sub['media']:
            thumbnail = requests.get(sub['media']['thumbnail-source'][0]['url']).content

        if sub['rating'] == 'general':
            rating = 'general'
        else:
            rating = 'adult'

        story = Story('markdown', title, description, tags, rating)
        story.loadContent(io.StringIO(content))

        if thumbnail is not None:
            story.loadThumbnail('default', io.BytesIO(thumbnail))

        return story

    def _parse_description(self, description: str) -> str:
        description = re.sub(r'</?p>', '\n', description)

        description = description.replace('<br>', '\n')

        # turn links into markdown
        pattern = r'(<a.*?((?<=href=").*?)".*?>(.*?)</a>)'
        for match in re.findall(pattern, description):
            description = description.replace(
                match[0], '[{}]({})'.format(match[1], match[2]))

        return description.strip()


if __name__ == '__main__':
    site = Weasyl()
    site.load('weasylcookies.txt')
    site.testSite()
