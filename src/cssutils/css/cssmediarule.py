"""CSSMediaRule implements DOM Level 2 CSS CSSMediaRule.
"""
__all__ = ['CSSMediaRule']
__docformat__ = 'restructuredtext'
__version__ = '0.9.1a4'

import xml.dom

import cssrule
import cssutils

class CSSMediaRule(cssrule.CSSRule):
    """
    represents an @media rule in a CSS style sheet. A @media rule can be
    used to delimit style rules for specific media types.  

    Properties
    ==========
    cssRules: A css::CSSRuleList of all CSS rules contained within the
        media block.
    cssText: of type DOMString
        The parsable textual representation of this rule
    media: of type stylesheets::MediaList, (DOM readonly)
        A list of media types for this rule of type MediaList.

    cssutils only
    -------------
    atkeyword: 
        the literal keyword used

    Inherits properties from CSSRule

    Format
    ======
    media
      : MEDIA_SYM S* medium [ COMMA S* medium ]* LBRACE S* ruleset* '}' S*;
    """
    # CONSTANT
    type = cssrule.CSSRule.MEDIA_RULE 

    def __init__(self, readonly=False):
        """
        constructor
        """
        super(CSSMediaRule, self).__init__()
        
        self.atkeyword = u'@media'
        self._media = cssutils.stylesheets.MediaList()
        self._rules = cssutils.css.cssrulelist.CSSRuleList()

        self._readonly = readonly


    def _getMedia(self):
        "returns MediaList"
        return self._media
    
    media = property(_getMedia,
        doc=u"(DOM readonly) A list of media types for this rule of type\
            MediaList")

    
    def _getCssRules(self):
        return self._rules

    cssRules = property(_getCssRules,
        doc="(DOM readonly) A css::CSSRuleList of all CSS rules contained\
            within the media block.")


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
            self._rules[index].parentRule = None # detach
            del self._rules[index] # remove from @media
        except IndexError:
            raise xml.dom.IndexSizeErr(
                u'CSSMediaRule: %s is not a valid index in the rulelist of length %i' % (
                index, self.cssRules.length))


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
            tempsheet = CSSStyleSheet()
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
        # @charset @import @media -> TODO: @page @namespace
        if isinstance(rule, cssutils.css.CSSCharsetRule) or \
           isinstance(rule, cssutils.css.CSSImportRule) or \
           isinstance(rule, CSSMediaRule):
            self._log.error(u'CSSMediaRule: This type of rule is not allowed here: %s' %
                      rule.cssText,
                      error=xml.dom.HierarchyRequestErr)
            return
            
        self.cssRules.insert(index, rule)
        rule.parentRule = self
        return index


    def _getCssText(self):
        """
        returns serialized property cssText 
        """
        return cssutils.ser.do_CSSMediaRule(self)

    def _setCssText(self, cssText):
        """
        DOMException on setting
         
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if the rule is readonly.
        - INVALID_MODIFICATION_ERR: (self)
          Raised if the specified CSS string value represents a different
          type of rule than the current one.
        - HIERARCHY_REQUEST_ERR: (self)
          Raised if the rule cannot be inserted at this point in the
          style sheet.
        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        """
        super(CSSMediaRule, self)._setCssText(cssText)          
        tokens = self._tokenize(cssText)        
        valid = True

        # check if right token    
        if not tokens or tokens and tokens[0].type != self._ttypes.MEDIA_SYM:
            self._log.error(u'CSSMediaRule: No CSSMediaRule found: %s' %
                      self._valuestr(cssText),
                      error=xml.dom.InvalidModificationErr)
            return
        else:
            newatkeyword = tokens[0].value
            
        newmedia = cssutils.stylesheets.MediaList()
        mediatokens, endi = self._tokenizer.tokensupto(tokens[1:],
                                                    blockstartonly=True)

        # checks if media ends with rules start and if at least
        # one media found, medialist default to all which is wrong here!
        if mediatokens and mediatokens[-1].value == u'{' and \
           self._ttypes.IDENT in [_t.type for _t in mediatokens]:
            newmedia.mediaText = mediatokens[:-1]
        else:
            self._log.error(xml.dom.SyntaxErr(
                u'CSSMediaRule: Syntax error in MediaList: %s' %
                self._valuestr(cssText)))
            return

        newrules = cssutils.css.CSSRuleList()
        i = endi + 2 # ???
        while i < len(tokens):
            t = tokens[i]
            
            if self._ttypes.S == t.type: # ignore
                pass

            elif self._ttypes.COMMENT == t.type: # just add
                newrules.append(cssutils.css.CSSComment(t))

            elif u'}' == t.value: # end
                if i+1 < len(tokens):
                    self._log.error(
                        u'CSSMediaRule: Unexpected tokens found: "%s".'
                        % self._valuestr(tokens[i:]), t)
                break

            elif self._ttypes.ATKEYWORD == t.type:
                # @UNKNOWN
                self._log.info(u'CSSMediaRule: Found unknown @rule.', t,
                         error=None)
                atruletokens, endi = self._tokenizer.tokensupto(tokens[i:])
                i += endi 
                atrule = cssutils.css.CSSUnknownRule()
                atrule.cssText = atruletokens
                newrules.append(atrule)

            elif t.type in (self._ttypes.CHARSET_SYM, self._ttypes.IMPORT_SYM,
                            self._ttypes.MEDIA_SYM, self._ttypes.PAGE_SYM):
                atruletokens, endi = self._tokenizer.tokensupto(tokens[i:])
                i += endi + 1
                self._log.error(
                    u'CSSMediaRule: This rule is not allowed in CSSMediaRule - ignored: %s.'
                    % self._valuestr(atruletokens), t,
                    xml.dom.HierarchyRequestErr)
                continue

            else:
                # StyleRule
                ruletokens, endi = self._tokenizer.tokensupto(
                    tokens[i:], blockendonly=True)
                i += endi 
                rule = cssutils.css.CSSStyleRule()
                rule.cssText = ruletokens
                newrules.append(rule)

            i += 1

        if valid:
            self.atkeyword = newatkeyword
            self._media = newmedia
            self._rules = newrules
            for r in self._rules:
                r.parentRule = self

    cssText = property(_getCssText, _setCssText,
        doc="(DOM attribute) The parsable textual representation.")


if __name__ == '__main__':
    m = CSSMediaRule()
    m.cssText = u'@media all {@;}'
    print m.cssText