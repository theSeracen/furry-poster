import argparse
from furryposter.websites import sofurry, weasyl, furaffinity
from furryposter.websites.website import AuthenticationError, WebsiteError, Website
from furryposter.utilities import htmlformatter, markdownformatter, bbcodeformatter
import os
import re
import http.cookiejar
from io import StringIO
from typing import Optional

parser = argparse.ArgumentParser(prog="furrystoryuploader", description="Post stories to furry websites")

def initParser():
	parser.add_argument('directory', metavar='D')
	parser.add_argument('-i','--ignore-errors', action='store_true', help='Ignore all errors and continue with other sites')
	parser.add_argument('-f', '--format', choices =['html','markdown','text', 'bbcode'], default='markdown', help='Format of the source story file. Default is markdown')

	#site flags
	parser.add_argument('-F','--furaffinity', action='store_true', help="Flag for whether FurAffinity should be tried")
	parser.add_argument('-S','--sofurry', action='store_true', help="Flag for whether SoFurry should be tried")
	parser.add_argument('-W','--weasyl',action='store_true', help="Flag for whether Weasyl should be tried")

	#story details
	parser.add_argument('-t','--title', help="String for the title of the story")
	parser.add_argument('-d','--description', help="String for the description of the story")
	parser.add_argument('-k','--tags', help="List of CSV for the story tags")
	parser.add_argument('-p', '--thumbnail', action='store_true', help="Flag for whether a thumbnail is present and should be used")
	parser.add_argument('-s', '--post-script', action='store_true', help='Flag to look for a post-script.txt to add to the end of the description')
	parser.add_argument('-r', '--rating', choices=['general','adult'], default='adult', help="Rating for the story; choice between 'general' and 'adult'; defaults to adult")

	parser.add_argument('--test', action='store_true', help='debugging flag; if included, the program will do everything but submit')


def siteUpload(cj_path: str, site: Website, ignore_errors: bool ) -> Optional[Website]:
	loaded = False
	if cj_path is not None:
		cj = http.cookiejar.MozillaCookieJar(cj_path)
		cj.load()
		site.load(cj)
		loaded = True
	
	if loaded is False:
		if ignore_errors is False:
			raise AuthenticationError('{} cannot find a cookies file'.format(site.name))
		else:
			print('{} cannot find cookies; the site will be skipped'.format(site.name))
	else:
		try:
			site.testAuthentication()
		except AuthenticationError as e:
			if ignore_errors is True:
				print('{} authentication failed!\nContinuing...'.format(site.name))
			else:
				raise
		else:
			print('{} successfully authenticated'.format(site.name))
			return site
			
	return None


def main():
	initParser()
	args = parser.parse_args()
	sites = []
	if args.furaffinity:
		for file in os.listdir(os.getcwd()):
			if re.match(r'^(furaffinity|fa)?(cookies?)?\.txt', file):
				sites.append(siteUpload(file, furaffinity.FurAffinity(), args.ignore_errors))
				break
				
	if args.sofurry:
		for file in os.listdir(os.getcwd()):
			if re.match(r'^(sofurry|sf)?(cookies?)?\.txt', file):
				sites.append(siteUpload(file, sofurry.SoFurry(), args.ignore_errors))
				break
				
	if args.weasyl:
		for file in os.listdir(os.getcwd()):
			if re.match(r'^(weasyl|ws)?(cookies?)?\.txt', file):
				sites.append(siteUpload(file, weasyl.Weasyl(), args.ignore_errors))
				break
	
	sites = list(filter(None, sites))

	#now we can go into checking for all the required items
	if os.path.isdir(args.directory) is False: raise Exception("Valid directory required")

	if args.title is None: args.title = input('Please enter a title: ')
	if args.description is None: args.description = input('Please enter a description: ')
	if args.tags is None: args.tags = input('Please enter CSV tags: ')

	#error checking
	if args.title == '': raise Exception('No title specified!')
	if args.description == '': raise Exception('No description specified!')
	if args.tags == '': raise Exception('No tags specified!')

	if args.post_script:
		if os.path.exists('post-script.txt'):
			with open('post-script.txt','r',encoding='utf-8') as post:
				args.description = args.description + '\n\n' + ''.join(post.readlines())
		else:
			if args.ignore_errors:
				print('Post-script file cannot be loaded!\nContinuing...')
			else:
				raise Exception('Post-script file cannot be found')
	
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
			print('File found: {}'.format(storyLoc))
			break

	if storyLoc is None: raise Exception('No story file of format {} found!'.format(args.format))

	#get thumbnail
	thumbnailLoc = None
	if args.thumbnail:
		for file in os.listdir(args.directory):
			if re.match('.*\\.(png|jpg)', file):
				thumbnailLoc = args.directory + '\\' + file
				print('Thumbnail file found')
				break
		if thumbnailLoc is None:
			if args.ignore_errors:
				print('No thumbnail found!\nContinuing...')
			else:
				raise Exception('No thumbnail file found!')

	#submit the files to each website
	for site in sites:
		try:
			if thumbnailLoc is None: thumbnailPass = None
			else: thumbnailPass = open(thumbnailLoc, 'rb')

			#convert the description if necessary
			if site.preferredFormat == 'bbcode':
				print('Converting description to bbcode...')
				args.description = markdownformatter.parseStringBBcode(args.description)

			#handle the story files
			if site.preferredFormat == args.format or args.format == 'text':
				story = open(storyLoc, 'r',encoding='utf-8')
			else:
				loadedStory = ''.join(open(storyLoc, 'r',encoding='utf-8').readlines())
				#determine the type and convert
				if args.format == 'bbcode':
					if site.preferredFormat == 'markdown':
						print('Converting story to markdown...')
						story = StringIO(bbcodeformatter.parseStringMarkdown(loadedStory))
					else:
						raise Exception('Cannot convert BBcode to the format {}'.format(site.preferredFormat))
				elif args.format == 'markdown':
					if site.preferredFormat == 'bbcode':
						print('Converting story to bbcode...')
						story = StringIO(markdownformatter.parseStringBBcode(loadedStory))
					else:
						raise Exception('Cannot convert markdown to the format'.format(site.preferredFormat))
				elif args.format == 'html':
					if site.preferredFormat == 'bbcode':
						print('Converting story to bbcode...')
						story = StringIO(''.join(htmlformatter.formatFileBBcode(StringIO(loadedStory))))
					elif site.preferredFormat == 'markdown':
						print('Converting story to markdown...')
						story = StringIO(''.join(htmlformatter.formatFileMarkdown(StringIO(loadedStory))))
					else:
						raise Exception('Cannot convert HTML to the format'.format(site.preferredFormat))

			print('Beginning {} submission'.format(site.name))
			if args.test: print('test: {} bypassed'.format(site.name))
			else: site.submitStory(args.title, args.description, args.tags, args.rating, story, thumbnailPass)
			print('{} submission completed successfully'.format(site.name))
		except WebsiteError as e:
			if args.ignore_errors: print('{} has failed with exception {}'.format(site.name, e))
			else: raise

if __name__ == '__main__':
	main()