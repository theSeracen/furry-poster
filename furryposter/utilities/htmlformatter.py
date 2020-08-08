"""
Module for converting HTML story files to markdown-formatted text as used on FA and other sites
"""
import os
from typing import List, TextIO

import bs4


def parseStringBBcode(in_line: str) -> str:
    """Parse HTML tags to add BBcode tags to text"""
    out_line = ''
    if in_line.text != '':
        for child in in_line.children:
            text = child.text
            if 'italic' in child.attrs['style']:
                text = '[I]' + text + '[/I]'
            if 'font-weight' in child.attrs['style']:
                text = '[B]' + text + '[/B]'
            out_line = out_line + text

    return out_line


def parseStringMarkdown(in_line: str) -> str:
    """Parse HTML tags to markdown"""
    out_line = ''
    if in_line.text != '':
        for child in in_line.children:
            text = child.text
            if 'italic' in child.attrs['style']:
                text = '*' + text + '*'
            if 'font-weight' in child.attrs['style']:
                text = '**' + text + '**'
            out_line = out_line + text

    return out_line


def findFiles(directory: str, finalFormat: str):
    """Function to format all files in a directory"""
    files = os.listdir(directory)

    # create list of all html files in directory
    html_files = [(directory + '\\' + file)
                  for file in files if file.endswith('html')]

    for htmlpage in html_files:
        filename = htmlpage
        htmlpage = open(htmlpage, 'r', encoding='utf-8')
        if finalFormat == 'bbcode':
            formatted = formatFileBBcode(htmlpage)
        elif finalFormat == 'markdown':
            formatted = formatFileMarkdown(htmlpage)

        htmlpage.close()

        with open(filename.split('.')[0] + 'formatted.txt', 'w', encoding='UTF-8') as storyfile:
            for part in formatted:
                storyfile.write(part)


def formatFileBBcode(htmlfile: TextIO) -> List[str]:
    """Format a specified HTML file"""
    page = bs4.BeautifulSoup(htmlfile, 'html.parser')
    paragraphs = page.findAll('p')

    # build list of formatted strings, centring if necessary
    story = [("[center]" + parseStringBBcode(paragraph) + "[/center]" + '\n\n') if (
        'align' in paragraph.attrs) else (
        parseStringBBcode(paragraph) + '\n\n') for paragraph in paragraphs]

    return story


def formatFileMarkdown(htmlfile: TextIO) -> List[str]:
    """Format a specified HTML file"""
    page = bs4.BeautifulSoup(htmlfile, 'html.parser')
    paragraphs = page.findAll('p')

    # build list of formatted strings, centring if necessary
    story = [("[center]" + parseStringMarkdown(paragraph) + "[/center]" + '\n\n') if (
        'align' in paragraph.attrs) else (
        parseStringMarkdown(paragraph) + '\n\n') for paragraph in paragraphs]
    return story


if __name__ == '__main__':
    directory = input('Please enter a directory: ')
    mode = input('Enter a destination format (markdown|bbcode): ')
    findFiles(directory, mode)
    print('Conversion Complete')
