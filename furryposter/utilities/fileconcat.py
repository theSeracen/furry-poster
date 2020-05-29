'''Module for concatenating multiple text files'''
from typing import List


def concatFiles(file_list: List[str]):
    '''Load and concatenate the passed files'''
    file_content = []
    for file_loc in file_list:
        with open(file_loc, 'r') as file:
            file_content.append(file.read())
    return '\n********\n'.join(file_content)
