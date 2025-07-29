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

from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as etree
from typing import TYPE_CHECKING

import markdown
from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
    from markdown import Markdown

log = logging.getLogger('span_attr')


class SpanProcessor(InlineProcessor):
    '''
    Matches [content]{: attr-list} inline syntax and wraps the content in a <span> element.

    Requires the 'attr_list' extension to parse the attributes (id, class, key='value').

    Supports nested spans, inline links, reference links, and wikilinks.

    Pattern logic:
        - Captures content inside balanced square brackets.
        - Matches from the innermost span outward to support nesting.
        - Ensures that closing bracket is followed by an attribute list.
    '''

    SPAN_RE = (
        r'\[([^\[\]]*|(?:[^\[\]]*\[[^\[\]]*\](?!\{)[^\[\]]*)*)\]'
        r'(?=\{\:?[ ]*([^\}\n ][^\n]*)[ ]*\})' # same as attr_list pattern
    )

    def handleMatch(self, m: re.Match[str], data: str) -> tuple[Element | None, int | None, int | None]:
        log.debug('MATCH: %s\n         IN:    %s\n', m.group(0), data)

        text = m.group(1)
        el = etree.Element('span')
        el.text = text

        return el, m.start(0), m.end(0)


class SpanExtension(Extension):
    '''
    Registers the span processor with priority 72, just lower than 'wikilinks' (75).

    Requires 'attr_list' extension enabled to parse the attribute list.
    '''

    def extendMarkdown(self, md: Markdown) -> None:
        md.inlinePatterns.register(
            SpanProcessor(SpanProcessor.SPAN_RE, md),
            'span-attr',
            72
        )


def makeExtension(**kwargs):
    return SpanExtension(**kwargs)
