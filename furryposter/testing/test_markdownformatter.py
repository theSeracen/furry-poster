import unittest
from furryposter.utilities import markdownformatter

class TestMarkdownFormatting(unittest.TestCase):
	
	def test_bold(self):
		teststrings = ['**teststring**','**teststring**','this is a **test string** for bbcode','this **is** multiple **bold ** in a string']
		results = [markdownformatter.parseStringBBcode(string) for string in teststrings]
		self.assertListEqual(results, ['[B]teststring[/B]', '[B]teststring[/B]', 'this is a [B]test string[/B] for bbcode','this [B]is[/B] multiple [B]bold [/B] in a string'])

	def test_italics(self):
		teststrings = ['*teststring*','*teststring*','this is a *test string* for bbcode', 'this *is* multiple *italics * in a string']
		results = [markdownformatter.parseStringBBcode(string) for string in teststrings]
		self.assertListEqual(results, ['[I]teststring[/I]','[I]teststring[/I]','this is a [I]test string[/I] for bbcode', 'this [I]is[/I] multiple [I]italics [/I] in a string'])

	def test_strong(self):
		teststrings = ['***teststring***', '***teststring***','this is a ***test string*** for bbcode']
		results = [markdownformatter.parseStringBBcode(string) for string in teststrings]
		self.assertListEqual(results, ['[B][I]teststring[/I][/B]','[B][I]teststring[/I][/B]', 'this is a [B][I]test string[/I][/B] for bbcode'])

	def test_linksimple(self):
		teststrings = ['<testing.com/>','<testing.com>','<testing.com> <example.net>']
		results = [markdownformatter.parseStringBBcode(string) for string in teststrings]
		self.assertListEqual(results, ['[URL]testing.com/[/URL]','[URL]testing.com[/URL]','[URL]testing.com[/URL] [URL]example.net[/URL]'])

	def test_linkcomplex(self):
		teststrings = ['[test link](example.com)','[test link](example.com)[other link](second.test)']
		results = [markdownformatter.parseStringBBcode(string) for string in teststrings]
		self.assertListEqual	(results, ['[URL=example.com]test link[/URL]', '[URL=example.com]test link[/URL][URL=second.test]other link[/URL]'])

	def test_linkmixed(self):
		teststrings = ['[test link](example.com) <test.net>']
		results = [markdownformatter.parseStringBBcode(string) for string in teststrings]
		self.assertListEqual(results, ['[URL=example.com]test link[/URL][URL]test.net[/URL]'])

	def test_complex(self):
		teststrings = ['This *is* a **complicated** string with ***many*** [BBcode](test.com) options like <example.net> for example']
		results = [markdownformatter.parseStringBBcode(string) for string in teststrings]
		self.assertListEqual(results, ['This [I]is[/I] a [B]complicated[/B] string with [I][B]many[/B][/I] [URL=test.com]BBcode[/URL] options like [URL]example.net[/URL] for example'])


if __name__ == '__main__':
	unittest.main()