#!/usr/bin/env python
"""serializer classes for CSS classes

TODO:
- indent subrules if selector is subselector

"""
__all__ = ['CSSSerializer']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import re
import cssutils

class Preferences(object):
    """
    controls output of CSSSerializer

    defaultAtKeyword = True
        Should the literal @keyword from src CSS be used or the default
        form, e.g. if ``True``: ``@import`` else: ``@i\mport``
    defaultPropertyName = True
        Should the normalized propertyname be used or the one given in
        the src file, e.g. if ``True``: ``color`` else: ``c\olor``

        Only used if ``keepAllProperties==False``.

    importHrefFormat = None
        Uses hreftype if ``None`` or explicit ``'string'`` or ``'uri'``
    indent = 4 * ' '
        Indentation of e.g Properties inside a CSSStyleDeclaration
    keepAllProperties = False
        If ``True`` all properties set in the original CSSStylesheet
        are kept meaning even properties set twice with the exact same
        same name are kept!
    keepComments = True
        If ``False`` removes all CSSComments
    lineNumbers = False
        Only used if a complete CSSStyleSheet is serialized.
    lineSeparator = u'\n'
        How to end a line. This may be set to e.g. u'' for serializing
        of CSSStyleDeclarations usable in HTML style attribute.
    omitLastSemicolon = True
        If ``True`` omits ; after last property of CSSStyleDeclaration
    removeInvalid = True
        Omits invalid rules, MAY CHANGE!
    """
    def __init__(self, indent=u'    ', lineSeparator=u'\n'):
        """
        Always use named instead of positional parameters
        """
        self.defaultAtKeyword = True
        self.defaultPropertyName = True
        self.indent = indent
        self.lineSeparator = lineSeparator
        self.importHrefFormat = None
        self.keepAllProperties = False
        self.keepComments = True
        self.omitLastSemicolon = True
        self.lineNumbers = False
        self.removeInvalid = True

