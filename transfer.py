#!/usr/bin/env python3

import argparse
import builtins
import logging
import os
import re
import sys
import time

from tqdm import tqdm

from furryposter.story import Story
from furryposter.websites import furaffinity, sofurry, weasyl
from furryposter.websites.website import Website

parser = argparse.ArgumentParser(
    prog="furrytransfer",
    description="Transfer galleries between furry sites")
logger = logging.getLogger()


def initParser():
    parser.add_argument('source', metavar='S',
                        choices=[
                            'furaffinity',
                            'sofurry',
                            'weasyl'],
                        help='site with gallery')
    parser.add_argument('destination', metavar='D',
                        choices=[
                            'furaffinity',
                            'sofurry',
                            'weasyl'],
                        help='site to transfer to')
    parser.add_argument('name', metavar='N', help='the name of the user to copy the gallery from')

    parser.add_argument('-d', '--delay', type=int, default=5, help='seconds between posts to new site')
    parser.add_argument('-t', '--thumbnail-behaviour',
                        choices=[
                            'new',
                            'source',
                            'none'],
                        default='new')
    parser.add_argument(
        '-p',
        '--profile',
        default='default',
        help='Profile to use in thumbnail generation if -t flag set to new')
    parser.add_argument('-m', '--max', type=int, default=None, help='Maximum number of stories to post')
    parser.add_argument('-f', '--force', action='store_true', help='Skips all checks and inputs')
    parser.add_argument('--test', action='store_true', help='Aborts actual upload')

    return parser.parse_args()


def main():
    args = initParser()

    logger = logging.getLogger()
    logger.setLevel(1)
    stream = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] - %(message)s')
    stream.setFormatter(formatter)
    stream.setLevel(logging.INFO)
    logger.addHandler(stream)

    if args.source == args.destination:
        raise Exception('Source and destination sites cannot be the same')
    if args.source == 'sofurry' and args.thumbnail_behaviour == 'source' and args.force is False:
        print('Default thumbnails are generated in all Sofurry submissions and these cannot be distinguished from uploaded thumbnails. Do you wish to continue with this in mind?')
        response = input('(Yes/No): ')
        if 'n' in response.lower():
            print('Aborting...')
            exit(1)

    if args.test:
        logger.info('Testing is enabled; submissions are disabled')

    if args.max:
        logger.info('Only {} submissions will be transferred'.format(args.max))

    source = determineSite(args.source)
    dest = determineSite(args.destination)
    if args.force is False:
        print(
            'Confirmation required: Do you want to transfer the gallery of {} on site {} to the provided account on {}?'.format(
                args.name,
                source.name,
                dest.name))

        response = input('(Yes/No): ')
        if 'n' in response.lower():
            print('Aborting...')
            exit(0)

    sourceSubmissions = source.crawlGallery(args.name)
    logger.debug('{} submissions in source gallery found'.format(len(sourceSubmissions)))
    destSubmissions = dest.crawlGallery(args.name)
    logger.debug('{} submissions already in destination gallery'.format(len(destSubmissions)))

    logger.info('Processing source stories from {}'.format(source.name))

    sourceStories = []
    for sub in tqdm(sourceSubmissions, dynamic_ncols=True):
        sourceStories.append(source.parseSubmission(sub))
    sourceStories = list(filter(None, sourceStories))

    logger.info('Processing destination stories from {}'.format(dest.name))
    destStories = []
    for sub in tqdm(destSubmissions, dynamic_ncols=True):
        destStories.append(dest.parseSubmission(sub))
    destStories = list(filter(None, destStories))

    logger.info('{} stories to be transferred'.format(len(sourceStories)))
    destTitles = [story.title for story in destStories]

    postCount = 0
    for place, story in enumerate(sourceStories):
        if story.title in destTitles:
            logger.debug(
                'Skipping {} of {}: {} found in destination gallery'.format(
                    place + 1, len(sourceStories), story.title))
        else:
            if args.thumbnail_behaviour == 'new':
                story.forceGenThumbnail(args.profile)
            elif args.thumbnail_behaviour == 'none':
                story.thumbnail = None

            logger.debug('Transferring {} of {} --- {}'.format(place +
                                                               1, len(sourceStories), story.title))
            if args.test is False:
                dest.submitStory(
                    story.title, story.giveDescription(
                        dest.preferredFormat), story.tags, story.rating, story.giveStory(
                        dest.preferredFormat), story.giveThumbnail())

            postCount += 1
            if args.max:
                if postCount >= args.max:
                    logger.info('Posting limit reached!')
                    break

            time.sleep(args.delay)

    logger.info('{} stories transferred'.format(postCount))


def determineSite(site: str) -> Website:
    if site == 'furaffinity':
        site = furaffinity.FurAffinity()
        site.load(_find_cookies(site.cookiesRegex))
    elif site == 'sofurry':
        site = sofurry.SoFurry()
        site.load(_find_cookies(site.cookiesRegex))
    elif site == 'weasyl':
        site = weasyl.Weasyl()
        site.load(_find_cookies(site.cookiesRegex))
    else:
        raise Exception("Website '{}' unrecognised".format(site))
    return site


def _find_cookies(regex: str) -> str:
    for file in os.listdir(os.getcwd()):
        if re.match(regex, file):
            return file


if __name__ == '__main__':
    main()
