import argparse
from furryposter.websites import sofurry, weasyl, furaffinity
from furryposter.websites.website import AuthenticationError, WebsiteError, Website
import os
import re
import http.cookiejar
from io import StringIO, TextIOWrapper, BufferedReader
from typing import Optional
from furryposter.utilities.thumbnailgen import thumbnailerrors
from furryposter.story import Story

parser = argparse.ArgumentParser(prog="furrystoryuploader", description="Post stories to furry websites")

def initParser():
	thumbGroup = parser.add_mutually_exclusive_group()
	parser.add_argument('directory', metavar='D')
	parser.add_argument('-i','--ignore-errors', action='store_true', help='Ignore all errors and continue with other sites')
	parser.add_argument('-f', '--format', choices =['html','markdown','text', 'bbcode'], default='markdown', help='Format of the source story file. Default is markdown')
	parser.add_argument('-m', '--messy', action='store_true', help='Flag to cause all converted files to be written to disk rather than kept in memory')
	thumbGroup.add_argument('-g', '--generate-thumbnail', default=False, const='default', nargs='?', help='Flag causes a thumbnail to be dynamically generated. The default profile is used in thumbnail.config unless specified')

	#site flags
	parser.add_argument('-F','--furaffinity', action='store_true', help="Flag for whether FurAffinity should be tried")
	parser.add_argument('-S','--sofurry', action='store_true', help="Flag for whether SoFurry should be tried")
	parser.add_argument('-W','--weasyl',action='store_true', help="Flag for whether Weasyl should be tried")

	#story details
	parser.add_argument('-t','--title', help="String for the title of the story")
	parser.add_argument('-d','--description', help="String for the description of the story")
	parser.add_argument('-k','--tags', help="List of CSV for the story tags")
	thumbGroup.add_argument('-p', '--thumbnail', action='store_true', help="Flag for whether a thumbnail is present and should be used")
	parser.add_argument('-s', '--post-script', action='store_true', help='Flag to look for a post-script.txt to add to the end of the description')
	parser.add_argument('-r', '--rating', choices=['general','adult'], default='adult', help="Rating for the story; choice between 'general' and 'adult'; defaults to adult")

	parser.add_argument('--test', action='store_true', help='debugging flag; if included, the program will do everything but submit')


def initSite(regexString: str, site: Website, ignore_errors: bool) -> Optional[Website]:
	"""Initialise site with cookies"""

	cookiesLoc = None
	for file in os.listdir(os.getcwd()):
		if re.match(regexString, file):
			cookiesLoc = file
			break
	if cookiesLoc is None:
		if ignore_errors is False:
			raise AuthenticationError('{} cannot find a cookies file'.format(site.name))
		else:
			print('{}{} cannot find cookies; the site will be skipped'.format('[Site Init]\t', site.name))
	else:
		site.load(cookiesLoc)
		try:
			site.testAuthentication()
		except AuthenticationError as e:
			if ignore_errors is True:
				print('{} authentication failed!\nContinuing...'.format(site.name))
			else:
				raise
		else:
			print('{}{} successfully authenticated'.format('[Site Init]\t', site.name))
			return site
	return None


