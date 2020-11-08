"""Module for FurAffinity and an interface for posting stories to it"""

import http.cookiejar
import io
import re
import tempfile
from typing import BinaryIO, List, Optional, TextIO

import bs4
import requests
from furryposter.story import Story
from furryposter.utilities import markdownformatter
from furryposter.websites.website import (AuthenticationError, Website,
                                          WebsiteError)
from selenium import webdriver
from selenium.common.exceptions import (InvalidCookieDomainException,
                                        NoSuchElementException,
                                        WebDriverException)
from selenium.webdriver.firefox import options


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

        firefox_options = options.Options()
        firefox_options.headless = True

        try:
            with webdriver.Firefox(options=firefox_options) as driver:
                driver.set_window_size(1120, 550)

                driver.get('http://www.furaffinity.net/')

                for cookie in self.cookie:
                    cookie_dict = {
                        'domain': cookie.domain,
                        'name': cookie.name,
                        'value': cookie.value,
                        'secure': cookie.secure}
                    if cookie.expires:
                        cookie_dict['expiry'] = cookie.expires
                    if cookie.path_specified:
                        cookie_dict['path'] = cookie.path
                    try:
                        driver.add_cookie(cookie_dict)
                    except InvalidCookieDomainException:
                        pass

                driver.get('https://www.furaffinity.net/submit/')

                # first section: type selection
                driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/form/section/div[2]/h4[3]/label').click()
                driver.find_element_by_xpath(
                    '/html/body/div[3]/div[2]/div/div/form/section/div[2]/div[2]/button').click()

                # second section: file upload
                # selenium can only work with an actual file, so use tempfile
                try:
                    tmpstory = tempfile.NamedTemporaryFile(mode='w', suffix='.txt')
                    tmpstory.write(story.read())
                    if thumbnail:
                        tmpthumbnail = tempfile.NamedTemporaryFile(suffix='.png')
                        tmpthumbnail.write(thumbnail.read())

                        driver.find_element_by_xpath(
                            '/html/body/div[3]/div[2]/div/div/form/section/div[2]/input[2]').send_keys(tmpthumbnail.name)
                    driver.find_element_by_xpath(
                        '/html/body/div[3]/div[2]/div/div/form/section/div[2]/input[1]').send_keys(tmpstory.name)

                    driver.find_element_by_xpath(
                        '/html/body/div[3]/div[2]/div/div/form/section/div[2]/div/button').click()
                finally:
                    tmpstory.close()
                    if thumbnail:
                        tmpthumbnail.close()

                # third section: story details
                # make the story explicit
                driver.find_element_by_xpath(
                    '/html/body/div[3]/div[2]/div/div/div/form/section[1]/div[2]/div/div/div[1]/label[3]/input').click()
                driver.find_element_by_xpath('//*[@id="title"]').send_keys(title)
                driver.find_element_by_xpath('//*[@id="message"]').send_keys(description)
                driver.find_element_by_xpath('//*[@id="keywords"]').send_keys(tags)
                driver.find_element_by_xpath('//*[@id="finalize"]').click()
        except NoSuchElementException as e:
            pass

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
