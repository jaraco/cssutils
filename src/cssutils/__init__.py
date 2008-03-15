#!/usr/bin/env python
"""cssutils - CSS Cascading Style Sheets library for Python

    Copyright (C) 2004-2008 Christof Hoeke

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

A Python package to parse and build CSS Cascading Style Sheets.

Based upon and partly implements the following specifications (DOM only, not any rendering facilities):

`DOM Level 2 Style CSS <http://www.w3.org/TR/DOM-Level-2-Style/css.html>`__
    DOM for package css
`DOM Level 2 Style Stylesheets <http://www.w3.org/TR/DOM-Level-2-Style/stylesheets.html>`__
    DOM for package stylesheets
`CSSOM <http://dev.w3.org/csswg/cssom/>`__
    A few details (mainly the NamespaceRule DOM) is taken from here. Plan is to move implementation to the stuff defined here which is newer but still no REC so might change in the future

`CSS 2.1 <http://www.w3.org/TR/CSS21/>`__
    Rules and properties are defined here
`CSS 2.1 Errata  <http://www.w3.org/Style/css2-updates/CR-CSS21-20070719-errata.html>`__
    A few erratas, mainly the definition of CHARSET_SYM tokens
`MediaQueries <http://www.w3.org/TR/css3-mediaqueries/>`__
    MediaQueries are part of ``stylesheets.MediaList`` since v0.9.4, used in @import and @media rules.
`Namespaces <http://www.w3.org/TR/css3-namespace/>`__
    Added in v0.9.1 and updated to definition in CSSOM in v0.9.4
`Selectors <http://www.w3.org/TR/css3-selectors/>`__
    The selector syntax defined here (and not in CSS 2.1) should be parsable with cssutils (*should* mind though ;) )


Please visit http://cthedot.de/cssutils/ for full details and updates.

Tested with Python 2.5 on Windows XP.


This library is optimized for usage of ``from cssutils import *`` which
import subpackages ``css`` and ``stylesheets``, CSSParser and
CSSSerializer classes only.

Usage may be::

    >>> from cssutils import *
    >>> parser = CSSParser()
    >>> sheet = parser.parseString(u'a { color: red}')
    >>> print sheet.cssText

"""
__all__ = ['css', 'stylesheets', 'CSSParser', 'CSSSerializer']
__docformat__ = 'restructuredtext'
__author__ = 'Christof Hoeke with contributions by Walter Doerwald'
__date__ = '$LastChangedDate::                            $:'
__version__ = '0.9.5b1 $Id$'

import codec

# order of imports is important (maybe as it is partly circular)
import xml.dom

import errorhandler
log = errorhandler.ErrorHandler()

import util
import css
import stylesheets
from parse import CSSParser

from serialize import CSSSerializer
ser = CSSSerializer()

# used by Selector defining namespace prefix '*' 
_ANYNS = -1

class DOMImplementationCSS(object):
    """
    This interface allows the DOM user to create a CSSStyleSheet
    outside the context of a document. There is no way to associate
    the new CSSStyleSheet with a document in DOM Level 2.

    This class is its *own factory*, as it is given to
    xml.dom.registerDOMImplementation which simply calls it and receives
    an instance of this class then.
    """
    _features = [
        ('css', '1.0'),
        ('css', '2.0'),
        ('stylesheets', '1.0'),
        ('stylesheets', '2.0')
    ]

    def createCSSStyleSheet(self, title, media):
        """
        Creates a new CSSStyleSheet.

        title of type DOMString
            The advisory title. See also the Style Sheet Interfaces
            section.
        media of type DOMString
            The comma-separated list of media associated with the new style
            sheet. See also the Style Sheet Interfaces section.

        returns
            CSSStyleSheet: A new CSS style sheet.

        TODO: DOMException
            SYNTAX_ERR: Raised if the specified media string value has a
            syntax error and is unparsable.
        """
        return css.CSSStyleSheet(title=title, media=media)

    def createDocument(self, *args):
        # not needed to HTML, also not for CSS?
        raise NotImplementedError

    def createDocumentType(self, *args):
        # not needed to HTML, also not for CSS?
        raise NotImplementedError

    def hasFeature(self, feature, version):
        return (feature.lower(), unicode(version)) in self._features

xml.dom.registerDOMImplementation('cssutils', DOMImplementationCSS)


def parseString(*a, **k):
    return CSSParser().parseString(*a, **k)
parseString.__doc__ = CSSParser.parseString.__doc__

def parse(*a, **k):
    return CSSParser().parse(*a, **k)
parse.__doc__ = CSSParser.parse.__doc__

def parseURL(*a, **k):
    return CSSParser().parseURL(*a, **k)
parseURL.__doc__ = CSSParser.parseURL.__doc__


# set "ser", default serializer
def setSerializer(serializer):
    """
    sets the global serializer used by all class in cssutils
    """
    global ser
    ser = serializer


def getUrls(sheet):
    """
    Utility function to get all ``url(urlstring)`` values in 
    ``CSSImportRules`` and ``CSSStyleDeclaration`` objects (properties)
    of given CSSStyleSheet ``sheet``.

    This function is a generator. The url values exclude ``url(`` and ``)``
    and surrounding single or double quotes.
    """
    for importrule in (r for r in sheet if r.type == r.IMPORT_RULE):
        yield importrule.href

    def getUrl(v):
        if v.CSS_PRIMITIVE_VALUE == v.cssValueType and\
           v.CSS_URI == v.primitiveType:
                return v.getStringValue()

    def styleDeclarations(base):
        "recursive generator to find all CSSStyleDeclarations"
        if hasattr(base, 'cssRules'):
            for rule in base.cssRules:
                for s in styleDeclarations(rule):
                    yield s
        elif hasattr(base, 'style'):
            yield base.style

    for style in styleDeclarations(sheet):
        for p in style.getProperties(all=True):
            v = p.cssValue
            if v.CSS_VALUE_LIST == v.cssValueType:
                for item in v:
                    u = getUrl(item)
                    if u is not None:
                        yield u
            elif v.CSS_PRIMITIVE_VALUE == v.cssValueType:
                u = getUrl(v)
                if u is not None:
                    yield u
        
def replaceUrls(sheet, replacer):
    """
    Utility function to replace all ``url(urlstring)`` values in 
    ``CSSImportRules`` and ``CSSStyleDeclaration`` objects (properties)
    of given CSSStyleSheet ``sheet``.

    ``replacer`` must be a function which is called with a single
    argument ``urlstring`` which is the current value of url()
    excluding ``url(`` and ``)`` and surrounding single or double quotes.
    """
    for importrule in (r for r in sheet if r.type == r.IMPORT_RULE):
        importrule.href = replacer(importrule.href)

    def setProperty(v):
        if v.CSS_PRIMITIVE_VALUE == v.cssValueType and\
           v.CSS_URI == v.primitiveType:
                v.setStringValue(v.CSS_URI,
                                 replacer(v.getStringValue()))

    def styleDeclarations(base):
        "recursive generator to find all CSSStyleDeclarations"
        if hasattr(base, 'cssRules'):
            for rule in base.cssRules:
                for s in styleDeclarations(rule):
                    yield s
        elif hasattr(base, 'style'):
            yield base.style

    for style in styleDeclarations(sheet):
        for p in style.getProperties(all=True):
            v = p.cssValue
            if v.CSS_VALUE_LIST == v.cssValueType:
                for item in v:
                    setProperty(item)
            elif v.CSS_PRIMITIVE_VALUE == v.cssValueType:
                setProperty(v)


if __name__ == '__main__':
    print __doc__
