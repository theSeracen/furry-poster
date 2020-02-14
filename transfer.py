import argparse
import os
from furryposter.story import Story
from furryposter.websites import furaffinity, sofurry, weasyl
from furryposter.websites.website import Website
import builtins

stage = '[init]\t'
def print(inp: str): builtins.print(stage + inp)
def setstage(newstage:str):
	global stage
	stage = '[{}]\t'.format(newstage)

parser = argparse.ArgumentParser(prog="furrytransfer", description="Transfer galleries between furry sites")


def initParser():
	parser.add_argument('source', metavar='S', choice=['furaffinity','sofurry','weasyl'], help='site with gallery')
	parser.add_argument('destination', metavar='D', choice=['furaffinity','sofurry','weasyl'], help='site to transfer to')
	parser.add_argument('name', metavar='N', help='the name of the user to copy the gallery from')

	parser.add_argument('-d', '--delay', type=int, default=5, help='seconds between posts to new site')
	parser.add_argument('-t', '--thumbnail-behaviour', choice=['new', 'source', 'none'], default='new')
	parser.add_argument('--test', help = 'Aborts actual upload')

def main():
	initParser()
	args = parser.parse_args()
	if args.source == args.destination:
		raise Exception('Source and destination sites cannot be the same')
	if args.source == 'sofurry' and args.thumbnail_behaviour == 'source':
		print('Default thumbnails are generated in all Sofurry submissions and these cannot be distinguished from uploaded thumbnails. Do you wish to continue with this in mind?')
		response = input('(Yes/No): ')
		if 'n' in response.lower():
			print('Aborting...')
			exit(1)
	
	source = determineSite(args.source)
	dest = determineSite(args.destination)
	setstage('scanning')
	print('Confirmation required: Do you want to scan the gallery of {} on site {}?'.format(args.name, source.name))
	response = input('(Yes/No): ')
	if 'n' in response.lower():
		print('Aborting...')
		exit(0)

	sourceSubmissions = source.crawlGallery(args.name)
	print('{} submissions in source gallery found'.format(len(sourceSubmissions)))
	destSubmissions = dest.crawlGallery(args.name)
	print('{} submissions already in destination gallery'.format(len(destSubmissions)))

	sourceStories = [source.parseSubmission(sub) for sub in sourceSubmissions]
	destStories = [dest.parseSubmission(sub) for sub in destSubmissions]
	setstage('transfer')
	destTitles = [story.title for story in destStories]
	
	for story, place in enumerate(sourceStories):
		if story.title in destTitles:
			print('Skipping {} of {}: {} found in destination gallery'.format(place, len(sourceStories), story.title))
		else:
			if args.test: pass
			else:
				if args.thumbnail_behaviour == 'new': story.forceGenThumbnail()
				elif args.thumbnail_behaviour == 'none': story.thumbnail = None

				print('Transferring {} of {}: {}'.format(place, len(sourceStories), story.title))
				dest.submitStory(story.title, story.giveDescription(dest.preferredFormat), story.tags, story.rating, story.giveStory(dest.preferredFormat), story.giveThumbnail())


def determineSite(site: str) -> Website:
	if site == 'furaffinity': 
		site = furaffinity.FurAffinity()
		site.load(__findCookies(site.cookiesRegex))
	elif site == 'sofurry': 
		site = sofurry.SoFurry()
		site.load(__findCookies(site.cookiesRegex))
	elif site == 'weasyl': 
		site = weasyl.Weasyl()
		site.load(__findCookies(site.cookiesRegex))
	else: raise Exception("Website '{}' unrecognised".format(site))

def __findCookies(regex: str) -> str:
	for file in os.listdir(os.getcwd()):
		if re.match(regex, file):
			cookiesLoc = file
			break
if __name__ == '__main__':
	main()