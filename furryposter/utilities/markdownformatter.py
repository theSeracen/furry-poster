"""Module for converting a markdown file"""

import os
import re


def findFiles(directory: str):
    files = os.listdir(directory)
    # create list of all markdown files in directory
    markdown_files = [(directory + '\\' + file)
                      for file in files if file.endswith('.mmd')]
    for md_file in markdown_files:
        formatFileBBcode(md_file)


def checkMarkdown(line: str) -> str:
    """Check the passed string and validate all markdown in it"""
    line = __doubleNewLines(line)
    return line


def parseStringBBcode(line: str) -> str:
    """Takes a string of markdown formatting and converts it to BBcode"""
    formattingFunctions = [
        __linkMarkdowntoBBcode,
        __strongMarkdowntoBBcode,
        __boldMarkdowntoBBcode,
        __italicMarkdowntoBBcode,
        __doubleNewLines]
    for formatFunc in formattingFunctions:
        line = formatFunc(line)
    return line


def __linkMarkdowntoBBcode(line: str) -> str:
    simple_pattern = r'\[(.*?)\]\(((http|www)?.*?)\)'
    complex_pattern = r'<(.*?)>'
    substitutions = []

    for match in re.findall(r'(({})|({}))'.format(simple_pattern, complex_pattern), line):
        match = match[0]
        # first format for links
        if re.search(simple_pattern, match):
            link = re.search(simple_pattern, match)
            substitutions.append(
                (re.sub(simple_pattern, '[URL=' + link.group(2) + ']' + link.group(1) + '[/URL]', match), match))
        # second format for links
        elif re.search(complex_pattern, match):
            link = re.search(complex_pattern, match)
            substitutions.append((re.sub(complex_pattern, '[URL]' + link.group(1) + '[/URL]', match), match))

    for (new, old) in substitutions:
        line = line.replace(old, new)
    return line


def __doubleNewLines(line: str) -> str:
    """Doubles the new lines in the document, if there is not already a blank line between each paragraph"""
    # number 5 is completely abitrary
    if len(re.findall(r'\n\n', line)) >= 5:
        return line
    else:
        return line.replace('\n', '\n\n')


def __boldMarkdowntoBBcode(line: str) -> str:
    """Takes a string and returns a single BBcode string with bold formatting"""
    # explode into bold parts
    boldParts = re.split(r'(\*{2,2}.+?\*{2,2})', line)
    for part in range(len(boldParts)):
        if boldParts[part - 1].startswith('**'):
            boldParts[part - 1] = '[B]' + boldParts[part - 1].lstrip('**')
        if boldParts[part - 1].endswith('**'):
            boldParts[part - 1] = boldParts[part - 1].rstrip('**') + '[/B]'
    return ''.join(boldParts)


def __strongMarkdowntoBBcode(line: str) -> str:
    strongParts = re.split(r'(\*{3,3}.+?\*{3,3})', line)
    for part in range(len(strongParts)):
        if strongParts[part - 1].startswith('***'):
            strongParts[part - 1] = '[B][I]' + strongParts[part - 1].lstrip('***')
        if strongParts[part - 1].endswith('***'):
            strongParts[part - 1] = strongParts[part - 1].rstrip('***') + '[/I][/B]'
    return ''.join(strongParts)


def __italicMarkdowntoBBcode(line: str) -> str:
    italicParts = re.split(r'(\*{1,1}.+?\*{1,1})', line)
    for part in range(len(italicParts)):
        if italicParts[part - 1].startswith('*'):
            italicParts[part - 1] = '[I]' + italicParts[part - 1].lstrip('*')
        if italicParts[part - 1].endswith('*'):
            italicParts[part - 1] = italicParts[part - 1].rstrip('*') + '[/I]'
    return ''.join(italicParts)


def formatFileBBcode(file: str):
    with open(file, 'r', encoding='utf-8') as markdown:
        lines = markdown.readlines()
        formatted = []
        for line in lines:
            # add double lines for each paragraph
            line = line.replace('\n', '\n\n')
            formatted.append(parseStringBBcode(line))
    with open(file.rstrip('.mmd') + 'formatted.txt', 'w') as textfile:
        textfile.writelines(formatted)


if __name__ == '__main__':
    directory = input('Please enter a directory: ')
    findFiles(directory)
    print('Conversion Complete')
