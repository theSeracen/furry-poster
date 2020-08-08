"""Module for FurAffinity and an interface for posting stories to it"""

import http.cookiejar
import io
import re
from typing import BinaryIO, List, Optional, TextIO

import bs4
import requests
from furryposter.story import Story
from furryposter.utilities import markdownformatter
from furryposter.websites.website import (AuthenticationError, Website,
                                          WebsiteError)


class FurAffinity(Website):
    """Class for a FurAffinity object"""

    def __init__(self):
        Website.__init__(
            self, 'furaffinity', {
                'general': 0, 'adult': 1}, 'bbcode')
        self.cookiesRegex = r'^(furaffinity|fa)?(cookies?)?\.txt'

    def submitStory(
            self,
            title: str,
            description: str,
            tags: str,
            passedRating: str,
            story: TextIO,
            thumbnail):
        """Send story and submit it via POST"""

        s = requests.Session()
        s.cookies = self.cookie
        tags = self.validateTags(tags)
        description = markdownformatter.parseStringBBcode(description)

        # type selection
        page = s.post(
            'http://www.furaffinity.net/submit/',
            params={
                'part': 2,
                'submission_type': 'story'})
        if page.status_code != 200:
            raise WebsiteError('An error has occurred when trying to reach FurAffinity')
        elif bs4.BeautifulSoup(page.content, 'html.parser').find('input', {'name': 'part'})['value'] == '2':
            raise WebsiteError("Posting didn't move on from first part")

        # file upload stage
        key = bs4.BeautifulSoup(
            page.content, 'html.parser').find('div', {'class': 'content'}).find('input', {'name': 'key'})['value']
        if thumbnail is not None:
            uploadFiles = {'submission': story, 'thumbnail': thumbnail}
        else:
            uploadFiles = {'submission': story}
        page = s.post('http://www.furaffinity.net/submit/story/4',
                      data={
                          'part': '3',
                          'key': key,
                          'submission_type': 'story'},
                      files=uploadFiles)

        if 'Uploaded file has a filesize of 0 bytes' in page.text:
            raise WebsiteError('One of the uploaded files read as 0 bytes')
        elif 'Error encountered' in page.text:
            raise WebsiteError('Error encountered with file upload')
        elif 'submission files could not be found' in page.text:
            raise WebsiteError('Submisssion files could not be found')
        elif bs4.BeautifulSoup(page.content, 'html.parser').find('input', {'name': 'part'})['value'] == '2':
            raise WebsiteError('Furaffinity submission stage reverted')
        elif page.status_code != 200:
            raise WebsiteError('The upload page returned with an error')

        # final stage
        key = bs4.BeautifulSoup(
            page.content, 'html.parser').find(
            'div', {
                'class': 'content'}).find(
                'input', {
                    'name': 'key'})['value']
        cat = bs4.BeautifulSoup(
            page.content, 'html.parser').find(
            'input', {
                'name': 'cat_duplicate'})['value']

        # TODO add customisation for hardcoded specifications and categories
        storyParams = {
            'key': key,
            'part': 5,
            'cat_duplicate': cat,
            'submission_type': 'story',
            'atype': 1,
            'species': 1,
            'gender': 0,
            'rating': self.ratings[passedRating],
            'title': title,
            'message': description,
            'keywords': tags,
            'scrap': 0}

        page = s.post(
            'https://www.furaffinity.net/submit/story/4',
            data=storyParams)
        if 'Security code missing or invalid' in page.text or 'view' not in page.url:
            raise WebsiteError("FurAffinity submission failed")

    def testAuthentication(self):
        """Test that the user is properly authenticated on the site"""

        testpage = requests.get(
            "https://www.furaffinity.net/controls/settings/",
            cookies=self.cookie)
        if testpage.status_code != 200 or "Please log in!" in testpage.text:
            raise AuthenticationError("FurAffinity authentication failed")

    def validateTags(self, tags: str) -> str:
        """Convert the given tag string to a form that is valid on the site"""
        return tags.replace(', ', ' ')

    def crawlGallery(self, user: str) -> List[str]:
        """Crawl a gallery for all the submissions"""
        self.testAuthentication()
        s = requests.Session()
        s.cookies = self.cookie

        gallery_page = 1
        submissions = []

        userGallery = 'http://www.furaffinity.net/gallery/{}/{}'.format(
            user, gallery_page)
        foundSubs = self._get_gallery_page(userGallery)

        while foundSubs:
            for sub in foundSubs:
                submissions.append('http://www.furaffinity.net{}'.format(sub.get('href')))

            gallery_page += 1
            userGallery = 'http://www.furaffinity.net/gallery/{}/{}'.format(
                user, gallery_page)
            foundSubs = self._get_gallery_page(userGallery)

        uniqueSubs = []
        for sub in submissions:
            if sub not in uniqueSubs:
                uniqueSubs.append(sub)

        uniqueSubs.reverse()

        return uniqueSubs

    def parseSubmission(self, url: str) -> Optional[Story]:
        s = requests.Session()
        s.cookies = self.cookie

        page = s.get(url)
        soup = bs4.BeautifulSoup(page.text, 'html.parser')
        subtype = soup.find('span', {'class': 'category-name'}).text

        if subtype != 'Story':
            return None

        title = soup.find('div', {'class': 'submission-title'}).text.strip()
        description = self._parse_html_desc_tags(soup.find('div', {'class': 'submission-description'})).strip()

        rawTags = soup.findAll('span', {'class': 'tags'})
        tags = []
        for tag in rawTags:
            tags.append(tag.text)
        tags = ', '.join(tags)

        rating = soup.find('span', {'class': 'rating-box'}).text.lower().strip()
        if rating == 'mature':
            rating = 'adult'

        source = s.get('http:{}'.format(soup.find('a', {
            'href': re.compile(r'//d.facdn.net/art/.*')}).get('href'))).content.decode('utf-8', 'ignore')
        story = Story('bbcode', title, description, tags, rating)
        story.content = source

        thumbnail = soup.find(
            'img', {
                'data-fullview-src': re.compile(r'//d.facdn.net/.*\.thumbnail\..*')}).get('data-fullview-src')
        if thumbnail is not None:
            story.loadThumbnail('default', io.BytesIO(s.get('http:{}'.format(thumbnail)).content))
        return story

    def _get_gallery_page(self, url: str) -> List[bs4.Tag]:
        page = requests.get(url, cookies=self.cookie)
        soup = bs4.BeautifulSoup(page.text, 'html.parser')
        return soup.findAll('a', {'href': re.compile(r'/view/\d*')})

    def _parse_html_desc_tags(self, master_tag: bs4.Tag) -> str:
        description = ''
        for tag in master_tag.children:
            if tag.name == 'i':
                description = description + '*{}*'.format(tag.text)
            elif tag.name == 'b':
                description = description + '**{}**'.format(tag.text)
            elif tag.name == 'a':
                description = description + '[{}]({})'.format(tag.text, tag.get('href'))
            elif isinstance(tag, bs4.NavigableString):
                description = description + tag
            else:
                description = description + self._parse_html_desc_tags(tag)
        return description


if __name__ == "__main__":
    site = FurAffinity()
    site.load('furaffinitycookies.txt')
    for sub in site.crawlGallery('seracen'):
        site.parseSubmission(sub)
    site.testSite()
