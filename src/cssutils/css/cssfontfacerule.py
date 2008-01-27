"""CSSFontFaceRule implements DOM Level 2 CSS CSSFontFaceRule.
"""
__all__ = ['CSSFontFaceRule']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-10-18 22:44:54 +0200 (Do, 18 Okt 2007) $'
__version__ = '$LastChangedRevision: 507 $'

import xml.dom
import cssrule
import cssutils
from cssstyledeclaration import CSSStyleDeclaration

class CSSFontFaceRule(cssrule.CSSRule):
    """
    The CSSFontFaceRule interface represents a @font-face rule in a CSS
    style sheet. The @font-face rule is used to hold a set of font 
    descriptions.

    Properties
    ==========
    cssText: of type DOMString
        The parsable textual representation of this rule
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

        font_face
          : FONT_FACE_SYM S*
            '{' S* declaration [ ';' S* declaration ]* '}' S*
          ;
    """
    type = cssrule.CSSRule.FONT_FACE_RULE

    def __init__(self, style=None, parentRule=None, 
                 parentStyleSheet=None, readonly=False):
        """
        if readonly allows setting of properties in constructor only

        style
            CSSStyleDeclaration for this CSSStyleRule
        """
        super(CSSFontFaceRule, self).__init__(parentRule=parentRule, 
                                              parentStyleSheet=parentStyleSheet)

        self.atkeyword = u'@font-face'
        
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
        return cssutils.ser.do_CSSFontFaceRule(self)

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
        super(CSSFontFaceRule, self)._setCssText(cssText)
        
        tokenizer = self._tokenize2(cssText)
        attoken = self._nexttoken(tokenizer, None)
        if not attoken or u'@font-face' != self._tokenvalue(
                                                attoken, normalize=True):
            self._log.error(u'CSSFontFaceRule: No CSSFontFaceRule found: %s' %
                self._valuestr(cssText),
                error=xml.dom.InvalidModificationErr)
        else:
            valid = True
            beforetokens = self._tokensupto2(tokenizer, blockstartonly=True)            
            try:
                bracetoken = beforetokens.pop()
            except IndexError:
                bracetoken = None
            if self._tokenvalue(bracetoken) != u'{':
                valid = False
                self._log.error(
                    u'CSSFontFaceRule: No start { of style declaration found: %r' %
                    self._valuestr(cssText), bracetoken)
            
            # parse stuff before { which should be comments and S only
            new = {'valid': True}
            newseq = []
            beforevalid, expected = self._parse(expected=':',
                seq=newseq, tokenizer=self._tokenize2(beforetokens),
                productions={})
            valid = valid and beforevalid and new['valid']
    
            styletokens = self._tokensupto2(tokenizer, blockendonly=True)
            newstyle = CSSStyleDeclaration()
            if not styletokens:
                valid = False
                self._log.error(
                    u'CSSFontFaceRule: No style declaration or "}" found: %r' %
                    self._valuestr(cssText))            

            braceorEOFtoken = styletokens.pop()
            val, typ = self._tokenvalue(braceorEOFtoken), self._type(braceorEOFtoken)
            if val != u'}' and typ != 'EOF':
                valid = False
                self._log.error(
                    u'CSSFontFaceRule: No "}" after style declaration found: %r' %
                    self._valuestr(cssText))
            else:
                if 'EOF' == typ:
                    # add again as style needs it
                    styletokens.append(braceorEOFtoken)
                newstyle.cssText = styletokens

            if valid:
                self.valid = True
                self.style = newstyle
                self.seq = newseq # contains upto { only

    cssText = property(_getCssText, _setCssText,
        doc="(DOM) The parsable textual representation of the rule.")

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
            self._style.seq = style.seq

    style = property(_getStyle, _setStyle,
        doc="(DOM) The declaration-block of this rule set.")

    def __repr__(self):
        return "cssutils.css.%s(style=%r)" % (
                self.__class__.__name__, self.style.cssText)

    def __str__(self):
        return "<cssutils.css.%s object style=%r at 0x%x>" % (
                self.__class__.__name__, self.style.cssText, id(self))
