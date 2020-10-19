#!/usr/bin/env python3

import argparse
import builtins
import http.cookiejar
import logging
import os
import pathlib
import re
import sys
from io import BufferedReader, StringIO, TextIOWrapper
from typing import Optional

from furryposter.story import Story
from furryposter.utilities.fileconcat import concatFiles
from furryposter.utilities.thumbnailgen import thumbnailerrors
from furryposter.websites import furaffinity, sofurry, weasyl
from furryposter.websites.website import (AuthenticationError, Website,
                                          WebsiteError)

parser = argparse.ArgumentParser(
    prog="furrystoryuploader",
    description="Post stories to furry websites")
logger = logging.getLogger()


def initParser():
    thumbGroup = parser.add_mutually_exclusive_group()
    parser.add_argument('directory', metavar='D')
    parser.add_argument('-i', '--ignore-errors', action='store_true',
                        help='Ignore all errors and continue with other sites')
    parser.add_argument(
        '-f',
        '--format',
        choices=[
            'html',
            'markdown',
            'text',
            'bbcode'],
        default='markdown',
        help='Format of the source story file. Default is markdown')
    parser.add_argument(
        '-m',
        '--messy',
        action='store_true',
        help='Flag to cause all converted files to be written to disk rather than kept in memory')
    thumbGroup.add_argument(
        '-g',
        '--generate-thumbnail',
        default=False,
        const='default',
        nargs='?',
        help='Flag causes a thumbnail to be dynamically generated. The default profile is used in thumbnail.config unless specified')

    # site flags
    parser.add_argument('-F', '--furaffinity', action='store_true', help="Flag for whether FurAffinity should be tried")
    parser.add_argument('-S', '--sofurry', action='store_true', help="Flag for whether SoFurry should be tried")
    parser.add_argument('-W', '--weasyl', action='store_true', help="Flag for whether Weasyl should be tried")

    # story details
    parser.add_argument('-t', '--title', help="String for the title of the story")
    parser.add_argument('-d', '--description', help="String for the description of the story")
    parser.add_argument('-k', '--tags', help="List of CSV for the story tags")
    thumbGroup.add_argument('-p', '--thumbnail', action='store_true',
                            help="Flag for whether a thumbnail is present and should be used")
    parser.add_argument(
        '-s',
        '--post-script',
        action='store_true',
        help='Flag to look for a post-script.txt to add to the end of the description')
    parser.add_argument(
        '-r',
        '--rating',
        choices=[
            'general',
            'adult'],
        default='adult',
        help="Rating for the story; choice between 'general' and 'adult'; defaults to adult")
    parser.add_argument('-w', '--warning', action='store_true', help='Adds a content warning to the top of a story')

    parser.add_argument(
        '-o',
        '--offline',
        action='store_true',
        help='Converts and writes everything to files but does not upload')
    parser.add_argument(
        '--test',
        action='store_true',
        help='debugging flag; if included, the program will do everything but submit')
    parser.add_argument('-O', '--outputdir', help='The output directory for any files to be saved to')
    parser.add_argument('-c', '--concatenate', action='store_true', help='concatenate all files found in folder')
    parser.add_argument('-v', '--verbose', action='count')


def initSite(regexString: str, site: Website, ignore_errors: bool) -> Optional[Website]:
    """Initialise site with cookies"""

    cookiesLoc = None
    for file in pathlib.Path('res/').iterdir():
        if re.match(regexString, file.name):
            cookiesLoc = file
            break
    if cookiesLoc is None:
        if ignore_errors is False:
            raise AuthenticationError('{} cannot find a cookies file'.format(site.name))
        else:
            logger.warning('{} cannot find cookies; the site will be skipped'.format(site.name))
    else:
        site.load(cookiesLoc)
        try:
            site.testAuthentication()
        except AuthenticationError:
            if ignore_errors is True:
                logger.error('{} authentication failed!\nContinuing...'.format(site.name))
            else:
                raise
        else:
            logger.info('{} successfully authenticated'.format(site.name))
            return site
    return None