def main():
	initParser()
	args = parser.parse_args()

	sites = []
	if args.furaffinity:
		sites.append(initSite(r'^(furaffinity|fa)?(cookies?)?\.txt', furaffinity.FurAffinity(), args.ignore_errors))

	if args.sofurry:
		sites.append(initSite(r'^(sofurry|sf)?(cookies?)?\.txt', sofurry.SoFurry(), args.ignore_errors))
						
	if args.weasyl:
		sites.append(initSite(r'^(weasyl|ws)?(cookies?)?\.txt', weasyl.Weasyl(), args.ignore_errors))
	
	sites = filter(None, sites)

	stage = '[Loading]\t'

	#now we can go into checking for all the required items
	if os.path.isdir(args.directory) is False: raise Exception("Valid directory required")

	if args.title is None: args.title = input('Please enter a title: ')
	if args.description is None: args.description = input('Please enter a description: ')
	if args.tags is None: args.tags = input('Please enter CSV tags: ')

	args.description = args.description.replace('\\n', '\n') #replaces newline from manual input as it doesn't add an escape
	
	#error checking
	if args.title == '': raise Exception('No title specified!')
	if args.description == '': raise Exception('No description specified!')
	if args.tags == '': raise Exception('No tags specified!')
	if args.post_script:
		if os.path.exists('post-script.txt'):
			print('{}Post-script found'.format(stage))
			with open('post-script.txt','r',encoding='utf-8') as post:
				args.description = args.description + '\n\n' + ''.join(post.readlines())
		else:
			if args.ignore_errors:
				print('{}Post-script file cannot be loaded!\nContinuing...'.format(stage))
			else:
				raise Exception('Post-script file cannot be found')
	
	submission = Story(args.format, args.title, args.description, args.tags)
	#determine file type to look for
	storyLoc = None
	args.format = args.format.lower()
	if args.format == 'text' or args.format == 'bbcode':
		ends = ['.txt']
	elif args.format == 'markdown':
		ends = ['.mmd','.md']
	elif args.format == 'html':
		ends = ['.html']

	for file, ending in ((file, ending) for ending in ends for file in os.listdir(args.directory)):
		if file.endswith(ending): 
			storyLoc = args.directory + '\\' + file
			print('{}File found: {}'.format(stage, storyLoc))
			break
	if storyLoc is None: raise Exception('No story file of format {} found!'.format(args.format))

	submission.loadContent(open(storyLoc, 'r', encoding='utf-8'))

	#get thumbnail
	if args.generate_thumbnail:
		try:
			submission.loadThumbnail(args.generate_thumbnail)
			if args.messy:
				print('{}Saving thumbnail to file...'.format(stage))
				with open(args.directory + '\\thumbnail.png', 'wb') as file:
					file.write(submission.giveThumbnail().getvalue())
		except thumbnailerrors.ThumbnailSizingError:
			if args.ignore_errors:
				print('{}Thumbnail generation has failed!'.format(stage))
				thumbnailPass = None
			else:
				raise
	else:
		thumbnailLoc = None
		if args.thumbnail:
			for file in os.listdir(args.directory):
				if re.match('.*\\.(png|jpg)', file):
					thumbnailLoc = args.directory + '\\' + file
					print('{}Thumbnail file found'.format(stage))
					submission.loadThumbnail(open(thumbnailLoc, 'rb'))
					break
			if thumbnailLoc is None:
				if args.ignore_errors:
					print('{}No thumbnail found!\nContinuing...'.format(stage))
				else:
					raise Exception('No thumbnail file found!')

	#submit the files to each website
	for site in sites:
		if args.messy:
			if site.preferredFormat == 'bbcode':
				with open(''.join(storyLoc.split('.')[:-1]) + 'bbcode.txt', 'w', encoding='utf-8') as file:
					file.write(submission.giveStory('bbcode').getvalue())
			elif site.preferredFormat == 'markdown':
				with open(''.join(storyLoc.split('.')[:-1]) + '.md', 'w', encoding='utf-8') as file:
					file.write(submission.giveStory('markdown').getvalue())
		try:
			stage = '[Posting]\t'
			print('{}Beginning {} submission'.format(stage, site.name))
			if args.test: print('{}test: {} bypassed'.format(stage, site.name))
			else: site.submitStory(submission.title, submission.giveDescription(site.preferredFormat), submission.tags, args.rating, submission.giveStory(site.preferredFormat), submission.giveThumbnail())
			print('{}{} submission completed successfully'.format(stage, site.name))
		except WebsiteError as e:
			if args.ignore_errors: print('{} has failed with exception {}'.format(site.name, e))
			else: raise

if __name__ == '__main__':
	main()