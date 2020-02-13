"""Module with a class that represents a story and associated methods"""
from typing import TextIO, BinaryIO
import io
from furryposter.utilities import bbcodeformatter, markdownformatter, htmlformatter
from furryposter.utilities.thumbnailgen import thumbnailgeneration

class StoryError(Exception): pass

class Story():
	def __init__(self, sourceFormat: str, title: str, description: str, tags: str):
		self.sourceFormat = sourceFormat
		self.title = title
		self.description = description
		self.tags = tags

		self.content = None
		self.thumbnail = None

	def loadContent(self, file: TextIO):
		self.content = file.read()
		if self.sourceFormat == 'bbcode':
			self.content = bbcodeformatter.checkBBcode(self.content)
		elif self.sourceFormat == 'markdown':
			self.content = markdownformatter.checkMarkdown(self.content)

	def loadThumbnail(self, file: BinaryIO = None, thumbnailProfile: str = 'default'):
		"""Loads the thumbnail if a file is given, else generates it"""
		if file is None: self.thumbnail = thumbnailgeneration.makeThumbnail(self.title, self.tags.split(', '), thumbnailProfile).read()
		else: self.thumbnail = file.read()

	def giveStory(self, format: str) -> TextIO:
		"""Returns StringIO of the story"""
		if self.sourceFormat == format: return io.StringIO(self.content)
		elif self.sourceFormat == 'bbcode' and format == 'markdown': return io.StringIO(bbcodeformatter.parseStringMarkdown(self.content))
		elif self.sourceFormat == 'markdown' and format == 'bbcode': return io.StringIO(markdownformatter.parseStringBBcode(self.content))
		elif self.sourceFormat == 'html' and format == 'markdown': return io.StringIO(htmlformatter.formatFileMarkdown(io.StringIO(self.content)))
		elif self.sourceFormat == 'html' and format == 'bbcode': return io.StringIO(htmlformatter.formatFileBBcode(io.StringIO(self.content)))

	def giveThumbnail(self) -> BinaryIO:
		return io.BytesIO(self.thumbnail)
