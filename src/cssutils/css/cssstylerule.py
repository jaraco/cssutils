"""CSSStyleRule implements DOM Level 2 CSS CSSStyleRule.
"""
__all__ = ['CSSStyleRule']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssrule
import cssutils
from selectorlist import SelectorList
from cssstyledeclaration import CSSStyleDeclaration

class CSSStyleRule(cssrule.CSSRule):
    """
    The CSSStyleRule object represents a ruleset specified (if any) in a CSS
    style sheet. It provides access to a declaration block as well as to the
    associated group of selectors.
    
    Properties
    ==========
    selectorText: of type DOMString
        The textual representation of the selector for the rule set. The
        implementation may have stripped out insignificant whitespace while
        parsing the selector.
    style: of type CSSStyleDeclaration, (DOM)
        The declaration-block of this rule set.
        
    inherited properties:
        - cssText
        - parentRule
        - parentStyleSheet
        - type: STYLE_RULE

    cssutils only
    -------------
    selectorList: of type SelectorList (cssutils only)
        A list of all Selector elements for the rule set.
    
    Format
    ======
    ruleset::
    
        : selector [ COMMA S* selector ]*
        LBRACE S* declaration [ ';' S* declaration ]* '}' S*
        ;
    """
    type = cssrule.CSSRule.STYLE_RULE

    def __init__(self, selectorText=None, style=None, readonly=False):
        """
        if readonly allows setting of properties in constructor only

        selectorText
            type string
        style
            CSSStyleDeclaration for this CSSStyleRule
        """
        super(CSSStyleRule, self).__init__()

        if selectorText:
            self.selectorText = selectorText
            self.seq.append(self.selectorText)
        else:
            self._selectorList = SelectorList(parentRule=self)
        if style:
            self.style = style
            self.seq.append(self.style)
        else:
            self._style = CSSStyleDeclaration(parentRule=self)

        self._readonly = readonly

    def _getCssText(self):
        """
        returns serialized property cssText
        """
        return cssutils.ser.do_CSSStyleRule(self)

    def _setCssText(self, cssText):
        """
        DOMException on setting

        - SYNTAX_ERR: (self, StyleDeclaration, etc)
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        - INVALID_MODIFICATION_ERR: (self)
          Raised if the specified CSS string value represents a different
          type of rule than the current one.
        - HIERARCHY_REQUEST_ERR: (CSSStylesheet)
          Raised if the rule cannot be inserted at this point in the
          style sheet.
        - NO_MODIFICATION_ALLOWED_ERR: (CSSRule)
          Raised if the rule is readonly.
        """
        super(CSSStyleRule, self)._setCssText(cssText)
        
        tokenizer = self._tokenize2(cssText)
        selectortokens = self._tokensupto2(tokenizer, blockstartonly=True)
        styletokens = self._tokensupto2(tokenizer, blockendonly=True)

        trail = self._nexttoken(tokenizer)
        if trail:
            self._log.error(u'CSSStyleRule: Trailing content: %s',
                            token=trail,
                            error=xml.dom.SyntaxErr)
        
        if not selectortokens or self._tokenvalue(
                                        selectortokens[0]).startswith(u'@'):
            self._log.error(u'CSSStyleRule: No content or no style rule.',
                    error=xml.dom.InvalidModificationErr)

        else:
            valid = True
            
            bracetoken = selectortokens.pop()
            if self._tokenvalue(bracetoken) != u'{':
                valid = False
                self._log.error(
                    u'CSSStyleRule: No start { of style declaration found: %r' %
                    self._valuestr(cssText), bracetoken)
            elif not selectortokens:
                valid = False
                self._log.error(u'CSSStyleRule: No selector found: %r.' %
                            self._valuestr(cssText), bracetoken)
                
            newselectorlist = SelectorList(selectorText=selectortokens,
                                           parentRule=self)

            newstyle = CSSStyleDeclaration()
            if not styletokens:
                valid = False
                self._log.error(
                    u'CSSStyleRule: No style declaration or "}" found: %r' %
                    self._valuestr(cssText))
            else:
                braceorEOFtoken = styletokens.pop()
                val, typ = self._tokenvalue(braceorEOFtoken), self._type(braceorEOFtoken)
                if val != u'}' and typ != 'EOF':
                    valid = False
                    self._log.error(
                        u'CSSStyleRule: No "}" after style declaration found: %r' %
                        self._valuestr(cssText))
                else:
                    if 'EOF' == typ:
                        # add again as style needs it
                        styletokens.append(braceorEOFtoken)
                    newstyle.cssText = styletokens

            if valid:
                self.valid = True
                self.selectorList = newselectorlist
                self.style = newstyle

    cssText = property(_getCssText, _setCssText,
        doc="(DOM) The parsable textual representation of the rule.")

    def _setSelectorList(self, selectorList):
        """
        (cssutils)
        set the SelectorList of this rule

        selectorList
            instance of SelectorList

        DOMException on setting

        - NO_MODIFICATION_ALLOWED_ERR:
          Raised if this rule is readonly.
        """
        self._checkReadonly()
        self._selectorList = selectorList
        self._selectorList.parentRule = self

    def _getSelectorList(self):
        """
        (cssutils)
        returns the SelectorList of this rule
        see selectorText for a textual representation
        """
        return self._selectorList

    selectorList = property(_getSelectorList, _setSelectorList,
        doc="The SelectorList of this rule.")

    def _getSelectorText(self):
        """
        wrapper for cssutils SelectorList object
        """
        return self._selectorList.selectorText

    def _setSelectorText(self, selectorText):
        """
        wrapper for cssutils SelectorList object

        selector
            of type string, might also be a comma separated list of
            selectors

        DOMException on setting

        - SYNTAX_ERR: (SelectorList, Selector)
          Raised if the specified CSS string value has a syntax error
          and is unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this rule is readonly.
        """
        self._checkReadonly()
        self._selectorList = SelectorList(selectorText, parentRule=self)

    selectorText = property(_getSelectorText, _setSelectorText,
        doc="""(DOM) The textual representation of the selector for the
            rule set.""")

    def _getStyle(self):
        return self._style

    def _setStyle(self, style):
        """
        style
            StyleDeclaration or string
        """
        self._checkReadonly()
        if isinstance(style, basestring):
            self._style = CSSStyleDeclaration(parentRule=self, cssText=style)
        else:
            self._style = style
            style.parentRule = self

    style = property(_getStyle, _setStyle,
        doc="(DOM) The declaration-block of this rule set.")

    def __repr__(self):
        return "cssutils.css.%s(selectorText=%r, style=%r)" % (
                self.__class__.__name__, self.selectorText, self.style.cssText)

    def __str__(self):
        return "<cssutils.css.%s object selector=%r style=%r at 0x%x>" % (
                self.__class__.__name__, self.selectorText, self.style.cssText, 
                id(self))
