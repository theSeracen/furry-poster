import configparser
from io import BytesIO
from typing import List, Tuple

from furryposter.utilities.thumbnailgen.thumbnailerrors import (
    ThumbnailError, ThumbnailSizingError)
from PIL import Image, ImageDraw, ImageFont

configs = None


def _createBase() -> Image:
    """Create the thumbnail base"""
    background_colour = tuple((int(val) for val in configs.get('backcolour').split(', ')))
    base = Image.new('RGB',
                     (configs.getint('width'), configs.getint('height')),
                     background_colour)

    return base


def _determineOptimalTextSize(
        text: str,
        maxSize: int,
        doingTags: bool) -> int:
    """Function to find the biggest text size that fits in the given space"""

    font_size = 5
    if doingTags:
        size_index = 1
    else:
        size_index = 0

    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerif.ttf', font_size)
    while font.getsize_multiline(text)[size_index] < maxSize:
        if doingTags:
            if font.getsize_multiline(text)[0] >= (configs.getint('width') *
                                                   0.75):  # make sure that it doesn't cover more than 75% of width
                break
        font_size += 1
        font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSerif.ttf", font_size)

    return font_size - 1


def _findOptimalTitle(title: str) -> Tuple[str, int]:
    """Function to split up long titles into multiline strings to get the best size"""
    title_cut_position = -1
    title_starting_pos = tuple((int(val) for val in configs.get('titleStartCoords').split(', ')))

    titleSize = _determineOptimalTextSize(title, (configs.getint('width') - title_starting_pos[0]), False)
    title_text = title
    while titleSize < configs.getint('minTitleSize'):
        title_text = title.split(' ')
        if abs(title_cut_position) >= len(title_text):
            raise ThumbnailSizingError('Cannot find best title size')
        title_text = ' '.join(title_text[:title_cut_position]) + '\n' + \
            ' '.join(title_text[title_cut_position:]).replace('\n', ' ')

        titleSize = _determineOptimalTextSize(
            title_text, (configs.getint('width') - title_starting_pos[0]), False)
        title_cut_position -= 1

    return title_text, titleSize


def _addText(title: str, tags: List[str], base: Image) -> Image:
    """Add the title and tags to the base image"""
    # find the best size for the title
    title_coordinates = tuple((int(val) for val in configs.get('titleStartCoords').split(', ')))

    title, titlesize = _findOptimalTitle(title)
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSerif.ttf", titlesize)

    # max out the size and then centre if too big
    if titlesize > configs.getint('maxTitleSize'):
        titlesize = configs.getint('maxTitleSize')
        font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSerif.ttf", titlesize)
        title_width, title_height = font.getsize_multiline(title)
        new_title_x = (base.width - title_width) / 2
        title_coordinates = (new_title_x, title_coordinates[1])

    titleColour = tuple((int(val) for val in configs.get('titleColour').split(', ')))

    drawer = ImageDraw.Draw(base)

    drawer.multiline_text(title_coordinates, title, titleColour, font, align='center')
    titlewidth, titleheight = font.getsize_multiline(title)

    starty = titleheight + int(configs.getint('titleTagSepDist'))
    tags = '\n'.join(tags)
    tagsize = _determineOptimalTextSize(tags, (configs.getint(
        'width') - starty - configs.getint('tagBottomBorder')), True)

    # if the tags are too close in size to the title, reduce
    if abs(titlesize - tagsize) <= 10:
        tagsize = titlesize - 11

    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerif.ttf', tagsize)

    tag_width, tag_height = font.getsize_multiline(tags)
    tag_start_x = (base.width - tag_width) / 2
    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerif.ttf', tagsize - 1)
    tag_colour = tuple((int(val) for val in configs.get('tagColour').split(', ')))
    drawer.multiline_text((tag_start_x, starty), tags, tag_colour, font, align='center')

    return base


def makeThumbnail(title: str, tags: List[str], configSection: str = 'default') -> BytesIO:
    parsedOptions = configparser.ConfigParser()
    parsedOptions.read_file(
        open('./furryposter/utilities/thumbnailgen/thumbnail.config', 'r', encoding='utf-8'))

    global configs
    try:
        configs = parsedOptions[configSection]
    except KeyError:
        print('No valid config found under {}'.format(configSection))
        raise

    if len(tags) > configs.getint('maxTags'):
        tags = tags[:configs.getint('maxTags')]

    tags = [tag.title() for tag in tags]

    thumbnail = _createBase()
    thumbnail = _addText(title, tags, thumbnail)
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
