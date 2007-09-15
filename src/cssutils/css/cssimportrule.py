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
        # import : IMPORT_SYM S* [STRING|URI]
        #            S* [ medium [ ',' S* medium]* ]? ';' S*  ;
        super(CSSImportRule, self)._setCssText(cssText)
        valid = True

        tokens = self._tokenize2(cssText, aslist=True)

        # check if right type
        if not tokens or\
           tokens and self._type(tokens[0]) != self._prods.IMPORT_SYM:
            valid = False
            self._log.error(u'CSSImportRule: No CSSImportRule found: %s' %
                self._valuestr(cssText),
                error=xml.dom.InvalidModificationErr)
        else:
            newatkeyword = self._value(tokens[0])

            newseq = []
            newhref = None
            newhreftype = None
            newmedia = cssutils.stylesheets.MediaList()

            mediatokens = []
            expected = 'href' # href medialist EOF
            for i in range(1, len(tokens)):
                t = tokens[i]
                typ, val = self._type(t), self._value(t)

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
