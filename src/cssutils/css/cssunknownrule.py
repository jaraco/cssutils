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
    atkeyword
        keyword used including @, e.g. @-moz-unknown
    cssText: of type DOMString
        The parsable textual representation of this rule
    seq: a list (cssutils)
        All parts of this rule excluding @KEYWORD but including CSSComments
    type: see CSSRule
        The typecode for this rule

    cssutils only
    -------------
    atkeyword:
        the literal keyword used

    Inherits properties from CSSRule

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
        tokens = self._tokenize(cssText)

        if not tokens or tokens and tokens[0].type != self._ttypes.ATKEYWORD:
            self._log.error(u'CSSUnknown: No CSSUnknown found.',
                                error=xml.dom.InvalidModificationErr)
            return
           
        newatkeyword = tokens[0].value[1:]
        newseq = []
        expected = ''
        for i in range(1, len(tokens)):
            t = tokens[i]
            if self._ttypes.EOF == t.type:
                break

            if self._ttypes.S == t.type:
                newseq.append(t.value) # whitespace: add
                
            elif self._ttypes.COMMENT == t.type:
                # Comment: just add
                newseq.append(cssutils.css.CSSComment(t))

            # TODO: block or simple content ending with ;

            elif self._ttypes.INVALID == t.type:
                self.valid = False
                self._log.error(u'CSSUnknown: Invalid Token found.', t)
                return

            else:
                newseq.append(t.value)

        self.atkeyword = newatkeyword
        self.seq = newseq

    cssText = property(fget=_getCssText, fset=_setCssText,
        doc="(DOM) The parsable textual representation.")
    
    def __repr__(self):
        return "cssutils.css.%s()" % (
                self.__class__.__name__)
        
    def __str__(self):
        return "<cssutils.css.%s object at 0x%x>" % (
                self.__class__.__name__, id(self))


if __name__ == '__main__':
    c = CSSUnknownRule('@x something /*comment*/;')
##    print c.seq
##    print c.cssText
##    print
##    c.cssText = u'@x { block /*comment*/ }'
##    print c.seq
##    print c.cssText
    sheet = cssutils.parseString(u'''@three-dee {
          @background-lighting {
            azimuth : 30deg;
            elevation : 190deg;
          }
        }''')
    print "SHEET:", sheet.cssText