class CSSSerializer(object):
    """
    Methods to serialize a CSSStylesheet and its parts

    To use your own serializing method the easiest is to subclass CSS
    Serializer and overwrite the methods you like to customize.
    """
    __notinurimatcher = re.compile(ur'''.*?[\)\s\;]''', re.U).match
    # chars not in URI without quotes around

    def __init__(self, prefs=None):
        """
        prefs
            instance of Preferences
        """
        if not prefs:
            prefs = Preferences()
        self.prefs = prefs
        self.ttypes = cssutils.token.Token
        self._level = 0 # current nesting level

    def _serialize(self, text):
        if self.prefs.lineNumbers:
            pad = len(str(text.count(self.prefs.lineSeparator)+1))
            out = []
            for i, line in enumerate(text.split(self.prefs.lineSeparator)):
                out.append((u'%*i: %s') % (pad, i+1, line))
            text = self.prefs.lineSeparator.join(out)
        return text

    def _noinvalids(self, x):
        """
        returns
            True if x.valid or prefs.removeInvalid == False
            else False
        """
        if self.prefs.removeInvalid and \
           hasattr(x, 'valid') and not x.valid:
            return True
        else:
            return False

    def _escapestring(self, s, delim=u'"'):
        """
        escapes delim charaters in string s with \delim
        """
        return s.replace(delim, u'\\%s' % delim)

    def _getatkeyword(self, rule, default):
        """
        used by all @rules to get the keyword used
        dependent on prefs setting defaultAtKeyword
        """
        if self.prefs.defaultAtKeyword:
            return default
        else:
            return rule.atkeyword

    def _getpropertyname(self, property, actual):
        """
        used by all styledeclarations to get the propertyname used
        dependent on prefs setting defaultPropertyName
        """
        if self.prefs.defaultPropertyName and \
           not self.prefs.keepAllProperties:
            return property.normalname
        else:
            return actual

    def _indentblock(self, text, level):
        """
        indent a block like a CSSStyleDeclaration to the given level
        which may be higher than self._level (e.g. for CSSStyleDeclaration)
        """
        if not self.prefs.lineSeparator:
            return text
        return self.prefs.lineSeparator.join(
            [u'%s%s' % (level * self.prefs.indent, line)
                for line in text.split(self.prefs.lineSeparator)]
        )

    def _uri(self, uri):
        """
        returns uri enclosed in " if necessary
        """
        if CSSSerializer.__notinurimatcher(uri):
            return '"%s"' % uri
        else:
            return uri

    def do_stylesheets_mediaquery(self, mediaquery):
        """
        a single media used in medialist
        """
        if len(mediaquery.seq) == 0:
            return u''
        else:
            out = []
            for part in mediaquery.seq:
                if isinstance(part, cssutils.css.Property): # Property
                    out.append(u'(%s)' % part.cssText)
                elif hasattr(part, 'cssText'): # comments
                    out.append(part.cssText)
                else:
                    # TODO: media queries!
                    out.append(part)
            return u' '.join(out)

    def do_stylesheets_medialist(self, medialist):
        """
        comma-separated list of media, default is 'all'

        If "all" is in the list, every other media *except* "handheld" will
        be stripped. This is because how Opera handles CSS for PDAs.
        """
        if len(medialist) == 0:
            return u'all'
        else:
            return u', '.join((mq.mediaText for mq in medialist))

    def do_CSSStyleSheet(self, stylesheet):
        out = []
        for rule in stylesheet.cssRules:
            cssText = rule.cssText
            if cssText:
                out.append(cssText)
        return self._serialize(self.prefs.lineSeparator.join(out))

    def do_CSSComment(self, rule):
        """
        serializes CSSComment which consists only of commentText
        """
        if self.prefs.keepComments and rule._cssText:
            return rule._cssText
        else:
            return u''

    def do_CSSCharsetRule(self, rule):
        """
        serializes CSSCharsetRule
        encoding: string

        always @charset "encoding";
        no comments or other things allowed!
        """
        if not rule.encoding or self._noinvalids(rule):
            return u''
        return u'@charset "%s";' % self._escapestring(rule.encoding)

    def do_CSSImportRule(self, rule):
        """
        serializes CSSImportRule

        href
            string
        hreftype
            'uri' or 'string'
        media
            cssutils.stylesheets.medialist.MediaList

        + CSSComments
        """
        if not rule.href or self._noinvalids(rule):
            return u''
        out = [u'%s ' % self._getatkeyword(rule, u'@import')]
        for part in rule.seq:
            if rule.href == part:
                if self.prefs.importHrefFormat == 'uri':
                    out.append(u'url(%s)' % self._uri(part))
                elif self.prefs.importHrefFormat == 'string' or \
                   rule.hreftype == 'string':
                    out.append(u'"%s"' % self._escapestring(part))
                else:
                    out.append(u'url(%s)' % self._uri(part))
            elif isinstance(
                  part, cssutils.stylesheets.medialist.MediaList):
                mediaText = self.do_stylesheets_medialist(part).strip()
                if mediaText and not mediaText == u'all':
                    out.append(u' %s' % mediaText)
            elif hasattr(part, 'cssText'): # comments
                out.append(part.cssText)
        return u'%s;' % u''.join(out)

    def do_CSSNamespaceRule(self, rule):
        """
        serializes CSSNamespaceRule

        uri
            string
        prefix
            string

        + CSSComments
        """
        if not rule.uri or self._noinvalids(rule):
            return u''

        out = [u'%s' % self._getatkeyword(rule, u'@namespace')]
        for part in rule.seq:
            if rule.prefix == part and part != u'':
                out.append(u' %s' % part)
            elif rule.uri == part:
                out.append(u' "%s"' % self._escapestring(part))
            elif hasattr(part, 'cssText'): # comments
                out.append(part.cssText)
        return u'%s;' % u''.join(out)

    def do_CSSMediaRule(self, rule):
        """
        serializes CSSMediaRule

        + CSSComments
        """
        if not rule.cssRules or self._noinvalids(rule.media):
            return u''
        mediaText = self.do_stylesheets_medialist(rule.media).strip()
        out = [u'%s %s {%s' % (self._getatkeyword(rule, u'@media'),
                               mediaText, self.prefs.lineSeparator)]
        for r in rule.cssRules:
            rtext = r.cssText
            if rtext:
                # indent each line of cssText
                out.append(self._indentblock(rtext, self._level + 1))
                out.append(self.prefs.lineSeparator)
        return u'%s%s}' % (u''.join(out), (self._level + 1) * self.prefs.indent)

    def do_CSSPageRule(self, rule):
        """
        serializes CSSPageRule

        selectorText
            string
        style
            CSSStyleDeclaration

        + CSSComments
        """
        self._level += 1
        try:
            styleText = self.do_css_CSSStyleDeclaration(rule.style)
        finally:
            self._level -= 1

        if not styleText or self._noinvalids(rule):
            return u''

        return u'%s%s {%s%s%s%s}' % (
            self._getatkeyword(rule, u'@page'),
            self.do_pageselector(rule.seq),
            self.prefs.lineSeparator,
            self._indentblock(styleText, self._level + 1),
            self.prefs.lineSeparator,
            (self._level + 1) * self.prefs.indent
            )

    def do_pageselector(self, seq):
        """
        a selector of a CSSPageRule including comments
        """
        if len(seq) == 0 or self._noinvalids(seq):
            return u''
        else:
            out = []
            for part in seq:
                if hasattr(part, 'cssText'):
                    out.append(part.cssText)
                else:
                    out.append(part)
            return u' %s' % u''.join(out)

    def do_CSSUnknownRule(self, rule):
        """
        serializes CSSUnknownRule
        anything until ";" or "{...}"
        + CSSComments
        """
        if rule.atkeyword and not self._noinvalids(rule):
            out = [u'@%s' % rule.atkeyword]
            for part in rule.seq:
                if isinstance(part, cssutils.css.csscomment.CSSComment):
                    if self.prefs.keepComments:
                        out.append(part.cssText)
                else:
                    out.append(part)
            if not (out[-1].endswith(u';') or out[-1].endswith(u'}')):
                out.append(u';')
            return u''.join(out)
        else:
            return u''

    def do_CSSStyleRule(self, rule):
        """
        serializes CSSStyleRule

        selectorList
        style

        + CSSComments
        """
        selectorText = self.do_css_SelectorList(rule.selectorList)
        if not selectorText or self._noinvalids(rule):
            return u''
        self._level += 1
        styleText = u''
        try:
            styleText = self.do_css_CSSStyleDeclaration(rule.style)
        finally:
            self._level -= 1

        if not styleText:
            return u'%s {}' % (
                selectorText,
                )
        else:
            return u'%s {%s%s%s%s}' % (
                selectorText,
                self.prefs.lineSeparator,
                self._indentblock(styleText, self._level + 1),
                self.prefs.lineSeparator,
                (self._level + 1) * self.prefs.indent,
                )

    def do_css_SelectorList(self, selectorlist):
        """
        comma-separated list of Selectors
        """
        if len(selectorlist.seq) == 0 or self._noinvalids(selectorlist):
            return u''
        else:
            out = []
            for part in selectorlist.seq:
                if hasattr(part, 'cssText'):
                    out.append(part.cssText)
                elif u',' == part:
                    out.append(u', ')
                elif isinstance(part, cssutils.css.cssstylerule.Selector):
                    out.append(self.do_css_Selector(part).strip())
                else:
                    out.append(part) # ?
            return u', '.join(out)

    def do_css_Selector(self, selector):
        """
        a single selector including comments

        TODO: style combinators like + >
        """
        if len(selector.seq) == 0 or self._noinvalids(selector):
            return u''
        else:
            out = []
            for part in selector.seq:
                if hasattr(part, 'cssText'):
                    out.append(part.cssText)
                else:
                    if type(part) == dict:
                        out.append(part['value'])
                    else:
                        out.append(part)
            return u''.join(out)

    def do_css_CSSStyleDeclaration(self, style, separator=None):
        """
        Style declaration of CSSStyleRule
        """
        if len(style.seq) == 0 or self._noinvalids(style):
            return u''
        else:
            if separator is None:
                separator = self.prefs.lineSeparator

            if self.prefs.keepAllProperties:
                parts = style.seq
            else:
                # find distinct names
                nnames = set()
                for x in style.seq:
                    if isinstance(x, cssutils.css.Property):
                        nnames.add(x.normalname)
                # filter list
                parts = []
                for x in reversed(style.seq):
                    if isinstance(x, cssutils.css.Property):
                        if x.normalname in nnames:
                            parts.append(x)
                            nnames.remove(x.normalname)
                    else:
                        parts.append(x)
                parts.reverse()

            out = []
            for (i, part) in enumerate(parts):
                if isinstance(part, cssutils.css.CSSComment):
                    # CSSComment
                    if self.prefs.keepComments:
                        out.append(part.cssText)
                        out.append(separator)
                elif isinstance(part, cssutils.css.Property):
                    # PropertySimilarNameList
                    out.append(self.do_Property(part))
                    if not (self.prefs.omitLastSemicolon and i==len(parts)-1):
                        out.append(u';')
                    out.append(separator)
                else:
                    # other?
                    out.append(part)

            if out and out[-1] == separator:
                del out[-1]

            return u''.join(out)

    def do_Property(self, property):
        """
        Style declaration of CSSStyleRule

        Property has a seqs attribute which contains seq lists for
        name, a CSSvalue and a seq list for priority
        """
        if not property.seqs[0] or self._noinvalids(property):
            return u''
        else:
            out = []
            nameseq, cssvalue, priorityseq = property.seqs

            #name
            for part in nameseq:
                if hasattr(part, 'cssText'):
                    out.append(part.cssText)
                elif property.name == part:
                    out.append(self._getpropertyname(property, part))
                else:
                    out.append(part)

            if out and (not property._mediaQuery or
                        property._mediaQuery and cssvalue.cssText):
                # MediaQuery may consist of name only
                out.append(u': ')

            # value
            out.append(cssvalue.cssText)

            # priority
            if out and priorityseq:
                out.append(u' ')
                for part in priorityseq:
                    if hasattr(part, 'cssText'): # comments
                        out.append(part.cssText)
                    else:
                        out.append(part)

        return u''.join(out)

    def do_Property_priority(self, priorityseq):
        """
        a Properties priority "!" S* "important"
        """
        out = []
        for part in priorityseq:
            if hasattr(part, 'cssText'): # comments
                out.append(u' ')
                out.append(part.cssText)
                out.append(u' ')
            else:
                out.append(part)
        return u''.join(out).strip()

    def do_css_CSSValue(self, cssvalue):
        """
        serializes a CSSValue
        """
        if not cssvalue:
            return u''
        else:
            out = []
            for part in cssvalue.seq:
                if hasattr(part, 'cssText'):
                    # comments or CSSValue if a CSSValueList
                    out.append(part.cssText)
                elif isinstance(part, basestring) and part == u',':
                    out.append(', ')
                else:
                    out.append(part)
            return (u''.join(out)).strip()
