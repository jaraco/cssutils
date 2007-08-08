"""CSSStyleRule implements DOM Level 2 CSS CSSStyleRule.

TODO
- parentRule?
- parentStyleSheet?
"""
__all__ = ['CSSStyleRule']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssrule
import cssstyledeclaration
import cssutils
from selector import Selector
from selectorlist import SelectorList

class CSSStyleRule(cssrule.CSSRule):
    """
    represents a single rule set in a CSS style sheet.

    Properties
    ==========
    cssText: of type DOMString
        The parsable textual representation of this rule
    selectorText: of type DOMString
        The textual representation of the selector for the rule set. The
        implementation may have stripped out insignificant whitespace while
        parsing the selector.
    style: of type CSSStyleDeclaration, (DOM)
        The declaration-block of this rule set.

    cssutils only
    -------------
    selectorList: of type SelectorList (cssutils only)
        A list of all Selector elements for the rule set.

    Inherits properties from CSSRule

    Format
    ======
    ruleset
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
            self._selectorList = SelectorList()
        if style:
            self.style = style
            self.seq.append(self.style)
        else:
            self._style = cssstyledeclaration.CSSStyleDeclaration(
                parentRule=self)

        self._readonly = readonly

    def _getCssText(self):
        """
        returns serialized property cssText
        """
        return cssutils.ser.do_CSSStyleRule(self)

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
        super(CSSStyleRule, self)._setCssText(cssText)
        tokens = self._tokenize(cssText)
        valid = True

        # check if right token
        if not tokens or tokens[0].value.startswith(u'@'):
            self._log.error(u'CSSStyleRule: No CSSStyleRule found: %s' %
                      self._valuestr(cssText),
                      error=xml.dom.InvalidModificationErr)
            return

        # init
        newselectorList = SelectorList()
        newstyle = cssstyledeclaration.CSSStyleDeclaration(parentRule=self)
        newseq = []

        # get selector (must be one, see above)
        selectortokens, endi = self._tokensupto(tokens,
                                                    blockstartonly=True)
        expected = '{' # or None (end)
        if selectortokens[-1].value != expected:
            self._log.error(u'CSSStyleRule: No StyleDeclaration found.',
                selectortokens[-1])
            return
        newselectorList.selectorText = selectortokens[:-1]
        newseq.append(newselectorList)

        # get rest (StyleDeclaration and Comments)
        i, imax = endi, len(tokens)
        while i < imax:
            t = tokens[i]
            if self._ttypes.EOF == t.type:
                expected = 'EOF'

            elif self._ttypes.S == t.type: # ignore
                pass

            elif self._ttypes.COMMENT == t.type: # just add
                newseq.append(cssutils.css.CSSComment(t))

            elif self._ttypes.LBRACE == t.type:
                foundtokens, endi = self._tokensupto(
                    tokens[i:], blockendonly=True)
                i += endi
                if len(foundtokens) < 2:
                    self._log.error(u'CSSStyleRule: Syntax Error.', t)
                    return
                else:
                    styletokens = foundtokens[1:-1] # without { and }
                    newstyle = cssstyledeclaration.CSSStyleDeclaration(
                        parentRule=self)
                    newstyle.cssText = styletokens
                    newseq.append(newstyle)
                    expected = '}'
                continue

            elif '}' == expected and self._ttypes.RBRACE == t.type:
                expected = None

            else:
                self._log.error(u'CSSStyleRule: Unexpected token.', t)
                return

            i += 1

        if expected == '{':
            self._log.error(u'CSSStyleRule: No StyleDeclaration found: %s' %
                      self._valuestr(cssText))
            return
        elif expected and expected == 'EOF':
            self._log.error(u'CSSStyleRule: Trailing text after ending "}" or no end of StyleDeclaration found: %s' %
                      self._valuestr(cssText))
            return
        else:
            # everything ok
            self.selectorList = newselectorList
            self.style = newstyle
            self.seq = newseq

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
        wrapper for cssutils Selector object
        """
        return self._selectorList.selectorText

    def _setSelectorText(self, selectorText):
        """
        wrapper for cssutils Selector object

        selector
            of type string, might also be a comma separated list of
            selectors

        DOMException on setting

        - SYNTAX_ERR:
          Raised if the specified CSS string value has a syntax error
          and is unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this rule is readonly.
        """
        self._checkReadonly()
        self._selectorList = SelectorList(selectorText)

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
            # may raise Exception!
            temp = cssstyledeclaration.CSSStyleDeclaration(parentRule=self)
            temp.cssText = style
            self._style = temp
        else:
            self._style = style
            style.parentRule = self

    style = property(_getStyle, _setStyle,
        doc="(DOM) The declaration-block of this rule set.")

    def __repr__(self):
        return "<cssutils.css.%s object selector=%r at 0x%x>" % (
                self.__class__.__name__, self.selectorText, id(self))


if __name__ == '__main__':
    cssutils.css.cssstylerule.Selector = Selector # for main test
    r = CSSStyleRule()
    r.cssText = 'a {}a'
    r.selectorText = u'b + a'
    print r.cssText


