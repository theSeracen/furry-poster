import argparse
from websites import sofurry, weasyl, furaffinity
from websites.website import AuthenticationError, WebsiteError
import os, re, http.cookiejar

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

def main():
	initParser()
	args = parser.parse_args()
	sites = []
	if args.furaffinity:
		fa = None
		for file in os.listdir(os.getcwd()):
			if re.match("(furaffinity|fa)*(cookie)?.*\.txt", file) is not None:
				fa = furaffinity.FurAffinity(http.cookiejar.MozillaCookieJar(file))
				break
		if fa is None:
			if args.ignore-errors is False:
				raise AuthenticationError('Furaffinity cannot find a cookies file')
			else:
				print('FA cannot find cookies; the site will be skipped')
		else:
			try:
				fa.testAuthentication()
			except AuthenticationError as e:
				if args.ignore-error is True:
					print('FA authentication failed!\nContinuing...')
				else:
					raise
			else:
				sites.append(fa)
	if args.sofurry:
		sf = None
		for file in os.listdir(os.getcwd()):
			if re.match("(sofurry|sf)*(cookie)?.*\.txt", file) is not None:
				sf = sofurry.SoFurry(http.cookiejar.MozillaCookieJar(file))
				break
		if sf is None:
			if args.ignore-errors is False:
				raise AuthenticationError('SoFurry cannot find a cookies file')
			else:
				print('SoFurry cannot find cookies; the site will be skipped')
		else:
			try:
				sf.testAuthentication()
			except AuthenticationError as e:
				if args.ignore-error is True:
					print('SoFurry authentication failed!\nContinuing...')
				else:
					raise
			else:
				sites.append(sf)
	if args.weasyl:
		ws = None
		for file in os.listdir(os.getcwd()):
			if re.match("(weasyl|ws)*(cookie)?.*\.txt", file) is not None:
				ws = weasyl.Weasyl(http.cookiejar.MozillaCookieJar(file))
				break
		if ws is None:
			if args.ignore-errors is False:
				raise AuthenticationError('Weasyl cannot find a cookies file')
			else:
				print('Weasyl cannot find cookies; the site will be skipped')
		else:
			try:
				ws.testAuthentication()
			except AuthenticationError as e:
				if args.ignore-error is True:
					print('Weasyl authentication failed!\nContinuing...')
				else:
					raise
			else:
				sites.append(ws)

if __name__ == '__main__':
	main()