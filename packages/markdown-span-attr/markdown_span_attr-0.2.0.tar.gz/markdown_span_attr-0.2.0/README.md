markdown-`span`-attr
====================================

> *Sometimes you really need a span*

[![PyPI Version][version-button]][pypi]
[![MIT License][mitlicense-button]][mitlicense]
[![Python Versions][pyversion-button]][pypi]
[![Build Status][build-button]][build]

A [Python-Markdown] extension that enables inline `<span>` elements with attribute lists:

```markdown
[content]{#id .class key="value"}
```

## Features

- Wraps inline content in `<span>` elements with appended attributes
- Fully compatible with Python-Markdown base and [extended] syntax, including:
  - Inline links
  - Reference links
  - Wikilinks
- Supports nested spans, links, and nesting inside links
- Renders correctly HTML elements inside attributes (e.g., for MkDocs Material [tooltips])
- No parsing overhead — delegates attribute handling to the [`attr_list`][official extension] extension

## Installation

```bash
$ pip install markdown-span-attr
```

## Usage

Enable alongside `attr_list` in Python:

```python
import markdown

md = markdown.Markdown(extensions=['attr_list', 'span_attr'])
```

Or in `mkdocs.yml`:

```yaml
markdown_extensions:
  - attr_list
  - span_attr
```

## Syntax

```markdown
[content]{#id .class key="value"}
```
Renders as:

```html
<span class="class" id="id" key="value">content</span>
```
See the [official extension] for attribute lists syntax.

### Examples

#### Nested content

```markdown
[horace]: #

[[Horace][horace]{.p} is [daring](#quint1){.cit}]{#s1}  # nested reference/inline links
[[audax]{.foreign} [daring]]{#s2}                       # nested spans and unescaped brackets
[[[Poets]] daring in [[words]]{title="Words"}]{#s3}     # wikilinks
```
Renders as:

```html
<span id="s1"><a class="p" href="#">Horace</a> is <a class="cit" href="#quint1">daring</a></span>
<span id="s2"><span class="foreign">audax</span> [daring]</span>
<span id="s3"><a class="wikilink" href="/Poets/">Poets</a> daring in <a class="wikilink" href="/words/" title="Words">words</a></span>
```
#### HTML in attributes

```markdown
[transilire lineas impune]{: .q title="Varro, <em>De Lingua Latina</em> IX 5" }
```

Renders as:

```html
<span class="q" title="Varro, <em>De Lingua Latina</em> IX 5">transilire lineas impune</span>
```

## Why?

Many would say that supporting arbitrary `<span>` elements in Markdown syntax goes against Markdown philosophy, and perhaps it is true. But sometimes you *really* need a readable span in Markdown, and decadence is inescapable, anyway. So at least be safe with `span_attr` not to break compatibility with other extensions.

## Technical Details

### Regular Expression

The extension uses a greedy-safe regular expression to match `[content]{: attr-list}` spans, supporting **nesting** while avoiding premature matches:

```regex
\[([^\[\]]*|(?:[^\[\]]*\[[^\[\]]*\](?!\{)[^\[\]]*)*)\](?=\{\:?[ ]*([^\}\n ][^\n]*)[ ]*\})
```

What it does:

- Matches the *innermost* span first to support nesting (no other attribute span is allowed inside).
- Allows only content with **none or balanced square brackets**.
- Uses a *lookahead* to ensure a valid `{}` attribute list follows.

It matches only `[content]`, while attribute parsing is delegated to [`attr_list`][official extension].

### Processing Priority

The processor is registered with priority `72`. This is chosen to:

- Run **after** `wikilinks` (75), so links are parsed before wrapping them in spans.
- Run **before** `attr_list` (8), so `<span>` elements are inserted before `attr_list` decorates them.

This placement ensures the extension is compatible with link handling and HTML escaping.

### Inline Processors Priority Table ([source])

| Priority | Pattern Name       | Description                                 |
|----------|--------------------|---------------------------------------------|
| 190      | `backtick`         | Code spans                                  |
| 180      | `escape`           | Backslash escapes                           |
| 175      | `footnotes`*       | Footnote references                         |
| 170      | `reference`        | Reference-style links                       |
| 160      | `link`             | Inline links                                |
| 150      | `image_link`       | Inline images                               |
| 140      | `image_reference`  | Reference-style images                      |
| 130      | `short_reference`  | Shortcut reference-style links              |
| 125      | `short_image_ref`  | Shortcut reference-style images             |
| 120      | `autolink`         | Automatic links                             |
| 110      | `automail`         | Automatic email links                       |
| 100      | `linebreak`        | Hard line breaks                            |
|  91      | `html`             | Inline HTML                                 |
|  80      | `entity`           | HTML entities                               |
|  75      | `wikilinks`*       | Wiki-style links                            |
|  72      | `span_attr`*       | _(this extension)_                          |
|  70      | `not_strong`       | Prevent misparsed emphasis                  |
|  60      | `em_strong`        | `*`-style emphasis                          |
|  50      | `em_strong2`       | `_`-style emphasis                          |
|  8       | `attr_list`*       | Attribute lists                             |
|  7       | `abbr`*            | Abbreviations                               |

\*: Extension

<!-- Badges -->
[version-button]: https://img.shields.io/pypi/v/markdown-span-attr.svg
[pypi]: https://pypi.org/project/markdown-span-attr/
[mitlicense-button]: https://img.shields.io/badge/License-MIT-blue.svg
[mitlicense]: https://opensource.org/license/mit/
[pyversion-button]: https://img.shields.io/pypi/pyversions/markdown-span-attr.svg
[build-button]: https://github.com/frammenti/markdown-span-attr/actions/workflows/ci.yml/badge.svg
[build]: https://github.com/frammenti/markdown-span-attr/actions/workflows/ci.yml

<!-- Links -->
[Python-Markdown]: https://python-markdown.github.io/
[official extension]: https://python-markdown.github.io/extensions/attr_list/
[extended]: https://python-markdown.github.io/extensions/#officially-supported-extensions
[tooltips]: https://squidfunk.github.io/mkdocs-material/reference/tooltips/#improved-tooltips
[source]: https://github.com/Python-Markdown/markdown/blob/master/markdown/inlinepatterns.py
