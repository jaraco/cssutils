"""CSSCharsetRule implements DOM Level 2 CSS CSSCharsetRule.

TODO:
    - check specific allowed syntaxes
    - check encoding syntax and not codecs.lookup?
"""
__all__ = ['CSSCharsetRule']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a1, $LastChangedRevision$'

import codecs
import re
import xml.dom

import cssrule
import cssutils


class CSSCharsetRule(cssrule.CSSRule):
    """
    The CSSCharsetRule interface represents an @charset rule in a CSS style
    sheet. The value of the encoding attribute does not affect the encoding
    of text data in the DOM objects; this encoding is always UTF-16
    (also in Python?). After a stylesheet is loaded, the value of the
    encoding attribute is the value found in the @charset rule. If there
    was no @charset in the original document, then no CSSCharsetRule is
    created. The value of the encoding attribute may also be used as a hint
    for the encoding used on serialization of the style sheet.

    The value of the @charset rule (and therefore of the CSSCharsetRule)
    may not correspond to the encoding the document actually came in;
    character encoding information e.g. in an HTTP header, has priority
    (see CSS document representation) but this is not reflected in the
    CSSCharsetRule.

    Properties
    ==========
    cssText: of type DOMString
        The parsable textual representation of this rule
    encoding: of type DOMString
        The encoding information used in this @charset rule.    

    Inherits properties from CSSRule

    Format
    ======
    charsetrule:
        CHARSET_SYM S* STRING S* ';'

    BUT: Only valid format is:
        @charset "ENCODING";
    """
    type = cssrule.CSSRule.CHARSET_RULE 

    def __init__(self, encoding=None, readonly=False):
        """
        encoding: 
            a valid character encoding
        readonly: 
            defaults to False, not used yet        

        if readonly allows setting of properties in constructor only
        """
        super(CSSCharsetRule, self).__init__()
        
        self._encoding = None
        if encoding:
            self.encoding = encoding

        self._pat = re.compile(u'^@charset "(.+?)";$',
                                 re.DOTALL | re.IGNORECASE | re.UNICODE) 

        self._readonly = readonly        

    def _getEncoding(self):
        """ returns encoding as a string """
        return self._encoding

    def _setEncoding(self, encoding):
        """
        DOMException on setting
        
        - NO_MODIFICATION_ALLOWED_ERR: (CSSRule)
          Raised if this encoding rule is readonly.
        - SYNTAX_ERR: (self)
          Raised if the specified encoding value has a syntax error and
          is unparsable.
          Currently only valid Python encodings are allowed.            
        """        
        self._checkReadonly()
        tokens = self._tokenize(encoding)
        valid = True

        if tokens and tokens[0].type != self._ttypes.IDENT or len(tokens) != 1:
            valid = False
            self._log.error(
                'CSSCharsetRule: Syntax Error in encoding value "%s".' %
                      encoding)
        try:
            codecs.lookup(encoding)
        except LookupError:
            valid = False
            self._log.error('CSSCharsetRule: Unknown (Python) encoding "%s".' %
                      encoding)
        if valid:
            self._encoding = encoding.lower()
                
    encoding = property(_getEncoding, _setEncoding,
        doc="(DOM)The encoding information used in this @charset rule.")


    def _getCssText(self):
        """returns serialized property cssText"""
        return cssutils.ser.do_CSSCharsetRule(self)

    def _setCssText(self, cssText):
        """
        DOMException on setting
        
        - SYNTAX_ERR: (self)
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
        super(CSSCharsetRule, self)._setCssText(cssText)
        tokens = self._tokenize(cssText)

        text = ''.join([t.value for t in tokens])
        # check if right token            
        if not text.startswith(u'@charset'):
            self._log.error(
                u'No CSSCharsetRule: %s' % text,
                error=xml.dom.InvalidModificationErr)
            return

        encoding = self._pat.match(text)
        if not encoding:
            self._log.error(u'CSSCharsetRule: Syntax Error: "%s".' % text,
                      tokens[0])
        else:
            encoding = encoding.group(1)
            if not encoding:
                self._log.error(
                    u'CSSCharsetRule: No Encoding found: "%s".' % text,
                    tokens[0])
            else:
                encoding
                self.encoding = encoding # also sets self.valid
        
    cssText = property(fget=_getCssText, fset=_setCssText,
        doc="(DOM) The parsable textual representation.")


if __name__ == '__main__':
    p = cssutils.CSSParser()
    s = p.parseString('@charset')
    print s.cssRules

    c = CSSCharsetRule('utf-8')
    c.cssText = u' @charset "ascii" ;'
    