"""CSSPageRule implements DOM Level 2 CSS CSSPageRule.
"""
__all__ = ['CSSPageRule']
__docformat__ = 'restructuredtext'
__version__ = '$Id$'

from cssstyledeclaration import CSSStyleDeclaration
from selectorlist import SelectorList
import cssrule
import cssutils
import xml.dom

class CSSPageRule(cssrule.CSSRule):
    """
    The CSSPageRule interface represents a @page rule within a CSS style
    sheet. The @page rule is used to specify the dimensions, orientation,
    margins, etc. of a page box for paged media.

    Properties
    ==========
    atkeyword (cssutils only)
        the literal keyword used
    cssText: of type DOMString
        The parsable textual representation of this rule
    selectorText: of type DOMString
        The parsable textual representation of the page selector for the rule.
    style: of type CSSStyleDeclaration
        The declaration-block of this rule.

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
    type = property(lambda self: cssrule.CSSRule.PAGE_RULE)
    # constant but needed:
    wellformed = True 

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
        self._atkeyword = u'@page'
        tempseq = self._tempSeq()
        if selectorText:
            self.selectorText = selectorText
            tempseq.append(self.selectorText, 'selectorText')
        else:
            self._selectorText = self._tempSeq()
        if style:
            self.style = style
            tempseq.append(self.style, 'style')
        else:
            self._style = CSSStyleDeclaration(parentRule=self,
                                              profiles=(cssutils.profiles.Profiles.CSS_LEVEL_2,))
        self._setSeq(tempseq)
        
        self._readonly = readonly

    def __parseSelectorText(self, selectorText):
        """
        parses selectorText which may also be a list of tokens
        and returns (selectorText, seq)

        see _setSelectorText for details
        """
        # for closures: must be a mutable
        new = {'wellformed': True, 'last-S': False}

        def _char(expected, seq, token, tokenizer=None):
            # pseudo_page, :left, :right or :first
            val = self._tokenvalue(token)
            if not new['last-S'] and expected in ['page', ': or EOF'] and u':' == val:
                try:
                    identtoken = tokenizer.next()
                except StopIteration:
                    self._log.error(
                        u'CSSPageRule selectorText: No IDENT found.', token)
                else:
                    ival, ityp = self._tokenvalue(identtoken), self._type(identtoken)
                    if self._prods.IDENT != ityp:
                        self._log.error(
                            u'CSSPageRule selectorText: Expected IDENT but found: %r' % 
                            ival, token)
                    else:
                        seq.append(val + ival, 'pseudo')
                        return 'EOF'
                return expected
            else:
                new['wellformed'] = False
                self._log.error(
                    u'CSSPageRule selectorText: Unexpected CHAR: %r' % val, token)
                return expected

        def S(expected, seq, token, tokenizer=None):
            "Does not raise if EOF is found."
            if expected == ': or EOF':
                # pseudo must directly follow IDENT if given
                new['last-S'] = True
            return expected

        def IDENT(expected, seq, token, tokenizer=None):
            ""
            val = self._tokenvalue(token)
            if 'page' == expected:
                seq.append(val, 'IDENT')
                return ': or EOF'
            else:
                new['wellformed'] = False
                self._log.error(
                    u'CSSPageRule selectorText: Unexpected IDENT: %r' % val, token)
                return expected

        def COMMENT(expected, seq, token, tokenizer=None):
            "Does not raise if EOF is found."
            seq.append(cssutils.css.CSSComment([token]), 'COMMENT')
            return expected 

        newseq = self._tempSeq()
        wellformed, expected = self._parse(expected='page',
            seq=newseq, tokenizer=self._tokenize2(selectorText),
            productions={'CHAR': _char,
                         'IDENT': IDENT,
                         'COMMENT': COMMENT, 
                         'S': S}, 
            new=new)
        wellformed = wellformed and new['wellformed']
        
        # post conditions
        if expected == 'ident':
            self._log.error(
                u'CSSPageRule selectorText: No valid selector: %r' %
                    self._valuestr(selectorText))
            
#        if not newselector in (None, u':first', u':left', u':right'):
#            self._log.warn(u'CSSPageRule: Unknown CSS 2.1 @page selector: %r' %
#                     newselector, neverraise=True)

        return wellformed, newseq

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
        if self._type(self._nexttoken(tokenizer)) != self._prods.PAGE_SYM:
            self._log.error(u'CSSPageRule: No CSSPageRule found: %s' %
                            self._valuestr(cssText), 
                            error=xml.dom.InvalidModificationErr)
        else:
            wellformed = True
            selectortokens, startbrace = self._tokensupto2(tokenizer, 
                                                           blockstartonly=True,
                                                           separateEnd=True)
            styletokens, braceorEOFtoken = self._tokensupto2(tokenizer, 
                                                        blockendonly=True,
                                                        separateEnd=True)
            nonetoken = self._nexttoken(tokenizer)
            if self._tokenvalue(startbrace) != u'{':
                wellformed = False
                self._log.error(
                    u'CSSPageRule: No start { of style declaration found: %r' %
                    self._valuestr(cssText), startbrace)
            elif nonetoken:
                wellformed = False
                self._log.error(
                    u'CSSPageRule: Trailing content found.', token=nonetoken)
                
                
            wellformed, newselectorseq = self.__parseSelectorText(selectortokens)

            newstyle = CSSStyleDeclaration(profiles=(cssutils.profiles.Profiles.CSS_LEVEL_2,) )
            val, typ = self._tokenvalue(braceorEOFtoken), self._type(braceorEOFtoken)
            if val != u'}' and typ != 'EOF':
                wellformed = False
                self._log.error(
                    u'CSSPageRule: No "}" after style declaration found: %r' %
                    self._valuestr(cssText))
            else:
                if 'EOF' == typ:
                    # add again as style needs it
                    styletokens.append(braceorEOFtoken)
                newstyle.cssText = styletokens

            if wellformed:
                self._selectorText = newselectorseq # already parsed
                self.style = newstyle
                self._setSeq(newselectorseq) # contains upto style only

    cssText = property(_getCssText, _setCssText,
        doc="(DOM) The parsable textual representation of the rule.")

    def _getSelectorText(self):
        """
        wrapper for cssutils Selector object
        """
        return cssutils.ser.do_CSSPageRuleSelector(self._selectorText)#self._selectorText

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
        wellformed, newseq = self.__parseSelectorText(selectorText)
        if wellformed and newseq:
            self._selectorText = newseq

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
            self._style._seq = style.seq 

    style = property(_getStyle, _setStyle,
        doc="(DOM) The declaration-block of this rule set.")

    def __repr__(self):
        return "cssutils.css.%s(selectorText=%r, style=%r)" % (
                self.__class__.__name__, self.selectorText, self.style.cssText)

    def __str__(self):
        return "<cssutils.css.%s object selectorText=%r style=%r at 0x%x>" % (
                self.__class__.__name__, self.selectorText, self.style.cssText,
                id(self))
