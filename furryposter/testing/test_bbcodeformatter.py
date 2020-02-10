import unittest
from furryposter.utilities import bbcodeformatter

class TestBBcodeFormatting(unittest.TestCase):

	def test_bold(self):
		teststrings = ['[B]teststring[/B]', '[b]teststring[/b]', 'this is a [B]test string[/B] for bbcode']
		results = [bbcodeformatter.parseStringMarkdown(string) for string in teststrings]
		self.assertListEqual(results, ['**teststring**','**teststring**','this is a **test string** for bbcode'])

	def test_italics(self):
		teststrings = ['[I]teststring[/I]','[i]teststring[/i]', 'this is a [I]test string[/I] for bbcode']
		results = [bbcodeformatter.parseStringMarkdown(string) for string in teststrings]
		self.assertListEqual(results,['*teststring*','*teststring*','this is a *test string* for bbcode'])

	def test_strong(self):
		teststrings = ['[B][I]teststring[/I][/B]','[b][i]teststring[/i][/b]', 'this is a [B][I]test string[/I][/B] for bbcode']
		results = [bbcodeformatter.parseStringMarkdown(string) for string in teststrings]
		self.assertListEqual(results,['***teststring***','***teststring***','this is a ***test string*** for bbcode'])

	def test_linksimple(self):
		teststrings = ['[URL]testing.com/[/URL]','[URL]testing.com[/URL]']
		results = [bbcodeformatter.parseStringMarkdown(string) for string in teststrings]
		self.assertListEqual(results, ['<testing.com/>','<testing.com>'])

	def test_linkcomplex(self):
		teststrings = ['[URL=example.com]test link[/URL]']
		results = [bbcodeformatter.parseStringMarkdown(string) for string in teststrings]
		self.assertListEqual(results, ['[test link](example.com)'])

if __name__ == '__main__':
	unittest.main()