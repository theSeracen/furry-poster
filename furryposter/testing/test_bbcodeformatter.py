import unittest
from furryposter.utilities import bbcodeformatter

class TestBBcodeFormatting(unittest.TestCase):

	def test_bold(self):
		teststrings = ['[B]teststring[/B]', '[b]teststring[/b]',
				 'this is a [B]test string[/B] for bbcode','this [b]is[/b] multiple [B]bold [/b] in a string']

		results = [bbcodeformatter.parseStringMarkdown(string) for string in teststrings]
		self.assertListEqual(results, ['**teststring**','**teststring**','this is a **test string** for bbcode','this **is** multiple **bold ** in a string'])

	def test_italics(self):
		teststrings = ['[I]teststring[/I]','[i]teststring[/i]',
				 'this is a [I]test string[/I] for bbcode', 'this [I]is[/I] multiple [i]italics [/I] in a string']

		results = [bbcodeformatter.parseStringMarkdown(string) for string in teststrings]
		self.assertListEqual(results,['*teststring*','*teststring*','this is a *test string* for bbcode', 'this *is* multiple *italics * in a string'])

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

	def test_complex(self):
		teststrings = ['This [I]is[/I] a [B]complicated[/B] string with [I][B]many[/B][/I] [URL=test.com]BBcode[/URL] options like [URL]example.net[/URL] for example']
		results = [bbcodeformatter.parseStringMarkdown(string) for string in teststrings]
		self.assertListEqual(results, ['This *is* a **complicated** string with ***many*** [BBcode](test.com) options like <example.net> for example'])

if __name__ == '__main__':
	unittest.main()