import configparser
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
from io import BytesIO
from furryposter.utilities.thumbnailgen.thumbnailerrors import *

configs = None


def __createBase() -> Image:
    """Create the thumbnail base"""
    backcolour = tuple((int(val)
                        for val in configs.get('backcolour').split(', ')))
    base = Image.new(
        'RGB',
        (configs.getint('width'),
         configs.getint('height')),
        backcolour)
    return base


def __determineOptimalTextSize(
        text: str,
        maxSize: int,
        doingTags: bool) -> int:
    """Function to find the biggest text size that fits in the given space"""
    textSize = 5
    if doingTags:
        sizeIndex = 1
    else:
        sizeIndex = 0
    font = ImageFont.truetype(
        '/usr/share/fonts/truetype/freefont/FreeMono.ttf',
        textSize)
    while font.getsize_multiline(text)[sizeIndex] < maxSize:
        if doingTags:
            if font.getsize_multiline(text)[0] >= (
                    configs.getint('width') *
                    0.75):  # make sure that it doesn't cover more than 75% of width
                break
        textSize += 1
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/freefont/FreeMono.ttf", textSize)

    return textSize - 1


def __findOptimalTitle(title: str) -> Tuple[str, int]:
    """Function to split up long titles into multiline strings to get the best size"""
    titleCut = -1
    titleStart = tuple((int(val)
                        for val in configs.get('titleStartCoords').split(', ')))

    titleSize = __determineOptimalTextSize(
        title, (configs.getint('width') - titleStart[0]), False)
    text = title
    while titleSize < configs.getint('minTitleSize'):
        text = title.split(' ')
        if abs(titleCut) >= len(text):
            raise ThumbnailSizingError('Cannot find best title size')
        text = ' '.join(text[:titleCut]) + '\n' + \
            ' '.join(text[titleCut:]).replace('\n', ' ')

        titleSize = __determineOptimalTextSize(
            text, (configs.getint('width') - titleStart[0]), False)
        titleCut -= 1

    return text, titleSize


def __addText(title: str, tags: List[str], base: Image) -> Image:
    """Add the title and tags to the base image"""
    # find the best size for the title
    titleStart = tuple((int(val)
                        for val in configs.get('titleStartCoords').split(', ')))

    title, titlesize = __findOptimalTitle(title)
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
        titlesize)

    # max out the size and then centre if too big
    if titlesize > configs.getint('maxTitleSize'):
        titlesize = configs.getint('maxTitleSize')
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/freefont/FreeMono.ttf", titlesize)
        wid, hei = font.getsize_multiline(title)
        newTitlex = (base.width - wid) / 2
        titleStart = (newTitlex, titleStart[1])

    titleColour = tuple((int(val)
                         for val in configs.get('titleColour').split(', ')))

    drawer = ImageDraw.Draw(base)

    drawer.multiline_text(titleStart, title, titleColour, font, align='center')
    titlewidth, titleheight = font.getsize_multiline(title)

    starty = titleheight + int(configs.getint('titleTagSepDist'))
    tags = '\n'.join(tags)
    tagsize = __determineOptimalTextSize(tags, (configs.getint(
        'width') - starty - configs.getint('tagBottomBorder')), True)
    # if the tags are too close in size to the title, reduce
    if abs(titlesize - tagsize) <= 10:
        tagsize = titlesize - 11

    font = ImageFont.truetype(
        '/usr/share/fonts/truetype/freefont/FreeMono.ttf', tagsize)

    tagswidth, tagsheight = font.getsize_multiline(tags)
    startx = (base.width - tagswidth) / 2
    font = ImageFont.truetype(
        '/usr/share/fonts/truetype/freefont/FreeMono.ttf',
        tagsize - 1)
    tagColour = tuple((int(val)
                       for val in configs.get('tagColour').split(', ')))
    drawer.multiline_text((startx, starty), tags,
                          tagColour, font, align='center')

    return base


def makeThumbnail(
        title: str,
        tags: List[str],
        configSection: str = 'default') -> BytesIO:
    parsedOptions = configparser.ConfigParser()
    parsedOptions.read_file(
        open(
            './furryposter/utilities/thumbnailgen/thumbnail.config',
            'r',
            encoding='utf-8'))
    global configs
    try:
        configs = parsedOptions[configSection]
    except KeyError:
        print('No valid config found under {}'.format(configSection))
        raise

    if len(tags) > configs.getint('maxTags'):
        tags = tags[:configs.getint('maxTags')]

    tags = [tag.title() for tag in tags]

    thumbnail = __createBase()
    thumbnail = __addText(title, tags, thumbnail)
    thumbfile = BytesIO()
    thumbnail.save(thumbfile, 'PNG')
    return thumbfile


if __name__ == '__main__':
    title = input('Enter title: ')
    title = title.replace('\\n', '\n')
    tags = input('Enter tags as CSV: ')
    destination = input('Enter target directory: ')
    thumbfile = makeThumbnail(title, tags.split(', '))
    with open(destination + r'\thumbnail.png', 'wb') as file:
        file.write(thumbfile.getbuffer())
