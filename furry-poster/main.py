import argparse

parser = argparse.ArgumentParser(prog="furrystoryuploader", description="Post stories to furry websites")
parser.add_argument('directory', metavar='D')

#site flags
parser.add_argument('-F','--furaffinity', action=store_true, help="Flag for whether FurAffinity should be tried")
parser.add_argument('-S','--sofurry', action=store_true, help="Flag for whether SoFurry should be tried")
parser.add_argument('-W','--weasyl',action=store_true, help="Flag for whether Weasyl should be tried")

#story details
parser.add_argument('-t','--title', help="String for the title of the story")
parser.add_argument('-d','--description', help="String for the description of the story")
parser.add_argument('-k','--tags', help="List of CSV for the story tags")
parser.add_argument('-p', '--thumbnail', action=store_true, help="Flag for whether a thumbnail is present and should be used")
