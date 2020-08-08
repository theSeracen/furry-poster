'''Module for concatenating multiple text files'''
from typing import List


def concatFiles(file_list: List[str]):
    '''Load and concatenate the passed files'''
    file_content = []
    for file_location in sorted(file_list):
        with open(file_location, 'r') as file:
            file_content.append(file.read())

    return '\n-------------\n'.join(file_content)
