#!/usr/bin/env python3

import pytest

from furryposter.utilities import bbcodeformatter


def test_bold():
    teststrings = [
        '[B]teststring[/B]',
        '[b]teststring[/b]',
        'this is a [B]test string[/B] for bbcode',
        'this [b]is[/b] multiple [B]bold [/b] in a string']

    results = [bbcodeformatter.parseStringMarkdown(
        string) for string in teststrings]
    assert results == ['**teststring**',
                       '**teststring**',
                       'this is a **test string** for bbcode',
                       'this **is** multiple **bold ** in a string']


def test_italics():
    teststrings = [
        '[I]teststring[/I]',
        '[i]teststring[/i]',
        'this is a [I]test string[/I] for bbcode',
        'this [I]is[/I] multiple [i]italics [/I] in a string']

    results = [bbcodeformatter.parseStringMarkdown(
        string) for string in teststrings]
    assert results == ['*teststring*',
                       '*teststring*',
                       'this is a *test string* for bbcode',
                       'this *is* multiple *italics * in a string']


def test_strong():
    teststrings = [
        '[B][I]teststring[/I][/B]',
        '[b][i]teststring[/i][/b]',
        'this is a [B][I]test string[/I][/B] for bbcode']
    results = [bbcodeformatter.parseStringMarkdown(
        string) for string in teststrings]
    assert results == ['***teststring***',
                       '***teststring***',
                       'this is a ***test string*** for bbcode']


def test_linksimple():
    teststrings = [
        '[URL]testing.com/[/URL]',
        '[URL]testing.com[/URL]',
        '[URL]testing.com[/URL] [URL]example.net[/URL]']
    results = [bbcodeformatter.parseStringMarkdown(
        string) for string in teststrings]
    assert results == ['<testing.com/>', '<testing.com>', '<testing.com> <example.net>']


def test_linkcomplex():
    teststrings = [
        '[URL=example.com]test link[/URL]',
        '[URL=example.com]test link[/URL][URL=second.test]other link[/URL]']
    results = [bbcodeformatter.parseStringMarkdown(
        string) for string in teststrings]
    assert results == ['[test link](example.com)',
                       '[test link](example.com)[other link](second.test)']


def test_linkmixed():
    teststrings = ['[URL=example.com]test link[/URL][URL]test.net[/URL]']
    results = [bbcodeformatter.parseStringMarkdown(
        string) for string in teststrings]
    assert results == ['[test link](example.com)<test.net>']


def test_complex():
    teststrings = [
        'This [I]is[/I] a [B]complicated[/B] string with [I][B]many[/B][/I] [URL=test.com]BBcode[/URL] options like [URL]example.net[/URL] for example']
    results = [bbcodeformatter.parseStringMarkdown(
        string) for string in teststrings]
    assert results == [
        'This *is* a **complicated** string with ***many*** [BBcode](test.com) options like <example.net> for example']