def main():
    initParser()
    args = parser.parse_args()

    logger.setLevel(1)
    stream = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] - %(message)s')
    stream.setFormatter(formatter)
    stream.setLevel(logging.INFO)
    logger.addHandler(stream)

    if args.verbose > 0:
        stream.setLevel(logging.DEBUG)

    args.directory = pathlib.Path(args.directory)

    if args.outputdir:
        args.outputdir = pathlib.Path(args.outputdir)
    else:
        args.outputdir = args.directory

    if args.offline:
        logger.info('Offline mode is active')
    else:
        sites = []
        if args.furaffinity:
            site = furaffinity.FurAffinity()
            sites.append(initSite(site.cookiesRegex, site, args.ignore_errors))

        if args.sofurry:
            site = sofurry.SoFurry()
            sites.append(initSite(site.cookiesRegex, site, args.ignore_errors))

        if args.weasyl:
            site = weasyl.Weasyl()
            sites.append(initSite(site.cookiesRegex, site, args.ignore_errors))

        sites = filter(None, sites)

    # now we can go into checking for all the required items
    if args.directory.is_dir() is False:
        raise Exception("Valid directory required")

    if args.outputdir.is_dir() is False:
        raise Exception("Valid output directory required")

    if args.title is None:
        args.title = input('Please enter a title: ')
    if args.description is None:
        args.description = input('Please enter a description: ')
    if args.tags is None:
        args.tags = input('Please enter CSV tags: ')

    # replaces newline from manual input as it doesn't add an escape
    args.description = args.description.replace('\\n', '\n')

    # error checking
    if args.title == '':
        raise Exception('No title specified')
    if args.description == '':
        raise Exception('No description specified')
    if args.tags == '':
        raise Exception('No tags specified')

    if args.post_script:
        if os.path.exists('res/post-script.txt'):
            logger.info('Post-script found')
            with open('res/post-script.txt', 'r', encoding='utf-8') as postScriptFile:
                args.description = args.description + '\n\n' + ''.join(postScriptFile.readlines())
        else:
            if args.ignore_errors:
                logger.error('Post-script file cannot be loaded!\nContinuing...')
            else:
                raise Exception('Post-script file cannot be found')

    submission = Story(args.format, args.title, args.description, args.tags, args.rating)

    # determine file type to look for
    storyLoc = None
    args.format = args.format.lower()
    if args.format == 'text' or args.format == 'bbcode':
        ends = ['.txt']
    elif args.format == 'markdown':
        ends = ['.mmd', '.md', '.stry']
    elif args.format == 'html':
        ends = ['.html']

    dirfiles = args.directory.iterdir()
    dirfiles = list(filter(lambda file: file.suffix in ends, dirfiles))

    # find all of the story files in the folder directory
    if len(dirfiles) == 0:
        raise Exception('No story file of format {} found'.format(args.format))

    elif len(dirfiles) == 1:
        storyLoc = dirfiles[0]
        logger.info('Story file found: {}'.format(storyLoc))

    elif len(dirfiles) > 1:
        if args.concatenate:
            logger.debug('Concatenating {} found files'.format(len(dirfiles)))
            dirfiles = [str(pathlib.PurePath(dirfile)) for dirfile in dirfiles]
            storyLoc = StringIO(concatFiles(dirfiles))
        else:
            while True:
                print('Multiple story files found. Please select one:')
                for pos, file in enumerate(dirfiles):
                    print('{}. {}'.format(pos + 1, file.name))

                try:
                    choice = int(input('Please choose a file -> ')) - 1
                    storyLoc = dirfiles[choice]
                    break
                except (ValueError, IndexError):
                    print('Invalid Selection!')

    if isinstance(storyLoc, StringIO):
        submission.loadContent(storyLoc)
    else:
        submission.loadContent(open(storyLoc, 'r', encoding='utf-8'))

    if args.warning:
        logger.info('Content warning found')
        with open('res/content-warning.txt', 'r') as warningFile:
            warning = warningFile.read()
            submission.content = warning + '\n\n' + ('~' * 10) + '\n\n' + submission.content

    # get thumbnail
    if args.generate_thumbnail:
        try:
            submission.loadThumbnail(args.generate_thumbnail)
            logger.debug('Thumbnail generated')
        except thumbnailerrors.ThumbnailSizingError:
            if args.ignore_errors:
                logger.error('Thumbnail generation has failed!')
                thumbnailPass = None
            else:
                raise
    else:
        thumbnailLoc = None
        if args.thumbnail:
            ends = ['png', 'jpg']
            dirfiles = args.directory.iterdir()
            dirfiles = list(filter(lambda file: file.suffix in ends, dirfiles))

            if len(dirfiles) == 0:
                if args.ignore_errors:
                    logger.warning('No thumbnail found')
                else:
                    raise Exception('No thumbnail file found')

            elif len(dirfiles) == 1:
                thumbnailLoc = dirfiles[0]
                logger.info('Thumbnail file found')
                submission.loadThumbnail(open(thumbnailLoc, 'rb'))

            elif len(dirfiles) > 1:
                while True:
                    print('Multiple thumbnail files found. Please select one:')
                    for pos, file in enumerate(dirfiles):
                        print('{}. {}'.format(pos + 1, file.name))

                    try:
                        choice = int(input('Please choose a file -> ')) - 1
                        thumbnailLoc = dirfiles[choice]
                        submission.loadThumbnail(open(thumbnailLoc, 'rb'))
                        break
                    except (ValueError, IndexError):
                        print('Invalid Selection!')

    # submit the files to each website
    try:
        storydest = pathlib.Path(args.outputdir, storyLoc.stem)
    except AttributeError:
        storydest = pathlib.Path(args.outputdir, 'story')

    if args.offline or args.messy:
        logger.info('Writing story files')

        with open(str(storydest) + 'bbcode.txt', 'w', encoding='utf-8') as file:
            file.write(submission.giveStory('bbcode').getvalue())
        with open(str(storydest) + '.md', 'w', encoding='utf-8') as file:
            file.write(submission.giveStory('markdown').getvalue())
        logger.debug('Written story files')

        if submission.thumbnail:
            with open(storydest.parent / 'thumbnail.png', 'wb') as file:
                file.write(submission.giveThumbnail().getvalue())
        logger.debug('Written thumbnail file')

        with open(storydest.parent / 'description.txt', 'w', encoding='utf-8') as file:
            file.write(submission.giveDescription('bbcode'))
        with open(storydest.parent / 'description.md', 'w', encoding='utf-8') as file:
            file.write(submission.giveDescription('markdown'))
        logger.debug('Written description files')

    if args.offline is False:
        for site in sites:
            try:
                logger.debug('Beginning {} submission'.format(site.name))
                if args.test:
                    logger.degub('Test: {} bypassed'.format(site.name))
                else:
                    site.submitStory(
                        submission.title, submission.giveDescription(
                            site.preferredFormat), submission.tags, args.rating, submission.giveStory(
                            site.preferredFormat), submission.giveThumbnail())

                logger.info('{} submission completed successfully'.format(site.name))
            except WebsiteError as e:
                if args.ignore_errors:
                    logger.error('Submission to {} has failed with exception {}'.format(site.name, e))
                else:
                    raise


if __name__ == '__main__':
    main()
