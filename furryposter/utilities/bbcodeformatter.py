"""Module for converting BBcode tags"""
import re

def parseStringMarkdown(line: str) -> str:
	"""Converts a string of BBcode to markdown formatting"""
	formattingFunctions = [boldBBcodetoMarkdown, italicsBBcodetoMarkdown, linksBBBcodetoMarkdown]
	for formatfunc in formattingFunctions:
		line = formatfunc(line)
	return line

def __italicsBBcodetoMarkdown(line: str) -> str:
	tags = ['[I]','[i]','[/I]','[/i]']
	for tag in tags:
		line = line.replace(tag, '*')
	return line

def __boldBBcodetoMarkdown(line: str) -> str:
	tags = ['[B]','[b]','[/B]','[/b]']
	for tag in tags:
		line = line.replace(tag, '**')
	return line

def __linksBBBcodetoMarkdown(line: str) -> str:
	simplePattern = r'\[URL\](.*?)\[/URL\]'
	complexPattern = r'\[URL=(.*?)\](.*?)\[/URL\]'
	subs = []
	for match in re.findall(r'(({})|({}))'.format(simplePattern, complexPattern), line):
		match = match[0]
		if re.search(complexPattern, match):
			link = re.search(complexPattern, match)
			subs.append((re.sub(complexPattern,'[' + link.group(2) + '](' + link.group(1) + ')', match), match))

		elif re.search(simplePattern, match):
			link = re.search(simplePattern, match)
			subs.append((re.sub(simplePattern, '<' + link.group(1) + '>', match), match))

	for (new, old) in subs:
		line = line.replace(old, new)
	return line

if __name__ == '__main__':
	line = input('Enter test string: ')
	print(parseStringMarkdown(line))