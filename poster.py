#!/usr/bin/env python3

import argparse
from furryposter.websites import sofurry, weasyl, furaffinity
from furryposter.websites.website import AuthenticationError, WebsiteError, Website
import os
import pathlib
import re
import http.cookiejar
from io import StringIO, TextIOWrapper, BufferedReader
from typing import Optional
from furryposter.utilities.thumbnailgen import thumbnailerrors
from furryposter.story import Story
import builtins

stage = ''


def print(inp: str): builtins.print(stage + inp)


def setstage(newstage: str):
    global stage
    stage = '[{}]'.format(newstage).ljust(15)


def getstage():
    global stage
    return stage


setstage('init')
parser = argparse.ArgumentParser(
    prog="furrystoryuploader",
    description="Post stories to furry websites")


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


def initSite(
        regexString: str,
        site: Website,
        ignore_errors: bool) -> Optional[Website]:
    """Initialise site with cookies"""

    cookiesLoc = None
    for file in os.listdir(os.getcwd()):
        if re.match(regexString, file):
            cookiesLoc = file
            break
    if cookiesLoc is None:
        if ignore_errors is False:
            raise AuthenticationError(
                '{} cannot find a cookies file'.format(
                    site.name))
        else:
            print(
                '{} cannot find cookies; the site will be skipped'.format(
                    site.name))
    else:
        site.load(cookiesLoc)
        try:
            site.testAuthentication()
        except AuthenticationError:
            if ignore_errors is True:
                print(
                    '{} authentication failed!\nContinuing...'.format(
                        site.name))
            else:
                raise
        else:
            print('{} successfully authenticated'.format(site.name))
            return site
    return None


def main():
    initParser()
    args = parser.parse_args()

    args.directory = pathlib.Path(args.directory)

    if not args.outputdir:
        # if no directory is specified, use the directory with the story file
        args.outputdir = args.directory
    else:
        args.outputdir = pathlib.Path(args.outputdir)

    if args.offline:
        print('Offline mode is active')
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

    setstage('loading')

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
        raise Exception('No title specified!')
    if args.description == '':
        raise Exception('No description specified!')
    if args.tags == '':
        raise Exception('No tags specified!')

    if args.post_script:
        if os.path.exists('post-script.txt'):
            print('Post-script found')
            with open('post-script.txt', 'r', encoding='utf-8') as post:
                args.description = args.description + '\n\n' + ''.join(post.readlines())
        else:
            if args.ignore_errors:
                print('Post-script file cannot be loaded!\nContinuing...')
            else:
                raise Exception('Post-script file cannot be found')

    submission = Story(
        args.format,
        args.title,
        args.description,
        args.tags,
        args.rating)

    # determine file type to look for
    storyLoc = None
    args.format = args.format.lower()
    if args.format == 'text' or args.format == 'bbcode':
        ends = ['.txt']
    elif args.format == 'markdown':
        ends = ['.mmd', '.md']
    elif args.format == 'html':
        ends = ['.html']

    for file, ending in ((file, ending) for ending in ends for file in os.listdir(args.directory)):
        if file.endswith(ending):
            storyLoc = pathlib.Path(args.directory, file)
            print('File found: {}'.format(storyLoc))
            break
    if storyLoc is None:
        raise Exception(
            'No story file of format {} found!'.format(
                args.format))

    submission.loadContent(open(storyLoc, 'r', encoding='utf-8'))

    if args.warning:
        with open('content-warning.txt', 'r') as file:
            warning = file.read()
            submission.content = warning + '\n\n' + ('~' * 10) + '\n\n' + submission.content

    # get thumbnail
    if args.generate_thumbnail:
        try:
            submission.loadThumbnail(args.generate_thumbnail)
        except thumbnailerrors.ThumbnailSizingError:
            if args.ignore_errors:
                print('Thumbnail generation has failed!')
                thumbnailPass = None
            else:
                raise
    else:
        thumbnailLoc = None
        if args.thumbnail:
            for file in os.listdir(args.directory):
                if re.match('.*\\.(png|jpg)', file):
                    thumbnailLoc = pathlib.Path(args.directory, file)
                    print('Thumbnail file found')
                    submission.loadThumbnail(open(thumbnailLoc, 'rb'))
                    break
            if thumbnailLoc is None:
                if args.ignore_errors:
                    print('No thumbnail found!\nContinuing...')
                else:
                    raise Exception('No thumbnail file found!')

    # submit the files to each website
    storydest = pathlib.Path(args.outputdir, storyLoc.stem)

    if args.offline or args.messy:
        setstage('writing')
        print('writing story files...')

        storydest = pathlib.Path(args.outputdir, storyLoc.stem)

        with open(str(storydest) + 'bbcode.txt', 'w', encoding='utf-8') as file:
            file.write(submission.giveStory('bbcode').getvalue())

        with open(str(storydest) + '.md', 'w', encoding='utf-8') as file:
            file.write(submission.giveStory('markdown').getvalue())

        print('writing thumbnail...')
        if submission.thumbnail:
            with open(os.path.join(args.outputdir, 'thumbnail.png'), 'wb') as file:
                file.write(submission.giveThumbnail().getvalue())

        if args.messy is False and args.offline is True:
            print('writing description...')
            with open(os.path.join(args.outputdir, 'description.txt'), 'w', encoding='utf-8') as file:
                file.write(submission.giveDescription('bbcode'))
            with open(os.path.join(args.outputdir, 'description.md'), 'w', encoding='utf-8') as file:
                file.write(submission.giveDescription('markdown'))

    if args.offline is False:
        for site in sites:
            try:
                setstage('posting')
                print('Beginning {} submission'.format(site.name))
                if args.test:
                    print('test: {} bypassed'.format(site.name))
                else:
                    site.submitStory(
                        submission.title, submission.giveDescription(
                            site.preferredFormat), submission.tags, args.rating, submission.giveStory(
                            site.preferredFormat), submission.giveThumbnail())
                print('{} submission completed successfully'.format(site.name))
            except WebsiteError as e:
                if args.ignore_errors:
                    print(
                        '{} has failed with exception {}'.format(
                            site.name, e))
                else:
                    raise


if __name__ == '__main__':
    main()
