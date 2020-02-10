"""Module for converting BBcode tags"""
import re

def parseStringMarkdown(line):
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
	if re.search(r'\[URL=(.*)\](.*)\[/URL\]', line):
		link = re.search(r'\[URL=(.*)\](.*)\[/URL\]', line)
		return re.sub(r'\[URL=(.*)\](.*)\[/URL\]','[' + link.group(2) + '](' + link.group(1) + ')', line)
	elif re.search(r'\[URL\](.*)\[/URL\]',line):
		link = re.search(r'\[URL\](.*)\[/URL\]',line)
		return re.sub(r'\[URL\](.*)\[/URL\]','[URL]' + link.group(1) + '[/URL]', line)
	else:
		return line

if __name__ == '__main__':
	line = input('Enter test string: ')
	print(parseStringMarkdown(line))