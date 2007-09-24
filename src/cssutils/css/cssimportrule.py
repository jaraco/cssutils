"""CSSImportRule implements DOM Level 2 CSS CSSImportRule.

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

class CSSImportRule(cssrule.CSSRule):
    """
    Represents an @import rule within a CSS style sheet.  The @import rule
    is used to import style rules from other style sheets.

    Properties
    ==========
    cssText: of type DOMString
        The parsable textual representation of this rule
    href: of type DOMString, (DOM readonly, cssutils also writable)
        The location of the style sheet to be imported. The attribute will
        not contain the url(...) specifier around the URI.
    media: of type stylesheets::MediaList (DOM readonly)
        A list of media types for this rule of type MediaList.
    stylesheet: of type CSSStyleSheet (DOM readonly)
        The style sheet referred to by this rule. The value of this
        attribute is None if the style sheet has not yet been loaded or if
        it will not be loaded (e.g. if the stylesheet is for a media type
        not supported by the user agent).

        Currently always None

    cssutils only
    -------------
    atkeyword:
        the literal keyword used
    hreftype: 'uri' (serializer default) or 'string'
        The original usage of href, not really relevant as it may be
        configured in the serializer too

    Inherits properties from CSSRule

    Format
    ======
    import
      : IMPORT_SYM S*
      [STRING|URI] S* [ medium [ COMMA S* medium]* ]? ';' S*
      ;
    """
    type = cssrule.CSSRule.IMPORT_RULE

    def __init__(self, href=None, mediaText=u'all', hreftype=None,
                 readonly=False):
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
        super(CSSImportRule, self).__init__()

        self.atkeyword = u'@import'
        self.href = href
        self.hreftype = hreftype
        self._media = cssutils.stylesheets.MediaList(
            mediaText, readonly=readonly)
        if not self.media.valid:
            self._media = cssutils.stylesheets.MediaList()
        self.seq = [self.href, self.media]

        # TODO: load stylesheet from href automatically?
        self._styleSheet = None

        self._readonly = readonly


    def _getHref(self):
        """ returns href as a string """
        return self._href

    def _setHref(self, href):
        """
        TODO:
            parse properly

        DOMException on setting

        - SYNTAX_ERR: (not checked here)
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (CSSRule)
          Raised if this rule is readonly.
        """
        self._checkReadonly()

        # update seq
        for i, x in enumerate(self.seq):
            if x == self._href:
                self.seq[i] = href
                break
        else:
            self.seq = [href]
        # set new href
        self._href = href

    href = property(_getHref, _setHref,
        doc="Location of the style sheet to be imported.")

    def _getMedia(self):
        "returns MediaList"
        return self._media

    media = property(_getMedia,
        doc=u"(DOM readonly) A list of media types for this rule of type\
            MediaList")

    def _getStyleSheet(self):
        """
        returns a CSSStyleSheet or None
        """
        return self._styleSheet

    styleSheet = property(_getStyleSheet,
        doc="(readonly) The style sheet referred to by this rule.")

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
        valid = True
        tokenizer = self._tokenize2(cssText)

        attoken = self._nexttoken(tokenizer, None)

        if not attoken or self._type(attoken) != self._prods.IMPORT_SYM:
            valid = False
            self._log.error(u'CSSImportRule: No CSSImportRule found: %s' %
                self._valuestr(cssText),
                error=xml.dom.InvalidModificationErr)

        else:
            # import : IMPORT_SYM S* [STRING|URI]
            #            S* [ medium [ ',' S* medium]* ]? ';' S*  ;
            newseq = []
            # for closures: must be a mutable
            new = {
                   'keyword': self._tokenvalue(attoken),
                   'href': None,
                   'hreftype': None,
                   'media': cssutils.stylesheets.MediaList(),
                   'valid': True
                   }

            def _string(expected, seq, token, tokenizer=None):
                # href
                if 'href' == expected:
                    new['hreftype'] = 'string'
                    new['href'] = self._tokenvalue(token)[1:-1] # "uri" or 'uri'
                    seq.append(new['href'])
                    return 'media or ;'
                else:
                    new['valid'] = False
                    self._log.error(
                        u'CSSImportRule: Unexpected string.', token)
                    return expected

            def _uri(expected, seq, token, tokenizer=None):
                # href
                if 'href' == expected:
                    new['hreftype'] = 'uri'
                    uri = self._tokenvalue(token)[4:-1].strip() # url(uri)
                    if uri[0] == uri[-1] == '"' or\
                       uri[0] == uri[-1] == "'":
                        uri = uri[1:-1]
                    new['href'] = uri
                    seq.append(new['href'])
                    return 'media or ;'
                else:
                    new['valid'] = False
                    self._log.error(
                        u'CSSImportRule: Unexpected URI.', token)
                    return expected

            # TODO!!!
            def _function(expected, seq, token, tokenizer=None):
                # href: incomplete URI!!!
                eof = self._type(tokenizer.next()) # should end here
                val = self._tokenvalue(token, normalize=True)
                if eof == 'EOF' and 'href' == expected and val.startswith(u'url('):
                    new['hreftype'] = 'uri'
                    uri = self._tokenvalue(token)[4:].strip() # url(uri INCOMPLETE!
                    if uri and (
                       uri[0] == uri[-1] == '"' or
                       uri[0] == uri[-1] == "'"):
                        uri = uri[1:-1]
                    new['href'] = uri
                    seq.append(new['href'])
                    return 'EOF'
                else:
                    new['valid'] = False
                    self._log.error(
                        u'CSSImportRule: Unexpected FUNCTION.', token)
                    return expected


            def _ident(expected, seq, token, tokenizer=None):
                # medialist ending with ; which is checked upon too
                if expected.startswith('media'):
                    mediatokens = self._tokensupto2(
                        tokenizer, semicolon=True, keepEnd=True)
                    mediatokens.insert(0, token) # push found token

                    semicolonOrEOF = mediatokens.pop() # retrieve ;
                    if self._tokenvalue(semicolonOrEOF) != u';' and\
                       self._type(semicolonOrEOF) != 'EOF':
                        new['valid'] = False
                        self._log.error(u'CSSImportRule: No ";" found: %s' %
                                        self._valuestr(cssText), token=token)

                    media = cssutils.stylesheets.MediaList()
                    media.mediaText = mediatokens
                    if media.valid:
                        new['media'] = media
                        seq.append(media)
                    else:
                        new['valid'] = False
                        self._log.error(u'CSSImportRule: Invalid MediaList: %s' %
                                        self._valuestr(cssText), token=token)
                    return 'EOF' # ';' is found already
                else:
                    new['valid'] = False
                    self._log.error(
                        u'CSSImportRule: Unexpected ident.', token)
                    return expected

            def _char(expected, seq, token, tokenizer=None):
                # final ;
                val = self._tokenvalue(token)
                if expected.endswith(';') and u';' == val:
                    return 'EOF'
                else:
                    new['valid'] = False
                    self._log.error(
                        u'CSSImportRule: Unexpected char.', token)
                    return expected

            # main loop
            valid, expected = self._parse(expected='href',
                seq=newseq, tokenizer=tokenizer,
                productions={'STRING': _string,
                             'URI': _uri,
                             'FUNCTION': _function,
                             'IDENT': _ident,
                             'CHAR': _char})

            # valid set by parse
            valid = valid and new['valid']

            # post conditions
            if not new['href']:
                valid = False
                self._log.error(u'CSSImportRule: No href found: %s' %
                    self._valuestr(cssText))

            if expected != 'EOF':
                valid = False
                self._log.error(u'CSSImportRule: No ";" found: %s' %
                    self._valuestr(cssText))

            # set all
            if valid:
                self.valid = True
                self.atkeyword = new['keyword']
                self.href = new['href']
                self.hreftype = new['hreftype']
                self._media = new['media']
                self.seq = newseq



            return








            newatkeyword = self._tokenvalue(tokenizer[0])

            newseq = []
            newhref = None
            newhreftype = None
            newmedia = cssutils.stylesheets.MediaList()

            mediatokens = []
            expected = 'href' # href medialist EOF
            for i in range(1, len(tokens)):
                t = tokens[i]
                typ, val = self._type(t), self._tokenvalue(t)

                if self._prods.EOF == typ:
                    expected = 'EOF'

                elif self._prods.S == typ: # ignore
                    pass

                elif self._prods.COMMENT == typ:
                    if 'href' == expected: # before href
                        newseq.append(cssutils.css.CSSComment(t))
                    else: # after href
                        mediatokens.append(t)

                elif 'href' == expected and \
                     typ in (self._prods.URI, self._prods.STRING):
                    if typ == self._prods.URI:
                        newhref = val[4:-1].strip() # url(href)
                        newhreftype = 'uri'
                    else:
                        newhref = val[1:-1].strip() # "href" or 'href'
                        newhreftype = 'string'
                    newseq.append(newhref)
                    expected = 'medialist'

                elif u';' == val:
                    if 'medialist' != expected: # normal end
                        valid = False
                        self._log.error(
                            u'CSSImportRule: Syntax Error, no href found.', t)
                    expected = None
                    break

                elif 'medialist' == expected:
                    mediatokens.append(t)

                else:
                    valid = False
                    self._log.error(u'CSSImportRule: Syntax Error.', t)

            if expected and expected != 'EOF':
                valid = False
                self._log.error(u'CSSImportRule: Syntax Error, no ";" found: %s' %
                          self._valuestr(cssText))

            if mediatokens:
                newmedia.mediaText = mediatokens
                if not newmedia.valid:
                    valid = False
                newseq.append(newmedia)

        self.valid = valid
        if valid:
            self.atkeyword = newatkeyword
            self.href = newhref
            self.hreftype = newhreftype
            self._media = newmedia
            self.seq = newseq

    cssText = property(fget=_getCssText, fset=_setCssText,
        doc="(DOM attribute) The parsable textual representation.")

    def __repr__(self):
        return "cssutils.css.%s(href=%r, mediaText=%r)" % (
                self.__class__.__name__, self.href, self.media.mediaText)

    def __str__(self):
        return "<cssutils.css.%s object href=%r at 0x%x>" % (
                self.__class__.__name__, self.href, id(self))

if __name__ == '__main__':
    c = CSSImportRule(href='"1.css"', mediaText='handheld, all, tv')
    print c.seq#, c.media.seq
    print c.cssText
    c.cssText = '@import'
