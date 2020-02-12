import configparser
from PIL import Image, ImageDraw, ImageFont
from typing import List
from io import BytesIO

configs = None

def createBase() -> Image:
	"""Create the thumbnail base"""
	backcolour = tuple((int(val) for val in configs.get('backcolour').split(', ')))
	base = Image.new('RGB', (configs.getint('width'), configs.getint('height')), backcolour)
	return base

def addText(title: str, tags: List[str], base: Image) -> Image:
	"""Add the title and tags to the base image"""
	#find the best size for the title
	titlesize = 5
	titleStart = tuple((int(val) for val in configs.get('titleStartCoords').split(', ')))
	font = ImageFont.truetype("arial.ttf", titlesize)
	while font.getsize_multiline(title)[0] < (configs.getint('width') - titleStart[0]):
		titlesize += 1
		font = ImageFont.truetype("arial.ttf", titlesize)
	font = ImageFont.truetype("arial.ttf", titlesize-1)

	titleColour = tuple((int(val) for val in configs.get('titleColour').split(', ')))

	drawer = ImageDraw.Draw(base)

	drawer.multiline_text(titleStart, title, titleColour, font, align='center')
	titlewidth, titleheight = font.getsize_multiline(title)

	starty = titleheight + int(configs.getint('titleTagSepDist'))
	tagsize = 5
	tags = '\n'.join(tags)
	font = ImageFont.truetype('arial.ttf', tagsize)
	while font.getsize_multiline(tags)[1] <= (500 - starty - configs.getint('tagBottomBorder')):
		if (tagsize == titlesize - configs.getint('titleTagMinSizeDiff')) or (font.getsize_multiline(tags)[0] >= (base.width * 0.9)):
			break
		tagsize += 1
		font = ImageFont.truetype('arial.ttf', tagsize)

	tagswidth, tagsheight = font.getsize_multiline(tags)
	startx = (base.width - tagswidth) / 2
	font = ImageFont.truetype('arial.ttf', tagsize - 1)
	tagColour = tuple((int(val) for val in configs.get('tagColour').split(', ')))
	drawer.multiline_text((startx, starty), tags, tagColour, font, align='center')
	return base

def makeThumbnail(title: str, tags: List[str], configSection: str = 'DEFAULT') -> BytesIO:
	parsedOptions = configparser.ConfigParser()
	parsedOptions.read_file(open(r'.\furryposter\utilities\thumbnailgen\thumbnail.config', 'r', encoding='utf-8'))
	global configs
	try:
		configs = parsedOptions[configSection]
	except KeyError:
		print('No valid config found under {}'.format(configSection))
		raise

	if len(tags) > configs.getint('maxTags'):
		tags = tags[:configs.getint('maxTags')]

	thumbnail = createBase()
	thumbnail = addText(title, tags, thumbnail)
	thumbfile = BytesIO()
	thumbnail.save(thumbfile, 'PNG')
	return thumbfile

if __name__ == '__main__':
	title = input('Enter title: ')
	title = title.replace('\\n', '\n')
	tags = input('Enter tags as CSV: ')
	destination = input('Enter target directory: ')
	thumbfile = makeThumbnail(title, tags.split(', '))
	with open(destination + '\\' + 'thumbnail.png', 'wb') as file:
		file.write(thumbfile.getbuffer())