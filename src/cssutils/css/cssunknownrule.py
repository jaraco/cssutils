"""CSSUnknownRule implements DOM Level 2 CSS CSSUnknownRule.
"""
__all__ = ['CSSUnknownRule']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssrule
import cssutils

class CSSUnknownRule(cssrule.CSSRule):
    """
    represents an at-rule not supported by this user agent.

    Properties
    ==========
    inherited from CSSRule
        - cssText
        - type

    cssutils only
    -------------
    atkeyword:
        the literal keyword used
    seq: a list (cssutils)
        All parts of this rule excluding @KEYWORD but including CSSComments

    Format
    ======
    unknownrule:
        @xxx until ';' or block {...}
    """
    type = cssrule.CSSRule.UNKNOWN_RULE

    def __init__(self, cssText=u'', readonly=False):
        """
        cssText
            of type string
        """
        super(CSSUnknownRule, self).__init__()

        self.valid = True # always as unknown...
        if cssText:
            self.cssText = cssText
        else:
            self.atkeyword = None
            
        self._readonly = readonly


    def _getCssText(self):
        """ returns serialized property cssText """
        return cssutils.ser.do_CSSUnknownRule(self)

    def _setCssText(self, cssText):
        """
        DOMException on setting
        
        - SYNTAX_ERR:
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        - INVALID_MODIFICATION_ERR:
          Raised if the specified CSS string value represents a different
          type of rule than the current one.
        - HIERARCHY_REQUEST_ERR: (never raised)
          Raised if the rule cannot be inserted at this point in the
          style sheet.
        - NO_MODIFICATION_ALLOWED_ERR: (CSSRule)
          Raised if the rule is readonly.
        """
        super(CSSUnknownRule, self)._setCssText(cssText)
        tokenizer = self._tokenize2(cssText)
        attoken = self._nexttoken(tokenizer, None)
        if not attoken or 'ATKEYWORD' != self._type(attoken):
            self._log.error(u'CSSUnknownRule: No CSSUnknownRule found.',
                            error=xml.dom.InvalidModificationErr)
        else:
            newatkeyword = self._tokenvalue(attoken)
            newseq = []
            for token in tokenizer:
                if 'INVALID' == self._type(token):
                    return
                newseq.append(self._tokenvalue(token))

            self.atkeyword = newatkeyword
            self.seq = newseq

    cssText = property(fget=_getCssText, fset=_setCssText,
        doc="(DOM) The parsable textual representation.")
    
    def __repr__(self):
        return "cssutils.css.%s(cssText=%r)" % (
                self.__class__.__name__, self.cssText)
        
    def __str__(self):
        return "<cssutils.css.%s object cssText=%r at 0x%x>" % (
                self.__class__.__name__, self.cssText, id(self))
