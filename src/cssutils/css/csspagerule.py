"""CSSPageRule implements DOM Level 2 CSS CSSPageRule.
"""
__all__ = ['CSSPageRule']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssrule
import cssutils
from selectorlist import SelectorList
from cssstyledeclaration import CSSStyleDeclaration
#from selector import Selector

class CSSPageRule(cssrule.CSSRule):
    """
    The CSSPageRule interface represents a @page rule within a CSS style
    sheet. The @page rule is used to specify the dimensions, orientation,
    margins, etc. of a page box for paged media.

    Properties
    ==========
    cssText: of type DOMString
        The parsable textual representation of this rule
    selectorText: of type DOMString
        The parsable textual representation of the page selector for the rule.
    style: of type CSSStyleDeclaration
        The declaration-block of this rule.

    cssutils only
    -------------
    atkeyword:
        the literal keyword used

    Inherits properties from CSSRule

    Format
    ======
    ::

        page
          : PAGE_SYM S* pseudo_page? S*
            LBRACE S* declaration [ ';' S* declaration ]* '}' S*
          ;
        pseudo_page
          : ':' IDENT # :first, :left, :right in CSS 2.1
          ;

    """
    type = cssrule.CSSRule.PAGE_RULE

    def __init__(self, selectorText=None, style=None, parentRule=None, 
                 parentStyleSheet=None, readonly=False):
        """
        if readonly allows setting of properties in constructor only

        selectorText
            type string
        style
            CSSStyleDeclaration for this CSSStyleRule
        """
        super(CSSPageRule, self).__init__(parentRule=parentRule, 
                                          parentStyleSheet=parentStyleSheet)

        self.atkeyword = u'@page'
        
        if selectorText:
            self.selectorText = selectorText
            self.seq.append(self.selectorText)
        else:
            self._selectorText = u''
        if style:
            self.style = style
            self.seq.append(self.style)
        else:
            self._style = CSSStyleDeclaration(parentRule=self)
        
        self._readonly = readonly

    def __parseSelectorText(self, selectorText):
        """
        parses selectorText which may also be a list of tokens
        and returns (selectorText, seq)

        see _setSelectorText for details
        """
        # for closures: must be a mutable
        new = {'selector': None, 'valid': True}

        def _char(expected, seq, token, tokenizer=None):
            # name
            val = self._tokenvalue(token)
            if ':' == expected and u':' == val:
                try:
                    identtoken = tokenizer.next()
                except StopIteration:
                    self._log.error(
                        u'CSSPageRule selectorText: No IDENT found.', token)
                else:
                    ival, ityp = self._tokenvalue(identtoken), self._type(identtoken)
                    if 'IDENT' != ityp:
                        self._log.error(
                            u'CSSPageRule selectorText: Expected IDENT but found: %r' % 
                            ival, token)
                    else:
                        new['selector'] = val + ival
                        seq.append(new['selector'])
                        return 'EOF'
                return expected
            else:
                new['valid'] = False
                self._log.error(
                    u'CSSPageRule selectorText: Unexpected CHAR: %r' % val, token)
                return expected

        newseq = []
        valid, expected = self._parse(expected=':',
            seq=newseq, tokenizer=self._tokenize2(selectorText),
            productions={'CHAR': _char})
        valid = valid and new['valid']
        newselector = new['selector']
        
        # post conditions
        if expected == 'ident':
            self._log.error(
                u'CSSPageRule selectorText: No valid selector: %r' %
                    self._valuestr(selectorText))
            
        if not newselector in (None, u':first', u':left', u':right'):
            self._log.warn(u'CSSPageRule: Unknown CSS 2.1 @page selector: %r' %
                     newselector, neverraise=True)

        return newselector, newseq

    def _getCssText(self):
        """
        returns serialized property cssText
        """
        return cssutils.ser.do_CSSPageRule(self)

    def _setCssText(self, cssText):
        """
        DOMException on setting

        - SYNTAX_ERR: (self, StyleDeclaration)
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
        super(CSSPageRule, self)._setCssText(cssText)
        
        tokenizer = self._tokenize2(cssText)
        attoken = self._nexttoken(tokenizer, None)
        if not attoken or u'@page' != self._tokenvalue(
                                                attoken, normalize=True):
            self._log.error(u'CSSPageRule: No CSSPageRule found: %s' %
                self._valuestr(cssText),
                error=xml.dom.InvalidModificationErr)
        else:
            valid = True
            selectortokens = self._tokensupto2(tokenizer, blockstartonly=True)
            styletokens = self._tokensupto2(tokenizer, blockendonly=True)
            
            try:
                bracetoken = selectortokens.pop()
            except IndexError:
                bracetoken = None
            if self._tokenvalue(bracetoken) != u'{':
                valid = False
                self._log.error(
                    u'CSSPageRule: No start { of style declaration found: %r' %
                    self._valuestr(cssText), bracetoken)
                
            newselector, newselectorseq = self.__parseSelectorText(selectortokens)

            newstyle = CSSStyleDeclaration()
            if not styletokens:
                valid = False
                self._log.error(
                    u'CSSPageRule: No style declaration or "}" found: %r' %
                    self._valuestr(cssText))            

            braceorEOFtoken = styletokens.pop()
            val, typ = self._tokenvalue(braceorEOFtoken), self._type(braceorEOFtoken)
            if val != u'}' and typ != 'EOF':
                valid = False
                self._log.error(
                    u'CSSPageRule: No "}" after style declaration found: %r' %
                    self._valuestr(cssText))
            else:
                if 'EOF' == typ:
                    # add again as style needs it
                    styletokens.append(braceorEOFtoken)
                newstyle.cssText = styletokens

            if valid:
                self._selectorText = newselector # already parsed
                self.style = newstyle
                self.seq = newselectorseq # contains upto style only

    cssText = property(_getCssText, _setCssText,
        doc="(DOM) The parsable textual representation of the rule.")

    def _getSelectorText(self):
        """
        wrapper for cssutils Selector object
        """
        return self._selectorText

    def _setSelectorText(self, selectorText):
        """
        wrapper for cssutils Selector object

        selector: DOM String
            in CSS 2.1 one of
            - :first
            - :left
            - :right
            - empty

        If WS or Comments are included they are ignored here! Only
        way to add a comment is via setting ``cssText``

        DOMException on setting

        - SYNTAX_ERR:
          Raised if the specified CSS string value has a syntax error
          and is unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this rule is readonly.
        """
        self._checkReadonly()

        # may raise SYNTAX_ERR
        newselectortext, newseq = self.__parseSelectorText(selectorText)

        if newselectortext:
            for i, x in enumerate(self.seq):
                if x == self._selectorText:
                    self.seq[i] = newselectortext
            self._selectorText = newselectortext

    selectorText = property(_getSelectorText, _setSelectorText,
        doc="""(DOM) The parsable textual representation of the page selector for the rule.""")

    def _getStyle(self):
        
        return self._style

    def _setStyle(self, style):
        """
        style
            StyleDeclaration or string
        """
        self._checkReadonly()
        
        if isinstance(style, basestring):
            self._style.cssText = style
        else:
            # cssText would be serialized with optional preferences
            # so use seq!
            self._style.seq = style.seq 

    style = property(_getStyle, _setStyle,
        doc="(DOM) The declaration-block of this rule set.")

    valid = property(lambda self: True)

    def __repr__(self):
        return "cssutils.css.%s(selectorText=%r, style=%r)" % (
                self.__class__.__name__, self.selectorText, self.style.cssText)

    def __str__(self):
        return "<cssutils.css.%s object selectorText=%r style=%r at 0x%x>" % (
                self.__class__.__name__, self.selectorText, self.style.cssText,
                id(self))
