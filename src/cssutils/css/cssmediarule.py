"""CSSMediaRule implements DOM Level 2 CSS CSSMediaRule.
"""
__all__ = ['CSSMediaRule']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssrule
import cssutils

class CSSMediaRule(cssrule.CSSRule):
    """
    Objects implementing the CSSMediaRule interface can be identified by the
    MEDIA_RULE constant. On these objects the type attribute must return the
    value of that constant.

    Properties
    ==========
    cssRules: A css::CSSRuleList of all CSS rules contained within the
        media block.
    media: of type stylesheets::MediaList, (DOM readonly)
        A list of media types for this rule of type MediaList.
    inherited from CSSRule
        cssText

    cssutils only
    -------------
    atkeyword:
        the literal keyword used

    Format
    ======
    media
      : MEDIA_SYM S* medium [ COMMA S* medium ]* LBRACE S* ruleset* '}' S*;
    """
    # CONSTANT
    type = cssrule.CSSRule.MEDIA_RULE

    def __init__(self, mediaText='all', parentRule=None, 
                 parentStyleSheet=None, readonly=False):
        """
        constructor
        """
        super(CSSMediaRule, self).__init__(parentRule=parentRule, 
                                           parentStyleSheet=parentStyleSheet)
        self.atkeyword = u'@media'
        self._media = cssutils.stylesheets.MediaList(
            mediaText, readonly=readonly)
        if not self.media.valid:
            self._media = cssutils.stylesheets.MediaList()
            
        self.cssRules = cssutils.css.cssrulelist.CSSRuleList()
        self.cssRules.append = self.insertRule
        self.cssRules.extend = self.insertRule
        self.cssRules.__delitem__ == self.deleteRule

        self._readonly = readonly

    def __iter__(self):
        """
        generator which iterates over cssRules.
        """
        for rule in self.cssRules:
            yield rule
            
    def _getCssText(self):
        """
        returns serialized property cssText
        """
        return cssutils.ser.do_CSSMediaRule(self)

    def _setCssText(self, cssText):
        """
        :param cssText:
            a parseable string or a tuple of (cssText, dict-of-namespaces)
        :Exceptions:
            - `NAMESPACE_ERR`: (Selector)
              Raised if a specified selector uses an unknown namespace
              prefix.
            - `SYNTAX_ERR`: (self, StyleDeclaration, etc)
              Raised if the specified CSS string value has a syntax error and
              is unparsable.
            - `INVALID_MODIFICATION_ERR`: (self)
              Raised if the specified CSS string value represents a different
              type of rule than the current one.
            - `HIERARCHY_REQUEST_ERR`: (CSSStylesheet)
              Raised if the rule cannot be inserted at this point in the
              style sheet.
            - `NO_MODIFICATION_ALLOWED_ERR`: (CSSRule)
              Raised if the rule is readonly.
        """
        super(CSSMediaRule, self)._setCssText(cssText)
        
        # might be (cssText, namespaces)
        cssText, namespaces = self._splitNamespacesOff(cssText)
        try:
            # use parent style sheet ones if available
            namespaces = self.parentStyleSheet.namespaces
        except AttributeError:
            pass
        
        tokenizer = self._tokenize2(cssText)
        attoken = self._nexttoken(tokenizer, None)
        if not attoken or u'@media' != self._tokenvalue(
                                                    attoken, normalize=True):
            self._log.error(u'CSSMediaRule: No CSSMediaRule found: %s' %
                self._valuestr(cssText),
                error=xml.dom.InvalidModificationErr)
        else:
            # media
            valid = True
            mediatokens = self._tokensupto2(tokenizer, blockstartonly=True)        
            if len(mediatokens) < 1 or\
               u'{' != self._tokenvalue(mediatokens[-1]):
                self._log.error(u'CSSMediaRule: No "{" found.')
            else:
                newmedia = cssutils.stylesheets.MediaList()
                newmedia.mediaText = mediatokens[:-1] # omit {
            
            # cssRules
            cssrulestokens = self._tokensupto2(tokenizer, mediaendonly=True)
            newcssrules = [] #cssutils.css.CSSRuleList()
            if len(cssrulestokens) < 1 or (
               u'}' != self._tokenvalue(cssrulestokens[-1]) and
               'EOF' != self._type(cssrulestokens[-1])):
                self._log.error(u'CSSMediaRule: No "}" found.')
            elif self._nexttoken(tokenizer, None):
                self._log.error(u'CSSMediaRule: Content after "}" found.')
            else:
                brace = cssrulestokens.pop()
                
                # for closures: must be a mutable
                new = {'valid': True }
                
                def COMMENT(expected, seq, token, tokenizer=None):
                    "special: sets parent*"
                    comment = cssutils.css.CSSComment([token], parentRule=self, 
                                        parentStyleSheet=self.parentStyleSheet)
                    seq.append(comment)
                    return expected
                
                def ruleset(expected, seq, token, tokenizer):
                    rule = cssutils.css.CSSStyleRule(parentRule=self)
                    rule.cssText = (self._tokensupto2(tokenizer, token), 
                                    namespaces)
                    if rule.valid:
                        rule._parentStyleSheet=self.parentStyleSheet
                        seq.append(rule)
                    return expected
        
                def atrule(expected, seq, token, tokenizer):
                    # TODO: get complete rule!
                    tokens = self._tokensupto2(tokenizer, token)
                    atval = self._tokenvalue(token)
                    if atval in ('@charset ', '@font-face', '@import', '@namespace', 
                                 '@page', '@media'):
                        self._log.error(
                            u'CSSMediaRule: This rule is not allowed in CSSMediaRule - ignored: %s.'
                                % self._valuestr(tokens),
                                token = token, 
                                error=xml.dom.HierarchyRequestErr)
                    else:
                        rule = cssutils.css.CSSUnknownRule(parentRule=self, 
                                           parentStyleSheet=self.parentStyleSheet)
                        rule.cssText = tokens
                        if rule.valid:
                            seq.append(rule)
                    return expected
                
                tokenizer = (t for t in cssrulestokens) # TODO: not elegant!
                valid, expected = self._parse('}', newcssrules, tokenizer, {
                     'COMMENT': COMMENT,
                     'CHARSET_SYM': atrule,
                     'FONT_FACE_SYM': atrule,
                     'IMPORT_SYM': atrule,
                     'NAMESPACE_SYM': atrule,
                     'PAGE_SYM': atrule,
                     'MEDIA_SYM': atrule,
                     'ATKEYWORD': atrule
                     }, 
                     default=ruleset)
                
                # no post condition
                    
            if newmedia.valid and valid:
                self._media = newmedia
                del self.cssRules[:]# = newcssrules
                for r in newcssrules:
                    self.cssRules.append(r)
        
    cssText = property(_getCssText, _setCssText,
        doc="(DOM attribute) The parsable textual representation.")

    def _getMedia(self):
        "returns MediaList"
        return self._media

    media = property(_getMedia,
        doc=u"(DOM readonly) A list of media types for this rule of type\
            MediaList")

    def deleteRule(self, index):
        """
        index
            within the media block's rule collection of the rule to remove.

        Used to delete a rule from the media block.

        DOMExceptions

        - INDEX_SIZE_ERR: (self)
          Raised if the specified index does not correspond to a rule in
          the media rule list.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this media rule is readonly.
        """
        self._checkReadonly()

        try:
            self.cssRules[index]._parentRule = None # detach
            del self.cssRules[index] # remove from @media
        except IndexError:
            raise xml.dom.IndexSizeErr(
                u'CSSMediaRule: %s is not a valid index in the rulelist of length %i' % (
                index, self.cssRules.length))

    def add(self, rule):
        """
        Adds rule to end of this mediarule. Same as ``.insertRule(rule)``. 
        """
        self.insertRule(rule, index=None)
            
    def insertRule(self, rule, index=None):
        """
        rule
            The parsable text representing the rule. For rule sets this
            contains both the selector and the style declaration. For
            at-rules, this specifies both the at-identifier and the rule
            content.

            cssutils also allows rule to be a valid **CSSRule** object

        index
            within the media block's rule collection of the rule before
            which to insert the specified rule. If the specified index is
            equal to the length of the media blocks's rule collection, the
            rule will be added to the end of the media block.
            If index is not given or None rule will be appended to rule
            list.

        Used to insert a new rule into the media block.

        DOMException on setting

        - HIERARCHY_REQUEST_ERR:
          (no use case yet as no @charset or @import allowed))
          Raised if the rule cannot be inserted at the specified index,
          e.g., if an @import rule is inserted after a standard rule set
          or other at-rule.
        - INDEX_SIZE_ERR: (self)
          Raised if the specified index is not a valid insertion point.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this media rule is readonly.
        - SYNTAX_ERR: (CSSStyleRule)
          Raised if the specified rule has a syntax error and is
          unparsable.

        returns the index within the media block's rule collection of the
        newly inserted rule.

        """
        self._checkReadonly()

        # check position
        if index is None:
            index = len(self.cssRules)
        elif index < 0 or index > self.cssRules.length:
            raise xml.dom.IndexSizeErr(
                u'CSSMediaRule: Invalid index %s for CSSRuleList with a length of %s.' % (
                    index, self.cssRules.length))

        # parse
        if isinstance(rule, basestring):
            tempsheet = cssutils.css.CSSStyleSheet()
            tempsheet.cssText = rule
            if len(tempsheet.cssRules) != 1 or (tempsheet.cssRules and
             not isinstance(tempsheet.cssRules[0], cssutils.css.CSSRule)):
                self._log.error(u'CSSMediaRule: Invalid Rule: %s' % rule)
                return
            rule = tempsheet.cssRules[0]
        elif not isinstance(rule, cssutils.css.CSSRule):
            self._log.error(u'CSSMediaRule: Not a CSSRule: %s' % rule)
            return

        # CHECK HIERARCHY
        # @charset @import @page @namespace @media
        if isinstance(rule, cssutils.css.CSSCharsetRule) or \
           isinstance(rule, cssutils.css.CSSFontFaceRule) or \
           isinstance(rule, cssutils.css.CSSImportRule) or \
           isinstance(rule, cssutils.css.CSSNamespaceRule) or \
           isinstance(rule, cssutils.css.CSSPageRule) or \
           isinstance(rule, CSSMediaRule):
            self._log.error(u'CSSMediaRule: This type of rule is not allowed here: %s' %
                      rule.cssText,
                      error=xml.dom.HierarchyRequestErr)
            return

        self.cssRules.insert(index, rule)
        rule._parentRule = self
        rule._parentStyleSheet = self.parentStyleSheet
        return index

    def __repr__(self):
        return "cssutils.css.%s(mediaText=%r)" % (
                self.__class__.__name__, self.media.mediaText)
        
    def __str__(self):
        return "<cssutils.css.%s object mediaText=%r at 0x%x>" % (
                self.__class__.__name__, self.media.mediaText, id(self))
