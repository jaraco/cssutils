"""CSSNamespaceRule currently implements
http://www.w3.org/TR/2006/WD-css3-namespace-20060828/

The following changes have been done:
    1. the url() syntax is not implemented as it may (?) be deprecated
    anyway
"""
__all__ = ['CSSNamespaceRule']
__docformat__ = 'restructuredtext'
__version__ = '0.9.1a4'

import xml.dom

import cssrule
import cssutils


class CSSNamespaceRule(cssrule.CSSRule):
    """
    Represents an @namespace rule within a CSS style sheet.

    The @namespace at-rule declares a namespace prefix and associates
    it with a given namespace (a string). This namespace prefix can then be
    used in namespace-qualified names such as those described in the
    Selectors Module [SELECT] or the Values and Units module [CSS3VAL].    

    Properties
    ==========
    cssText: of type DOMString
        The parsable textual representation of this rule
    uri: of type DOMString
        The namespace URI (a simple string!) which is bound to the given
        prefix. If no prefix is set (``CSSNamespaceRule.prefix==''``)
        the namespace defined by uri is set as the default namespace.
    prefix: of type DOMString
        The prefix used in the stylesheet for the given
        ``CSSNamespaceRule.nsuri``. If prefix is empty uri sets the default
        namespace for the stylesheet.
        
    cssutils only
    -------------
    atkeyword: 
        the literal keyword used

    Inherits properties from CSSRule

    Format
    ======
    namespace
      : NAMESPACE_SYM S* [namespace_prefix S*]? [STRING|URI] S* ';' S*
      ;
    namespace_prefix
      : IDENT
      ;        
    """
    type = cssrule.CSSRule.NAMESPACE_RULE

    def __init__(self, uri=None, prefix=u'', readonly=False):
        """
        if readonly allows setting of properties in constructor only

        Do not use as positional but as keyword attributes only!

        uri
            The namespace URI (a simple string!) which is bound to the
            given prefix. If no prefix is set
            (``CSSNamespaceRule.prefix==''``) the namespace defined by
            uri is set as the default namespace
        prefix
            The prefix used in the stylesheet for the given
            ``CSSNamespaceRule.uri``.
        """
        super(CSSNamespaceRule, self).__init__()
        
        self.atkeyword = u'@namespace'
        self.uri = uri
        self.prefix = prefix
        self.seq = [self.prefix, self.uri]

        self._readonly = readonly        
    

    def _getURI(self):
        """ returns uri as a string """
        return self._uri

    def _setURI(self, uri):
        """ 
        DOMException on setting
        
        - SYNTAX_ERR: (not checked here)
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (CSSRule)
          Raised if this rule is readonly.
        """
        self._checkReadonly()

        # update seq
        for i, x in enumerate(self.seq):
            if x == self._uri:
                self.seq[i] = uri
                break
        else:
            self.seq = [uri]
        # set new uri
        self._uri = uri

    uri = property(_getURI, _setURI,
        doc="URI (string!) of the defined namespace.")


    def _getPrefix(self):
        """ returns prefix """
        return self._prefix

    def _setPrefix(self, prefix=u''):
        """ 
        DOMException on setting
        
        - SYNTAX_ERR: (not checked here)
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (CSSRule)
          Raised if this rule is readonly.
        """
        self._checkReadonly()

        # set new uri
        self._prefix = prefix

        for i, x in enumerate(self.seq):
            if x == self._prefix:
                self.seq[i] = prefix
                break
        else:
            self.seq[0] = prefix # put prefix at the beginning!

    prefix = property(_getPrefix, _setPrefix,
        doc="Prefix used for the defined namespace.")


    def _getCssText(self):
        """ 
        returns serialized property cssText 
        """
        return cssutils.ser.do_CSSNamespaceRule(self)

    def _setCssText(self, cssText):
        """
        DOMException on setting
        
        - HIERARCHY_REQUEST_ERR: (CSSStylesheet)
          Raised if the rule cannot be inserted at this point in the
          style sheet.
        - INVALID_MODIFICATION_ERR: (self)
          Raised if the specified CSS string value represents a different
          type of rule than the current one.            
        - NO_MODIFICATION_ALLOWED_ERR: (CSSRule)
          Raised if the rule is readonly.
        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        """
        super(CSSNamespaceRule, self)._setCssText(cssText)          
        tokens = self._tokenize(cssText)
        valid = True

        # check if right type    
        if not tokens or tokens and tokens[0].type != self._ttypes.NAMESPACE_SYM:
            self._log.error(u'CSSNamespaceRule: No CSSNamespaceRule found: %s' %
                      self._valuestr(cssText),
                      error=xml.dom.InvalidModificationErr)
            return
        else:
            newatkeyword = tokens[0].value
            
        newseq = []
        newuri = None
        newprefix = u''

        expected = 'uri or prefix' # uri semicolon
        for i in range(1, len(tokens)):
            t = tokens[i]
            if self._ttypes.S == t.type: # ignore
                pass 
                
            elif self._ttypes.COMMENT == t.type:
                newseq.append(cssutils.css.CSSComment(t))
                
            elif 'uri or prefix' == expected and self._ttypes.IDENT == t.type:
                newprefix = t.value
                newseq.append(newprefix)
                expected = 'uri'

            elif expected.startswith('uri') and \
                 t.type in (self._ttypes.URI, self._ttypes.STRING):
                if t.type == self._ttypes.URI:
                    newuri = t.value[4:-1] # url(href)
                    self._log.warn(
                        u'CSSNamespaceRule: Found namespace definition with url(uri), this may be deprecated in the future, use string format "uri" instead.',
                        t, error = None, neverraise=True)
                else:
                    newuri = t.value[1:-1] # "href" or 'href'
                newseq.append(newuri)
                expected = 'semicolon'

            elif self._ttypes.SEMICOLON == t.type:
                if 'semicolon' != expected: # normal end
                    valid = False
                    self._log.error(
                        u'CSSNamespaceRule: No namespace URI found.', t)
                expected = None                     
                continue

            else:
                valid = False
                self._log.error(u'CSSNamespaceRule: Syntax Error.', t)

        if expected:
            valid = False
            self._log.error(u'CSSNamespaceRule: Syntax Error, no ";" found: %s' %
                      self._valuestr(cssText))
            return

        if valid:
            self.atkeyword = newatkeyword
            self.uri = newuri
            self.prefix = newprefix
            self.seq = newseq

    cssText = property(fget=_getCssText, fset=_setCssText,
        doc="(DOM attribute) The parsable textual representation.")


if __name__ == '__main__':
    c = CSSNamespaceRule()
    c.uri = "x"
    print c.cssText
    c.prefix = "p"
    print c.cssText
    c.cssText = r'''@namespace "\"";'''   
    print c.cssText