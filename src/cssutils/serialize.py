#!/usr/bin/env python
"""serializer classes for CSS classes

TODO:
- indent subrules if selector is subselector

"""
__all__ = ['CSSSerializer']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a2 $LastChangedRevision$'

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
        Uses hreftype if ``None`` or explicit 'string' or 'uri'        
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
    removeInvalid = True
        Omits invalid rules, MAY CHANGE!
    setBOM = False
        NOT USED YET
    """
    def __init__(self, indent=u'    '):
        """        
        Always use named instead of positional parameters!
        """
        self.defaultAtKeyword = True
        self.defaultPropertyName = True
        self.indent = indent
        self.importHrefFormat = None
        self.keepAllProperties = False
        self.keepComments = True
        self.lineNumbers = False
        self.removeInvalid = True
        self.setBOM = False # TODO
    

class CSSSerializer(object):
    """
    Methods to serialize a CSSStylesheet and its parts

    To use your own serializing method the easiest is to subclass CSS
    Serializer and overwrite the methods you like to customize.
    """
    def __init__(self, prefs=None):
        """
        prefs
            instance of Preferences
        """
        if not prefs:
            prefs = Preferences()
        self.prefs = prefs
        self.ttypes = cssutils.token.Token
        
        self._map = {
            cssutils.css.cssrule.CSSRule.COMMENT:
                self.do_CSSComment,
            cssutils.css.cssrule.CSSRule.CHARSET_RULE:
                self.do_CSSCharsetRule,
            cssutils.css.cssrule.CSSRule.IMPORT_RULE:
                self.do_CSSImportRule,
            cssutils.css.cssrule.CSSRule.MEDIA_RULE:
                self.do_CSSMediaRule,
            cssutils.css.cssrule.CSSRule.NAMESPACE_RULE:
                self.do_CSSNamespaceRule,
            cssutils.css.cssrule.CSSRule.PAGE_RULE:
                self.do_CSSPageRule,
            cssutils.css.cssrule.CSSRule.STYLE_RULE:
                self.do_CSSStyleRule,
            cssutils.css.cssrule.CSSRule.UNKNOWN_RULE:
                self.do_CSSUnknownRule
            }
        

    def _serialize(self, text):
        if self.prefs.lineNumbers:
            pad = text.count(u'\n') / 10 + 1
            out = []
            for i, line in enumerate(text.split(u'\n')):
                out.append((u'%'+str(pad)+'i: %s') % (i+1, line))
            text = u'\n'.join(out)
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
        return s.replace(delim, u'\%s' % delim)

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


    def _do_unknown(self, rule):
        raise NotImplementedError(
            "Serializer not implemented for %s" % rule)


    def do_stylesheets_medialist(self, medialist):
        """
        comma-separated list of media, default is 'all'

        If "all" is in the list, every other media *except* "handheld" will
        be stripped. This is because how Opera handles CSS for PDAs.
        """
        if len(medialist.seq) == 0:
            return u'all'
        else:
            hasall = bool(
                [1 for part in medialist.seq if part == u'all'])
            hashandheld = bool(
                [1 for part in medialist.seq if part == u'handheld'])
            doneall = donehandheld = False
            out = []
            for part in medialist.seq:
                if hasattr(part, 'cssText'): # comments
                    out.append(part.cssText)
                elif u',' == part and not hasall:
                    out.append(u', ')
                elif not hasall or (
                           hasall and hashandheld and \
                           part in (u'handheld', u'all')):
                    if hasall and hashandheld and (
                        (donehandheld and part == u'all') or\
                        (doneall and part == u'handheld')
                         ):
                        out.append(u', ')
                    if part == u'all':
                        doneall = True
                    else:
                        donehandheld = True
                    out.append(part)
            if out == []:
                out = [u'all']
            return u''.join(out)


    def do_stylesheet(self, stylesheet):
        out = []
        for rule in stylesheet.cssRules:
            cssText = self._map.get(rule.type, self._do_unknown)(rule)
            if cssText:
                out.append(cssText)
        return self._serialize(u'\n'.join(out))


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
                    out.append('url(%s)' % part)
                elif self.prefs.importHrefFormat == 'string' or \
                   rule.hreftype == 'string':
                    out.append('"%s"' % self._escapestring(part))
                else:
                    out.append('url(%s)' % part)
            elif isinstance(
                  part, cssutils.stylesheets.medialist.MediaList):
                mediaText = self.do_stylesheets_medialist(part).strip()
                if mediaText and not mediaText == u'all':
                    out.append(u' %s' % mediaText)
            elif hasattr(part, 'cssText'): # comments
                out.append(part.cssText)
        out.append(';')
        return u''.join(out)


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
                out.append(' %s' % part)
            elif rule.uri == part:
                out.append(' "%s"' % self._escapestring(part))
            elif hasattr(part, 'cssText'): # comments
                out.append(part.cssText)
        out.append(';')
        return u''.join(out)


    def do_CSSMediaRule(self, rule):
        """
        serializes CSSMediaRule

        + CSSComments
        """
        if not rule.cssRules or self._noinvalids(rule.media):
            return u''        
        mediaText = self.do_stylesheets_medialist(rule.media).strip()
        out = [u'%s %s {\n' % (
            self._getatkeyword(rule, u'@media'), mediaText)]
        for r in rule.cssRules:
            rtext = r.cssText
            if rtext:
                rtext = '\n'.join(
                    [u'%s%s' % (self.prefs.indent, line)
                         for line in rtext.split('\n')])
                out.append(rtext + u'\n')
        out.append('%s}' % self.prefs.indent)
        return u''.join(out)


    def do_CSSPageRule(self, rule):
        """
        serializes CSSPageRule

        selectorText
            string
        style
            CSSStyleDeclaration
        
        + CSSComments
        """
        styleText = self.do_css_CSSStyleDeclaration(rule.style)
        if not styleText or self._noinvalids(rule):
            return u''
        
        sel = self.do_pageselector(rule.seq)
        return u'%s%s {%s}' % (
            self._getatkeyword(rule, u'@page'),
            sel,
            self.do_css_CSSStyleDeclaration(rule.style))


    def do_pageselector(self, seq):
        """
        a selector of a CSSPageRule including comments
        """
        if len(seq) == 0 or self._noinvalids(seq):
            return u''
        else:
            out = []
            for part in seq:
                if isinstance(part, cssutils.css.csscomment.CSSComment):
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
            if not (out[-1].endswith(';') or out[-1].endswith('}')):
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
        styleText = self.do_css_CSSStyleDeclaration(rule.style)
        if not styleText:
            styleText = u''
        
        return u'%s {%s}' % (selectorText, styleText)


    def do_css_SelectorList(self, selectorlist):
        """
        comma-separated list of Selectors
        """
        if len(selectorlist.seq) == 0 or self._noinvalids(selectorlist):
            return u''
        else:
            out = []
            for part in selectorlist.seq:
                if isinstance(part, cssutils.css.csscomment.CSSComment):
                    out.append(part.cssText)
                elif u',' == part:
                    out.append(u', ')
                elif isinstance(part, cssutils.css.cssstylerule.Selector):
                    out.append(self.do_css_Selector(part).strip())
                else:
                    out.append(part) # ?
            return u''.join(out)


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
                if isinstance(part, cssutils.css.csscomment.CSSComment):
                    out.append(part.cssText)
                else:
                    if type(part) == dict:
                        out.append(part['value'])
                    else:
                        out.append(part)
            return u''.join(out)


    def do_css_CSSStyleDeclaration(self, style):
        """
        Style declaration of CSSStyleRule
        """
        if len(style.seq) == 0 or self._noinvalids(style):
            return u''
        else:
            out = ['\n']
            done1 = False # if no content empty done1
            lastwasprop = False            
            for part in style.seq:
                # CSSComment
                if isinstance(part,
                  cssutils.css.csscomment.CSSComment):
                    if self.prefs.keepComments:
                        done1 = True
                        if lastwasprop:
                            out.append(u';\n')
                        out.append(self.prefs.indent)
                        out.append(part.cssText)
                        out.append(u'\n')
                        lastwasprop = False
                        
                # PropertySimilarNameList
                elif isinstance(part,
                  cssutils.css.cssstyledeclaration.SameNamePropertyList):
                    # only last valid Property
                    if not self.prefs.keepAllProperties:
                        _index = part._currentIndex()
                        propertytext = self.do_css_Property(part[_index])
                    else:
                        # or all Properties
                        o = []
                        for p in part:
                            pt = self.do_css_Property(p)
                            if pt:
                                o.append(pt)
                                o.append(u';\n')
                                o.append(self.prefs.indent)
                        propertytext = u''.join(o[:-2]) # omit last \n and indent
                        
                    if propertytext:
                        done1 = True
                        if lastwasprop:
                            out.append(u';\n')
                        out.append(self.prefs.indent)
                        out.append(propertytext)
                        lastwasprop = True

                # other?
                else:
                    done1 = True
                    if lastwasprop:
                        out.append(u';\n')
                    out.append(part)
                    lastwasprop = False
            if not done1:
                return u''
            if lastwasprop:
                out.append(u'\n')
            out.append(self.prefs.indent)
            return u''.join(out)


    def do_css_Property(self, property):
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

            for part in nameseq:
                if isinstance(part, cssutils.css.csscomment.CSSComment):
                    out.append(part.cssText)
                elif property.name == part:
                    out.append(self._getpropertyname(property, part))
                else:
                    out.append(part)
            if out:
                out.append(u': ')
            v = self.do_css_CSSvalue(cssvalue)
            if v:
                out.append(v)

            if out and priorityseq:
                out.append(u' ')
            for part in priorityseq:
                if hasattr(part, 'cssText'): # comments
                    out.append(part.cssText)
                else:
                    out.append(part)
            
            return u''.join(out)


    def do_css_CSSvalue(self, cssvalue):
        """
        serializes a CSSValue
        """
        if not cssvalue:
            return u''
        else:
            out = []
            for part in cssvalue.seq:
                if hasattr(part, 'cssText'): # comments
                    out.append(part.cssText)
                else:
                    out.append(part)
            return (u''.join(out)).strip()
