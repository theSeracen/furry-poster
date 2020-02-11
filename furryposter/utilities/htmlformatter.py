"""
Module for converting HTML story files to markdown-formatted text as used on FA and other sites
"""
import bs4
import os

def parseStringBBcode(line: str) -> str:
	"""Parse HTML tags to add BBcode tags to text"""
	toreturn = ''
	if line.text != '': 
		for child in line.children:
			if 'italic' in child.attrs['style']:
				toreturn = toreturn + '[I]' + child.text + '[/I]'
			elif 'bold' in child.attrs['style']:
				toreturn = toreturn + '[B]' + child.text + '[/B]'
			else:
				toreturn = toreturn + child.text
	return toreturn

def parseStringMarkdown(line: str) -> str:
	"""Parse HTML tags to markdown"""
	toreturn = ''
	if line.text != '': 
		for child in line.children:
			if 'italic' in child.attrs['style']:
				toreturn = toreturn + '*' + child.text + '*'
			elif 'bold' in child.attrs['style']:
				toreturn = toreturn + '**' + child.text + '**'
			else:
				toreturn = toreturn + child.text
	return toreturn

def findFiles(directory: str, finalFormat: str):
	"""Function to format all files in a directory"""
	files = os.listdir(directory)
	#create list of all html files in directory
	htmls = [(directory + '\\' + file) for file in files if file.endswith('html')]
	
	for htmlpage in htmls:
		if finalFormat == 'bbbcode':
			formatFileBBcode(htmlpage)
		elif finalFormat == 'markdown':
			formatFileMarkdown(htmlpage)

def formatFileBBcode(htmlfile: str):
	"""Format a specified HTML file"""
	with open(htmlfile, 'r', encoding='utf-8') as file:
		page = bs4.BeautifulSoup(file, 'html.parser')
		paragraphs = page.findAll('p')

		#build list of formatted strings, centring if necessary
		story = [("[center]" + parseStringBBcode(paragraph) + "[/center]" + '\n\n') if ('align' in paragraph.attrs) else (parseStringBBcode(paragraph) + '\n\n') for paragraph in paragraphs]

	with open(htmlfile.split('.')[0] + 'formatted.txt','w',encoding='UTF-8') as storyfile:
		for part in story:
			storyfile.write(part)

def formatFileMarkdown(htmlfile: str):
	"""Format a specified HTML file"""
	with open(htmlfile, 'r', encoding='utf-8') as file:
		page = bs4.BeautifulSoup(file, 'html.parser')
		paragraphs = page.findAll('p')

		#build list of formatted strings, centring if necessary
		story = [("[center]" + parseStringMarkdown(paragraph) + "[/center]" + '\n\n') if ('align' in paragraph.attrs) else (parseStringMarkdown(paragraph) + '\n\n') for paragraph in paragraphs]

	with open(htmlfile.split('.')[0] + 'formatted.md','w',encoding='UTF-8') as storyfile:
		for part in story:
			storyfile.write(part)
	
if __name__ == '__main__':
	directory = input('Please enter a directory: ')
	findFiles(directory)
	print('Conversion Complete')
	input()