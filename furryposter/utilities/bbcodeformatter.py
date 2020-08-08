"""Module for converting BBcode tags"""
import re


def parseStringMarkdown(line: str) -> str:
    """Converts a string of BBcode to markdown formatting"""
    formattingFunctions = [
        _boldBBcodetoMarkdown,
        _italicsBBcodetoMarkdown,
        _linksBBBcodetoMarkdown,
        _doubleNewLines]
    for formatfunc in formattingFunctions:
        line = _boldBBcodetoMarkdown(line)
    return line


def checkBBcode(line: str) -> str:
    """Check the passed string and validate all BBcode in it"""
    line = _doubleNewLines(line)
    return line


def _italicsBBcodetoMarkdown(line: str) -> str:
    tags = ['[I]', '[i]', '[/I]', '[/i]']
    for tag in tags:
        line = line.replace(tag, '*')
    return line


def _boldBBcodetoMarkdown(line: str) -> str:
    tags = ['[B]', '[b]', '[/B]', '[/b]']
    for tag in tags:
        line = line.replace(tag, '**')
    return line


def _doubleNewLines(line: str) -> str:
    """Doubles the new lines in the document, if there is not already a blank line between each paragraph"""
    # number 5 is completely abitrary; just need to find if there's more than 5 empty lines
    if len(re.findall(r'\n\n', line)) >= 5:
        return line
    else:
        return line.replace('\n', '\n\n')


def _linksBBBcodetoMarkdown(line: str) -> str:
    simple_link_pattern = r'\[URL\](.*?)\[/URL\]'
    complex_link_pattern = r'\[URL=(.*?)\](.*?)\[/URL\]'

    substitutions = []

    for match in re.findall(r'(({})|({}))'.format(simple_link_pattern, complex_link_pattern), line):
        match = match[0]

        if re.search(complex_link_pattern, match):
            link = re.search(complex_link_pattern, match)
            substitutions.append(
                (re.sub(complex_link_pattern, '[' + link.group(2) + '](' + link.group(1) + ')', match),
                 match))

        elif re.search(simple_link_pattern, match):
            link = re.search(simple_link_pattern, match)
            substitutions.append((re.sub(simple_link_pattern, '<' + link.group(1) + '>', match), match))

    for (new, old) in substitutions:
        line = line.replace(old, new)
    return line


if __name__ == '__main__':
    line = input('Enter test string: ')
    print(parseStringMarkdown(line))
