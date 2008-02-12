"""CSSImportRule implements DOM Level 2 CSS CSSImportRule.

plus: 
    name
        http://www.w3.org/TR/css3-cascade/#cascading

TODO:
    - stylesheet: read and parse linked stylesheet
"""
__all__ = ['CSSImportRule']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssrule
import cssutils

class CSSImportRule(cssrule.CSSRule, cssutils.util.Base2):
    """
    Represents an @import rule within a CSS style sheet.  The @import rule
    is used to import style rules from other style sheets.

    Properties
    ==========
    atkeyword: (cssutils only)
        the literal keyword used
    cssText: of type DOMString
        The parsable textual representation of this rule
    href: of type DOMString, (DOM readonly, cssutils also writable)
        The location of the style sheet to be imported. The attribute will
        not contain the url(...) specifier around the URI.
    hreftype: 'uri' (serializer default) or 'string' (cssutils only)
        The original usage of href, not really relevant as it may be
        configured in the serializer too
    media: of type stylesheets::MediaList (DOM readonly)
        A list of media types for this rule of type MediaList.
    name: 
        An optional name used for cascading
    stylesheet: of type CSSStyleSheet (DOM readonly)
        The style sheet referred to by this rule. The value of this
        attribute is None if the style sheet has not yet been loaded or if
        it will not be loaded (e.g. if the stylesheet is for a media type
        not supported by the user agent).

        Currently always None

    Inherits properties from CSSRule

    Format
    ======
    import
      : IMPORT_SYM S*
      [STRING|URI] S* [ medium [ COMMA S* medium]* ]? S* STRING? S* ';' S*
      ;
    """
    type = cssrule.CSSRule.IMPORT_RULE

    def __init__(self, href=None, mediaText=u'all', name=None, hreftype=None, 
                 parentRule=None, parentStyleSheet=None, readonly=False):
        """
        if readonly allows setting of properties in constructor only

        Do not use as positional but as keyword attributes only!

        href
            location of the style sheet to be imported.
        mediaText
            A list of media types for which this style sheet may be used
            as a string
        hreftype
            'uri' (default) or 'string'
        """
        super(CSSImportRule, self).__init__(parentRule=parentRule, 
                                            parentStyleSheet=parentStyleSheet,
                                            _Base2=True)

        self.atkeyword = u'@import'
        self._href = None
        self.href = href
        self.hreftype = hreftype
        self._media = cssutils.stylesheets.MediaList(
            mediaText, readonly=readonly)
        self._name = name
        if not self.media.valid:
            self._media = cssutils.stylesheets.MediaList()
            
        seq = self._tempSeq()
        seq.append(self.href, 'href')
        seq.append(self.media, 'media')
        seq.append(self.name, 'name')
        self._seq = seq

        # TODO: load stylesheet from href automatically?
        self._styleSheet = None

        self._readonly = readonly

    def _getCssText(self):
        """
        returns serialized property cssText
        """
        return cssutils.ser.do_CSSImportRule(self)

    def _setCssText(self, cssText):
        """
        DOMException on setting

        - HIERARCHY_REQUEST_ERR: (CSSStylesheet)
          Raised if the rule cannot be inserted at this point in the
          style sheet.
        - INVALID_MODIFICATION_ERR: (self)
          Raised if the specified CSS string value represents a different
          type of rule than the current one.
        - NO_MODIFICATION_ALLOWED_ERR: (CSSRule)
          Raised if the rule is readonly.
        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        """
        super(CSSImportRule, self)._setCssText(cssText)
        tokenizer = self._tokenize2(cssText)
        attoken = self._nexttoken(tokenizer, None)
        if not attoken or self._type(attoken) != self._prods.IMPORT_SYM:
            self._log.error(u'CSSImportRule: No CSSImportRule found: %s' %
                self._valuestr(cssText),
                error=xml.dom.InvalidModificationErr)
        else:
            # for closures: must be a mutable
            new = {'keyword': self._tokenvalue(attoken),
                   'href': None,
                   'hreftype': None,
                   'media': cssutils.stylesheets.MediaList(),
                   'name': None,
                   'wellformed': True
                   }

            def __doname(seq, token):
                # called by _string or _ident
                new['name'] = self._stringtokenvalue(token)
                seq.append(new['name'], 'name')
                return ';'

            def _string(expected, seq, token, tokenizer=None):
                if 'href' == expected:
                    # href
                    new['href'] = self._stringtokenvalue(token)
                    new['hreftype'] = 'string'
                    seq.append(new['href'], 'href')
                    return 'media name ;'
                elif 'name' in expected:
                    # name
                    return __doname(seq, token)
                else:
                    new['wellformed'] = False
                    self._log.error(
                        u'CSSImportRule: Unexpected string.', token)
                    return expected

            def _uri(expected, seq, token, tokenizer=None):
                # href
                if 'href' == expected:
                    uri = self._uritokenvalue(token)
                    new['hreftype'] = 'uri'
                    new['href'] = uri
                    seq.append(new['href'], 'href')
                    return 'media name ;'
                else:
                    new['wellformed'] = False
                    self._log.error(
                        u'CSSImportRule: Unexpected URI.', token)
                    return expected

            def _ident(expected, seq, token, tokenizer=None):
                # medialist ending with ; which is checked upon too
                if expected.startswith('media'):
                    mediatokens = self._tokensupto2(
                        tokenizer, mediaqueryendonly=True, keepEnd=True)
                    mediatokens.insert(0, token) # push found token

                    last = mediatokens.pop() # retrieve ;
                    lastval, lasttyp = self._tokenvalue(last), self._type(last)
                    if lastval != u';' and lasttyp not in ('EOF', 'STRING'):
                        new['wellformed'] = False
                        self._log.error(u'CSSImportRule: No ";" found: %s' %
                                        self._valuestr(cssText), token=token)

                    media = cssutils.stylesheets.MediaList()
                    media.mediaText = mediatokens
                    if media.valid:
                        new['media'] = media
                        seq.append(media, 'media')
                    else:
                        new['wellformed'] = False
                        self._log.error(u'CSSImportRule: Invalid MediaList: %s' %
                                        self._valuestr(cssText), token=token)
                        
                    if lasttyp == 'STRING':
                        # name
                        return __doname(seq, last)
                    else:
                        return 'EOF' # ';' is token "last"
                else:
                    new['wellformed'] = False
                    self._log.error(
                        u'CSSImportRule: Unexpected ident.', token)
                    return expected

            def _char(expected, seq, token, tokenizer=None):
                # final ;
                val = self._tokenvalue(token)
                if expected.endswith(';') and u';' == val:
                    return 'EOF'
                else:
                    new['wellformed'] = False
                    self._log.error(
                        u'CSSImportRule: Unexpected char.', token)
                    return expected

            # import : IMPORT_SYM S* [STRING|URI]
            #            S* [ medium [ ',' S* medium]* ]? ';' S* 
            #         STRING? # see http://www.w3.org/TR/css3-cascade/#cascading
            #        ;
            newseq = self._tempSeq()
            wellformed, expected = self._parse(expected='href',
                seq=newseq, tokenizer=tokenizer,
                productions={'STRING': _string,
                             'URI': _uri,
                             #'FUNCTION': _function,
                             'IDENT': _ident,
                             'CHAR': _char})

            # wellformed set by parse
            wellformed = wellformed and new['wellformed']

            # post conditions
            if not new['href']:
                wellformed = False
                self._log.error(u'CSSImportRule: No href found: %s' %
                    self._valuestr(cssText))

            if expected != 'EOF':
                wellformed = False
                self._log.error(u'CSSImportRule: No ";" found: %s' %
                    self._valuestr(cssText))

            # set all
            if wellformed:
                self.atkeyword = new['keyword']
                self.href = new['href']
                self.hreftype = new['hreftype']
                self._media = new['media']
                self.name = new['name']
                self.seq = newseq

    cssText = property(fget=_getCssText, fset=_setCssText,
        doc="(DOM attribute) The parsable textual representation.")

    def _setHref(self, href):
        # update seq
        for i, item in enumerate(self.seq):
            val, typ = item.value, item.type
            if 'href' == typ:
                self._seq[i] = (href, typ, item.line, item.col)
                break
        else:
            seq = self._tempSeq()
            seq.append(self.href, 'href')
            self._seq = seq
        # set new href
        self._href = href

    href = property(lambda self: self._href, _setHref,
                    doc="Location of the style sheet to be imported.")

    media = property(lambda self: self._media,
                     doc=u"(DOM readonly) A list of media types for this rule"
                     " of type MediaList")

    def _setName(self, name):
        # update seq
        for i, item in enumerate(self.seq):
            val, typ = item.value, item.type
            if 'name' == typ:
                self._seq[i] = (name, typ, item.line, item.col)
                break
        else:
            # append
            seq = self._tempSeq()
            for item in self.seq:
                # copy current seq
                seq.append(item.value, item.type, item.line, item.col)
            seq.append(self.href, 'href')
            self._seq = seq
        self._name = name

    name = property(lambda self: self._name, _setName,
                    doc=u"An optional name for the imported sheet")

    styleSheet = property(lambda self: self._styleSheet,
                          doc="(readonly) The style sheet referred to by this rule.")

    valid = property(lambda self: bool(self.href and self.media.valid))

    def __repr__(self):
        return "cssutils.css.%s(href=%r, mediaText=%r, name=%r)" % (
                self.__class__.__name__, 
                self.href, self.media.mediaText, self.name)

    def __str__(self):
        return "<cssutils.css.%s object href=%r at 0x%x>" % (
                self.__class__.__name__, self.href, id(self))
