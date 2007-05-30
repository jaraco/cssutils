"""CSSComment is not defined in DOM Level 2 at all but a cssutils defined
class.
Implements CSSRule which is also extended for a CSSComment rule type
"""
__all__ = ['CSSComment']
__docformat__ = 'restructuredtext'
__version__ = '0.9.1a4'

import xml.dom

import cssrule
import cssutils


class CSSComment(cssrule.CSSRule):
    """
    (cssutils) a CSS comment

    Properties
    ==========
    cssText: of type DOMString
        The comment text including comment delimiters

    Inherits properties from CSSRule

    Format
    ======
    ::
    
        /*...*/
    """
    type = cssrule.CSSRule.COMMENT # value = -1

    def __init__(self, cssText=None, readonly=False):
        super(CSSComment, self).__init__()

        if cssText:
            self._setCssText(cssText)
        else:
            self._cssText = None

        self._readonly = readonly

        
    def _getCssText(self):
        """returns serialized property cssText"""
        return cssutils.ser.do_CSSComment(self)

    def _setCssText(self, cssText):
        """
        cssText
            textual text to set or tokenlist which is not tokenized
            anymore. May also be a single token for this rule
        parser
            if called from cssparser directly this is Parser instance

        DOMException on setting
        
        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        - INVALID_MODIFICATION_ERR: (self)
          Raised if the specified CSS string value represents a different
          type of rule than the current one.            
        - NO_MODIFICATION_ALLOWED_ERR: (CSSRule)
          Raised if the rule is readonly.
        """
        super(CSSComment, self)._setCssText(cssText)
        tokens = self._tokenize(cssText)        

        if not tokens or tokens[0].type != self._ttypes.COMMENT:
            self._log.error(u'CSSComent: Not a CSSComment: %s' %
                self._valuestr(cssText),
                error=xml.dom.InvalidModificationErr)
        elif len(tokens) > 1:
            self._log.error(
                u'CSSComment: Syntax error. %s' % cssText)
        else:
            token = tokens[0]
            self._cssText = token.value

    cssText = property(_getCssText, _setCssText,
        doc=u"(cssutils) Textual representation of this comment")
