"""CSSPageRule implements DOM Level 2 CSS CSSPageRule.
"""
__all__ = ['CSSPageRule']
__docformat__ = 'restructuredtext'
__version__ = '0.9.1a4'

import xml.dom

import cssrule
import cssstyledeclaration
import cssutils

from selector import Selector


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
    page
      : PAGE_SYM S* pseudo_page? S*
        LBRACE S* declaration [ ';' S* declaration ]* '}' S*
      ;
    pseudo_page
      : ':' IDENT # :first, :left, :right in CSS 2.1
      ;
    """
    type = cssrule.CSSRule.PAGE_RULE 

    def __init__(self, selectorText=None, style=None, readonly=False):
        """
        if readonly allows setting of properties in constructor only
        
        selectorText
            type string
        style
            CSSStyleDeclaration for this CSSStyleRule
        """
        super(CSSPageRule, self).__init__()
        
        self.atkeyword = u'@page'
        if selectorText:
            self.selectorText = selectorText
            self.seq.append(self.selectorText)
        else:
            self._selectorText = u''
        if style:
            self.style = style
        else:
            self._style = cssstyledeclaration.CSSStyleDeclaration(
                parentRule=self)

        self._readonly = readonly


    def __parseSelectorText(self, selectorText):
        """
        parses selectorText which may also be a list of tokens
        and returns (selectorText, seq)

        raises SYNTAX_ERR:
        """        
        tokens = self._tokenize(selectorText)
            
        newselectortext = None
        newseq = []

        i = 0
        expected = ':' # means no selector but 1 like ":first" is okay
        while i < len(tokens):
            t = tokens[i]
            if self._ttypes.S == t.type and 'ident' != expected: # ignore
                pass
                
            elif self._ttypes.COMMENT == t.type and 'ident' != expected: # just add
                newseq.append(cssutils.css.CSSComment(t))

            elif u':' == t.value  and ':' == expected: # selector start :
                expected = 'ident'

            elif self._ttypes.IDENT == t.type and 'ident' == expected: # selector
                newselectortext = u':%s' % t.value
                newseq.append(newselectortext)
                expected = None

            else:
                self._log.error(u'CSSPageRule: Syntax Error in selector: "%s".' %
                          self._valuestr(tokens))
                return None, None
            
            i += 1
            
        if expected and expected != ':':
            self._log.error(u'CSSPageRule: Invalid Selector: "%s".' %
                      self._valuestr(tokens))
            return None, None

        if newselectortext is None:
            newselectortext = u''

        # warn only
        if not newselectortext in (u'', u':first', u':left', u':right'):
            self._log.warn(u'CSSPageRule: Unknown CSS 2.1 @page selector: "%s".' %
                     self._valuestr(tokens), neverraise=True)

        return newselectortext, newseq

        
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
        tokens = self._tokenize(cssText)

        # check if right token    
        if not tokens or tokens and tokens[0].type != self._ttypes.PAGE_SYM:
            self._log.error(u'CSSPageRule: No CSSPageRule found: %s' %
                      self._valuestr(cssText),
                      error=xml.dom.InvalidModificationErr)
            return
        else:
            newatkeyword = tokens[0].value

        # init
        newstyle = cssstyledeclaration.CSSStyleDeclaration(parentRule=self)

        # selector
        selectortokens, stylestarti = self._tokenizer.tokensupto(
            tokens, blockstartonly=True)
        newselectortext, newseq = self.__parseSelectorText(
            selectortokens[1:-1]) # without @page and {

        # style
        styletokens, styleendi = self._tokenizer.tokensupto(
            tokens[stylestarti:], blockendonly=True)

        if not styletokens or \
           styletokens[0].value != u'{' or \
           styletokens[-1].value != u'}' or \
           len(tokens) > stylestarti + styleendi + 1:
            self._log.error(u'CSSPageRule: Invalid style found: %s' %
                      self._valuestr(styletokens[1:-1]))
            return

        newstyle = cssstyledeclaration.CSSStyleDeclaration(
                parentRule=self, cssText=styletokens[1:-1])

        # seems ok
        if newstyle:
            if newselectortext: # optional
                self._selectorText = newselectortext
            self.seq = newseq
            self.style = newstyle

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
            # may raise Exception!
            temp = cssstyledeclaration.CSSStyleDeclaration(parentRule=self)
            temp.cssText = style
            self._style = temp
        else:
            self._style = style
            style.parentRule = self

    style = property(_getStyle, _setStyle,
        doc="(DOM) The declaration-block of this rule set.")


if __name__ == '__main__':
    import property
    cssutils.css.cssstyledeclaration.Property = property._Property
    cssutils.css.cssstylerule.Selector = Selector # for main test        
    r = CSSPageRule()
    r.cssText = '@page :right { margin: 0 }'
    #r.selectorText = u':left :a'
    print r.cssText


