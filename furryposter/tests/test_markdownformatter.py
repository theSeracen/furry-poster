#!/usr/bin/env python3

import pytest

from furryposter.utilities import markdownformatter


def test_bold():
    teststrings = [
        '**teststring**',
        '**teststring**',
        'this is a **test string** for bbcode',
        'this **is** multiple **bold ** in a string']
    results = [markdownformatter.parseStringBBcode(
        string) for string in teststrings]
    assert results == ['[B]teststring[/B]',
                       '[B]teststring[/B]',
                       'this is a [B]test string[/B] for bbcode',
                       'this [B]is[/B] multiple [B]bold [/B] in a string']


def test_italics():
    teststrings = [
        '*teststring*',
        '*teststring*',
        'this is a *test string* for bbcode',
        'this *is* multiple *italics * in a string']
    results = [markdownformatter.parseStringBBcode(
        string) for string in teststrings]
    assert results == ['[I]teststring[/I]',
                       '[I]teststring[/I]',
                       'this is a [I]test string[/I] for bbcode',
                       'this [I]is[/I] multiple [I]italics [/I] in a string']


def test_strong():
    teststrings = [
        '***teststring***',
        '***teststring***',
        'this is a ***test string*** for bbcode']
    results = [markdownformatter.parseStringBBcode(
        string) for string in teststrings]
    assert results == ['[B][I]teststring[/I][/B]',
                       '[B][I]teststring[/I][/B]',
                       'this is a [B][I]test string[/I][/B] for bbcode']


def test_linksimple():
    teststrings = [
        '<testing.com/>',
        '<testing.com>',
        '<testing.com> <example.net>']
    results = [markdownformatter.parseStringBBcode(
        string) for string in teststrings]
    assert results == ['[URL]testing.com/[/URL]',
                       '[URL]testing.com[/URL]',
                       '[URL]testing.com[/URL] [URL]example.net[/URL]']


def test_linkcomplex():
    teststrings = [
        '[test link](example.com)',
        '[test link](example.com)[other link](second.test)']
    results = [markdownformatter.parseStringBBcode(
        string) for string in teststrings]
    assert results == ['[URL=example.com]test link[/URL]',
                       '[URL=example.com]test link[/URL][URL=second.test]other link[/URL]']


def test_linkmixed():
    teststrings = ['[test link](example.com)<test.net>']
    results = [markdownformatter.parseStringBBcode(
        string) for string in teststrings]
    assert results == ['[URL=example.com]test link[/URL][URL]test.net[/URL]']


def test_complex():
    teststrings = [
        'This *is* a **complicated** string with ***many*** [BBcode](test.com) options like <example.net> for example']
    results = [markdownformatter.parseStringBBcode(
        string) for string in teststrings]
    assert results == [
        'This [I]is[/I] a [B]complicated[/B] string with [B][I]many[/I][/B] [URL=test.com]BBcode[/URL] options like [URL]example.net[/URL] for example']
