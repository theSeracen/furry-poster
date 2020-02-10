"""Module for converting BBcode tags"""
import re

def parseStringMarkdown(line):
	"""Converts a string of BBcode to markdown formatting"""
	formattingFunctions = [boldBBcodetoMarkdown, italicsBBcodetoMarkdown, linksBBBcodetoMarkdown]
	for formatfunc in formattingFunctions:
		line = formatfunc(line)
	return line

def italicsBBcodetoMarkdown(line):
	tags = ['[I]','[i]','[/I]','[/i]']
	for tag in tags:
		line = line.replace(tag, '*')
	return line

def boldBBcodetoMarkdown(line):
	tags = ['[B]','[b]','[/B]','[/b]']
	for tag in tags:
		line = line.replace(tag, '**')
	return line

def linksBBBcodetoMarkdown(line):
	simplePattern = r'\[URL\](.*?)\[/URL\]'
	complexPattern = r'\[URL=(.*?)\](.*?)\[/URL\]'
	if re.search(complexPattern, line):
		link = re.search(complexPattern, line)
		return re.sub(complexPattern,'[' + link.group(2) + '](' + link.group(1) + ')', line)
	elif re.search(simplePattern,line):
		link = re.search(simplePattern,line)
		return re.sub(simplePattern,'<' + link.group(1) + '>', line)
	else:
		return line

if __name__ == '__main__':
	line = input('Enter test string: ')
	print(parseStringMarkdown(line))