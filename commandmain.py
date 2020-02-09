import argparse
from furryposter.websites import sofurry, weasyl, furaffinity
from furryposter.websites.website import AuthenticationError, WebsiteError
from furryposter.utilities import htmlformatter, markdownformatter
import os
import re
import http.cookiejar

parser = argparse.ArgumentParser(prog="furrystoryuploader", description="Post stories to furry websites")

def initParser():
	parser.add_argument('directory', metavar='D')
	parser.add_argument('-i','--ignore-errors', action='store_true', help='Ignore all errors and continue with other sites')

	#site flags
	parser.add_argument('-F','--furaffinity', action='store_true', help="Flag for whether FurAffinity should be tried")
	parser.add_argument('-S','--sofurry', action='store_true', help="Flag for whether SoFurry should be tried")
	parser.add_argument('-W','--weasyl',action='store_true', help="Flag for whether Weasyl should be tried")

	#story details
	parser.add_argument('-t','--title', help="String for the title of the story")
	parser.add_argument('-d','--description', help="String for the description of the story")
	parser.add_argument('-k','--tags', help="List of CSV for the story tags")
	parser.add_argument('-p', '--thumbnail', action='store_true', help="Flag for whether a thumbnail is present and should be used")
	parser.add_argument('-c', '--convert', action='store_true',help='Flag for whether a HTML file should be directed')
	parser.add_argument('-f','--format', choices =['html','markdown'], default='html', help='Option to choose the source story file format. Default is HTML')

def main():
	initParser()
	args = parser.parse_args()
	sites = []
	if args.furaffinity:
		fa = None
		for file in os.listdir(os.getcwd()):
			if re.match("^(furaffinity|fa)?(cookies?)?\.txt", file):
				cj = http.cookiejar.MozillaCookieJar(file)
				cj.load()
				fa = furaffinity.FurAffinity(cj)
				break
		if fa is None:
			if args.ignore_errors is False:
				raise AuthenticationError('Furaffinity cannot find a cookies file')
			else:
				print('FA cannot find cookies; the site will be skipped')
		else:
			try:
				fa.testAuthentication()
			except AuthenticationError as e:
				if args.ignore_errors is True:
					print('FA authentication failed!\nContinuing...')
				else:
					raise
			else:
				sites.append(fa)
				print('FurAffinity successfully authenticated')
	if args.sofurry:
		sf = None
		for file in os.listdir(os.getcwd()):
			if re.match("^(sofurry|sf)?(cookies?)?\.txt", file):
				cj = http.cookiejar.MozillaCookieJar(file)
				cj.load()
				sf = sofurry.SoFurry(cj)
				break
		if sf is None:
			if args.ignore_errors is False:
				raise AuthenticationError('SoFurry cannot find a cookies file')
			else:
				print('SoFurry cannot find cookies; the site will be skipped')
		else:
			try:
				sf.testAuthentication()
			except AuthenticationError as e:
				if args.ignore_errors is True:
					print('SoFurry authentication failed!\nContinuing...')
				else:
					raise
			else:
				sites.append(sf)
				print('SoFurry successfully authenticated')
	if args.weasyl:
		ws = None
		for file in os.listdir(os.getcwd()):
			if re.match("^(weasyl|ws)?(cookies?)?\.txt", file):
				cj = http.cookiejar.MozillaCookieJar(file)
				cj.load()
				ws = weasyl.Weasyl(cj)
				break
		if ws is None:
			if args.ignore_errorss is False:
				raise AuthenticationError('Weasyl cannot find a cookies file')
			else:
				print('Weasyl cannot find cookies; the site will be skipped')
		else:
			try:
				ws.testAuthentication()
			except AuthenticationError as e:
				if args.ignore_errors is True:
					print('Weasyl authentication failed!\nContinuing...')
				else:
					raise
			else:
				sites.append(ws)
				print('Weasyl successfully authenticated')

	#now we can go into checking for all the required items
	if os.path.isdir(args.directory) is False: raise Exception("Valid directory required")

	if args.title is None: args.title = input('Please enter a title: ')
	if args.description is None: args.description = input('Please enter a description: ')
	if args.tags is None: args.tags = input('Please enter CSV tags: ')

	#error checking
	if args.title == '': raise Exception('No title specified!')
	if args.description == '': raise Exception('No description specified!')
	if args.tags == '': raise Exception('No tags specified!')

	if args.convert:
		print('Story conversion commencing...')
		if args.format.lower() == 'html': htmlformatter.findFiles(args.directory)
		if args.format.lower() == 'markdown': markdownformatter.findFiles(args.directory)
	
	#prioritise formatted stories
	storyLoc = None
	ends = ['formatted.txt','.txt']
	for file, ending in ((file, ending) for ending in ends for file in os.listdir(args.directory)):
		if file.endswith(ending): 
			storyLoc = args.directory + '\\' + file
			print('Formatted file found: {}'.format(storyLoc))
			break

	if storyLoc is None: raise Exception('No story file found!')

	#get thumbnail
	thumbnailLoc = None
	if args.thumbnail:
		for file in os.listdir(args.directory):
			if re.match('.*\.(png|jpg)', file):
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

			print('Beginning {} submission'.format(site.name))
			site.submitStory(args.title, args.description, args.tags, open(storyLoc, 'r',encoding='utf-8'), thumbnailPass)
			print('{} submission completed successfully'.format(site.name))
		except WebsiteError as e:
			if args.ignore_errors: print('{} has failed with exception {}'.format(site.name, e))
			else: raise

if __name__ == '__main__':
	main()