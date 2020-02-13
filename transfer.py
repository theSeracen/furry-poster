import argparse
import os
from furryposter.story import Story

parser = argparse.ArgumentParser(prog="furrytransfer", description="Transfer galleries between furry sites")

def initParser():
	parser.add_argument('destination', metavar='D', help='site to transfer to')
	parser.add_argument('source', metavar='S', help='site with gallery')

	parser.add_argument('-d', '--delay', type=int, default=5, help='seconds between posts to new site')

def main():
	initParser()
	args = parser.parse_args()



if __name__ == '__main__':
	main()