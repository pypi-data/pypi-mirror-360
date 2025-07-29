'''
Span Attribute Extension for Python-Markdown
============================================

Wraps inline content in <span> elements using attribute list syntax:

    [content]{#id .class key='value'}

GitHub: https://github.com/frammenti/markdown-span-attr
PyPI: https://pypi.org/project/markdown-span-attr/

Copyright 2025 Francesca Massarenti <fra.mmenti@inventati.org>
License: MIT
'''

from markdown.test_tools import TestCase
from span_attr import makeExtension
import logging

def setup_module(module):
    logging.getLogger("span_attr").setLevel(logging.DEBUG)


class TestSpans(TestCase):

    default_kwargs = {'extensions': ['attr_list', 'wikilinks', makeExtension()]}

    def assertMarkdownRendersInline(self, source, expected, expected_attrs=None, **kwargs):
        return self.assertMarkdownRenders(source, f'<p>{expected}</p>', expected_attrs, **kwargs)

    def test_basic_span(self):
        target = '<span class="hl red" data-name="Red" id="r">highlighted</span>'
        self.assertMarkdownRendersInline(
            '[highlighted]{#r .hl .red data-name="Red"}',
            target
        )
        self.assertMarkdownRendersInline(
            '[highlighted]{ #r .hl .red data-name="Red" }',
            target
        )
        self.assertMarkdownRendersInline(
            '[highlighted]{: #r .hl .red data-name="Red" }',
            target
        )
        self.assertMarkdownRendersInline(
            '[one]{#1}[two]{#2}[three]{#3}',
            '<span id="1">one</span><span id="2">two</span><span id="3">three</span>'
        )
        self.assertMarkdownRendersInline(
            '[one]{#1} [two]{#2} [three]{#3}',
            '<span id="1">one</span> <span id="2">two</span> <span id="3">three</span>'
        )

    def test_empty_span(self):
        self.assertMarkdownRendersInline(
            '[]{.empty}',
            '<span class="empty"></span>'
        )
        self.assertMarkdownRendersInline(
            '[]{}',
            '[]{}'
        )
        self.assertMarkdownRendersInline(
            '[empty]{}',
            '[empty]{}'
        )
        self.assertMarkdownRendersInline(
            '[[]]{.empty}',
            '<span class="empty">[]</span>'
        )
        self.assertMarkdownRendersInline(
            '[[]{}]{.empty}',
            '[[]{}]{.empty}'
        )
        self.assertMarkdownRendersInline(
            '[[[]{#em}]{#pt}]{#y}',
            '<span id="y"><span id="pt"><span id="em"></span></span></span>'
        )
        self.assertMarkdownRendersInline(
            '[[[]{.hello}]{}]{}',
            '[[<span class="hello"></span>}]{}]{'
        )
        self.assertMarkdownRendersInline(
            '[[[]{}]{}]{.goodbye}',
            '[[[]{}]{}]{.goodbye}'
        )
        self.assertMarkdownRendersInline(
            '[[[]]]{.goodbye}',
            '[[[]]]{.goodbye}'
        )

    def test_wrong_span(self):
        self.assertMarkdownRendersInline(
            '[wrong]',
            '[wrong]'
        )
        self.assertMarkdownRendersInline(
            '[wrong]{',
            '[wrong]{'
        )
        self.assertMarkdownRendersInline(
            '[wrong]]{#w}',
            '[wrong]]{#w}'
        )
        self.assertMarkdownRendersInline(
            '[[wrong]{#w}',
            '[<span id="w">wrong</span>'
        )

    def test_conflict_with_attr_list(self):
        self.assertMarkdownRenders(
            '## [Nice span]{: #nice } {: .heading }',
            '<h2 class="heading"><span id="nice">Nice span</span></h2>'
        )
        self.assertMarkdownRenders(
            '## [Nice span]{: #nice }{: .heading }',
            '<h2><span id="nice">Nice span</span>}{: .heading </h2>'
        )

    def test_nested_inline_link(self):
        self.assertMarkdownRendersInline(
            '[[inline](#link)]{#outer}',
            '<span id="outer"><a href="#link">inline</a></span>'
        )
        self.assertMarkdownRendersInline(
            '[[inline](#link){#inner}]{#outer}',
            '<span id="outer"><a href="#link" id="inner">inline</a></span>'
        )
        self.assertMarkdownRendersInline(
            '[[inline](#link)]{#outer}is]{#wrong}',
            '<span id="outer"><a href="#link">inline</a></span>}is]{#wrong'
        )
        self.assertMarkdownRendersInline(
            '[[inline](#link)]]{#outer}is]{#wronger}',
            '[<a href="#link">inline</a>]]{#outer}is]{#wronger}'
        )

    def test_nested_reference_link(self):
        self.assertMarkdownRendersInline(
            '[ref]: # "Hello"\n\n[Some [reference][ref] link]{#outer}',
            '<span id="outer">Some <a href="#" title="Hello">reference</a> link</span>'
        )
        self.assertMarkdownRendersInline(
            '[[I miss the][ref]]{#outer}',
            '<span id="outer">[I miss the][ref]</span>'
        )
        self.assertMarkdownRendersInline(
            '[ref]: # "Brag"\n\n[[I do not][ref]]{#outer}',
            '<span id="outer"><a href="#" title="Brag">I do not</a></span>'
        )
        self.assertMarkdownRendersInline(
            '[strange]: # "??"\n\n[[I am][strange]{.very}]{#outer}',
            '<span id="outer"><a class="very" href="#" title="??">I am</a></span>'
        )
        self.assertMarkdownRendersInline(
            '[crooked]: # "Not ok"\n\n[[I am][crooked]{#outer}',
            '[<a href="#" id="outer" title="Not ok">I am</a>'
        )

    def test_nested_wikilink(self):
        self.assertMarkdownRendersInline(
            '[[im a wiki]]{#w}',
            '<a class="wikilink" href="/im_a_wiki/" id="w">im a wiki</a>'
        )
        self.assertMarkdownRendersInline(
            "[[i'm not a wiki]]{#nw}",
            """<span id="nw">[i'm not a wiki]</span>"""
        )
        self.assertMarkdownRendersInline(
            '[not[a wiki]]{#nw}',
            '<span id="nw">not[a wiki]</span>'
        )
        self.assertMarkdownRendersInline(
            '[[not a wiki] ]{#nw}',
            '<span id="nw">[not a wiki] </span>'
        )
        self.assertMarkdownRendersInline(
            '[[not a]wiki]{#nw}',
            '<span id="nw">[not a]wiki</span>'
        )
        self.assertMarkdownRendersInline(
            '[[[wiki]]{#w}is]{#correct}',
            '<span id="correct"><a class="wikilink" href="/wiki/" id="w">wiki</a>is</span>'
        )
        self.assertMarkdownRendersInline(
            '[[[]]{#nw}is not]{#correct}',
            '<span id="correct"><span id="nw">[]</span>is not</span>'
        )
        self.assertMarkdownRendersInline(
            '[[wrong]]]{#w}',
            '<a class="wikilink" href="/wrong/">wrong</a>]{#w}'
        )

    def test_nested_spans(self):
        self.assertMarkdownRendersInline(
            '[a [b [c [d [e]{#e}]{#d}]{#c}]{#b}]{#a}',
            '<span id="a">a <span id="b">b <span id="c">c <span id="d">d <span id="e">e</span></span></span></span></span>'
        )
        self.assertMarkdownRendersInline(
            '[a [b]{#b] }]{#a}',
            '[a <span id="b]">b</span>}]{#a'
        )
        self.assertMarkdownRendersInline(
            '[Maybe [it [works]{.great}]{.hope}](#maybe){.less}',
            '<a class="less" href="#maybe">Maybe <span class="hope">it <span class="great">works</span></span></a>'
        )
        self.assertMarkdownRendersInline(
            '[maybe]: # "Not"\n\n[Maybe [it [works]{.great}]{.hope}][maybe]{.less}',
            '<a class="less" href="#" title="Not">Maybe <span class="hope">it <span class="great">works</span></span></a>'
        )

    def test_nested_all(self):
        self.assertMarkdownRendersInline(
            '[horace]: viaf.org/viaf/100227522 "Quintus Horatius Flaccus"\n\n[In saying that [Horace][horace]{.p} is [«[verbis [felicissime]{.emph} audax](#quint1){.cit}»]{.q} [daring in his choice of [[words]]{#w1}]]{ana="#s26"}',
            '<span ana="#s26">In saying that <a class="p" href="viaf.org/viaf/100227522" title="Quintus Horatius Flaccus">Horace</a> is <span class="q">«<a class="cit" href="#quint1">verbis <span class="emph">felicissime</span> audax</a>»</span> [daring in his choice of <a class="wikilink" href="/words/" id="w1">words</a>]</span>'
        )

    def test_html_tags(self):
        self.assertMarkdownRendersInline(
            '[*transilire lineas impune*]{: .q title="Varro, <em>De Lingua Latina</em> IX 5" }',
            '<span class="q" title="Varro, <em>De Lingua Latina</em> IX 5"><em>transilire lineas impune</em></span>'
        )
        self.assertMarkdownRendersInline(
            '[<span>seeing</span>]{.double}',
            '<span class="double"><span>seeing</span></span>'
        )
        self.assertMarkdownRendersInline(
            '*[italic]{.em}*',
            '<em><span class="em">italic</span></em>'
        )
        self.assertMarkdownRendersInline(
            '[5 > 3]{.math}',
            '<span class="math">5 &gt; 3</span>'
        )

    def test_newline(self):
        self.assertMarkdownRendersInline(
            '[line\nbreak]{.test}',
            '<span class="test">line\nbreak</span>'
        )
        self.assertMarkdownRenders(
            '[long\n\nbreak]{.ohno}',
            '<p>[long</p>\n<p>break]{.ohno}</p>'
        )

