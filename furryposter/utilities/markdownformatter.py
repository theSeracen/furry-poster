"""Module for converting a markdown file"""

import os
import re

def findFiles(directory: str):
	files = os.listdir(directory)
	#create list of all markdown files in directory
	markdowns = [(directory + '\\' + file) for file in files if file.endswith('.mmd')]
	for markdownfile in markdowns:
		formatFileBBcode(markdownfile)

def parseStringBBcode(line: str) -> str:
	"""Takes a string of markdown formatting and converts it to BBcode"""
	formattingFunctions = [linkMarkdowntoBBcode, strongMarkdowntoBBcode, boldMarkdowntoBBcode, italicMarkdowntoBBcode]
	for formatFunc in formattingFunctions:
		line = formatFunc(line)
	return line

def linkMarkdowntoBBcode(line: str) -> str:
	simple = r'\[(.*?)\]\(((http|www)?.*?)\)'
	complex = r'<(.*?)>'
	subs = []
	for match in re.findall(r'(({})|({}))'.format(simple, complex), line):
		match = match[0]
		#first format for links
		if re.search(simple, match): 
			link = re.search(simple, match)
			subs.append((re.sub(simple, '[URL=' + link.group(2) + ']' + link.group(1) + '[/URL]',match), match))
		#second format for links
		elif re.search(complex,match):
			link = re.search(complex,match)
			subs.append((re.sub(complex,'[URL]' + link.group(1) + '[/URL]', match), match))

	for (new, old) in subs:
		line = line.replace(old,new)
	return line

def boldMarkdowntoBBcode(line: str) -> str:
	"""Takes a string and returns a single BBcode string with bold formatting"""
	#explode into bold parts
	boldParts = re.split(r'(\*{2,2}.+?\*{2,2})', line)
	for part in range(len(boldParts)):
		if boldParts[part - 1].startswith('**'): boldParts[part - 1] = '[B]' + boldParts[part - 1].lstrip('**')
		if boldParts[part - 1].endswith('**'): boldParts[part - 1] = boldParts[part - 1].rstrip('**') + '[/B]'
	return ''.join(boldParts)

def strongMarkdowntoBBcode(line: str) -> str:
	strongParts = re.split(r'(\*{3,3}.+?\*{3,3})', line)
	for part in range(len(strongParts)):
		if strongParts[part - 1].startswith('***'): strongParts[part - 1] = '[B][I]' + strongParts[part - 1].lstrip('***')
		if strongParts[part - 1].endswith('***'): strongParts[part - 1] = strongParts[part - 1].rstrip('***') + '[/I][/B]'
	return ''.join(strongParts)

def italicMarkdowntoBBcode(line: str) -> str:
	italicParts = re.split(r'(\*{1,1}.+?\*{1,1})', line)
	for part in range(len(italicParts)):
		if italicParts[part - 1].startswith('*'): italicParts[part - 1] = '[I]' + italicParts[part - 1].lstrip('*')
		if italicParts[part - 1].endswith('*'): italicParts[part - 1] = italicParts[part - 1].rstrip('*') + '[/I]'
	return ''.join(italicParts) 

def formatFileBBcode(file: str):
	with open(file,'r', encoding='utf-8') as markdown:
		lines = markdown.readlines()
		formatted = []
		for line in lines:
			line = line.replace('\n','\n\n') #add double lines for each paragraph
			formatted.append(parseStringBBcode(line))
	with open(file.rstrip('.mmd') + 'formatted.txt', 'w') as textfile:
		textfile.writelines(formatted)
			
if __name__ == '__main__':
	line = input('Enter test string: ')
	print(parseStringBBcode(line))