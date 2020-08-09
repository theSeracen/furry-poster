#!/usr/bin/env python3

import pytest

from bs4 import BeautifulSoup

from furryposter.utilities import htmlformatter


def test_boldtoBBcode():
    teststrings = [BeautifulSoup(r"""<p style=" margin-top:0px; margin-bottom:16px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:36px;"><span style=" font-family:'Calibri';">This has a </span><span style=" font-family:'Calibri'; font-weight:600;">bold</span><span style=" font-family:'Calibri';"> test</span></p>""").p]
    results = [htmlformatter.parseStringBBcode(
        test) for test in teststrings]
    assert results == ['This has a [B]bold[/B] test']


def test_boldtoMarkdown():
    teststrings = [BeautifulSoup(r"""<p style=" margin-top:0px; margin-bottom:16px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:36px;"><span style=" font-family:'Calibri';">This has a </span><span style=" font-family:'Calibri'; font-weight:600;">bold</span><span style=" font-family:'Calibri';"> test</span></p>""").p]
    results = [htmlformatter.parseStringMarkdown(
        test) for test in teststrings]
    assert results == ['This has a **bold** test']


def test_italicstoBBcode():
    teststrings = [BeautifulSoup(r"""<p style=" margin-top:0px; margin-bottom:16px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:36px;"><span style=" font-family:'Calibri';">This has an </span><span style=" font-family:'Calibri'; font-style:italic;">italic</span><span style=" font-family:'Calibri';"> test</span></p>""").p]
    results = [htmlformatter.parseStringBBcode(
        test) for test in teststrings]
    assert results == ['This has an [I]italic[/I] test']


def test_italicstoMarkdown():
    teststrings = [BeautifulSoup(r"""<p style=" margin-top:0px; margin-bottom:16px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:36px;"><span style=" font-family:'Calibri';">This has an </span><span style=" font-family:'Calibri'; font-style:italic;">italic</span><span style=" font-family:'Calibri';"> test</span></p>""").p]
    results = [htmlformatter.parseStringMarkdown(
        test) for test in teststrings]
    assert results == ['This has an *italic* test']


def test_strongtoBBcode():
    teststrings = [BeautifulSoup(r"""<p style=" margin-top:0px; margin-bottom:16px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:36px;"><span style=" font-family:'Calibri';">This has a </span><span style=" font-family:'Calibri'; font-weight:600; font-style:italic;">strong</span><span style=" font-family:'Calibri';"> test</span></p>""").p]
    results = [htmlformatter.parseStringBBcode(
        test) for test in teststrings]
    assert results == ["This has a [B][I]strong[/I][/B] test"]


def test_strongtoMarkdown():
    teststrings = [BeautifulSoup(r"""<p style=" margin-top:0px; margin-bottom:16px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:36px;"><span style=" font-family:'Calibri';">This has a </span><span style=" font-family:'Calibri'; font-weight:600; font-style:italic;">strong</span><span style=" font-family:'Calibri';"> test</span></p>""").p]
    results = [htmlformatter.parseStringMarkdown(
        test) for test in teststrings]
    assert results == ["This has a ***strong*** test"]


def test_complextoBBcode():
    teststrings = [BeautifulSoup(r"""<p style=" margin-top:0px; margin-bottom:16px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:36px;"><span style=" font-family:'Calibri';">This has an </span><span style=" font-family:'Calibri'; font-style:italic;">italic</span><span style=" font-family:'Calibri';"> and a </span><span style=" font-family:'Calibri'; font-weight:600;">bold</span><span style=" font-family:'Calibri';"> and a </span><span style=" font-family:'Calibri'; font-weight:600; font-style:italic;">strong</span><span style=" font-family:'Calibri';"> in it</span></p>""").p]
    results = [htmlformatter.parseStringBBcode(
        test) for test in teststrings]
    assert results == ['This has an [I]italic[/I] and a [B]bold[/B] and a [B][I]strong[/I][/B] in it']


def test_complextoMarkdown():
    teststrings = [BeautifulSoup(r"""<p style=" margin-top:0px; margin-bottom:16px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:36px;"><span style=" font-family:'Calibri';">This has an </span><span style=" font-family:'Calibri'; font-style:italic;">italic</span><span style=" font-family:'Calibri';"> and a </span><span style=" font-family:'Calibri'; font-weight:600;">bold</span><span style=" font-family:'Calibri';"> and a </span><span style=" font-family:'Calibri'; font-weight:600; font-style:italic;">strong</span><span style=" font-family:'Calibri';"> in it</span></p>""").p]
    results = [htmlformatter.parseStringMarkdown(
        test) for test in teststrings]
    assert results == ['This has an *italic* and a **bold** and a ***strong*** in it']
