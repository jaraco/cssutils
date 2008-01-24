"""CSSNamespaceRule currently implements
http://www.w3.org/TR/2006/WD-css3-namespace-20060828/

The following changes have been done:
    1. the url() syntax is not implemented as it may (?) be deprecated
    anyway
"""
__all__ = ['CSSNamespaceRule']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssrule
import cssutils
from cssutils.util import Deprecated

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
    namespaceURI: of type DOMString
        The namespace URI (a simple string!) which is bound to the given
        prefix. If no prefix is set (``CSSNamespaceRule.prefix==''``)
        the namespace defined by ``namespaceURI`` is set as the default 
        namespace.
    prefix: of type DOMString
        The prefix used in the stylesheet for the given
        ``CSSNamespaceRule.nsuri``. If prefix is empty namespaceURI sets a 
        default namespace for the stylesheet.

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

    def __init__(self, namespaceURI=None, prefix=None, 
                 cssText=None, parentStyleSheet=None, readonly=False):
        """
        :Parameters:
            namespaceURI
                The namespace URI (a simple string!) which is bound to the
                given prefix. If no prefix is set
                (``CSSNamespaceRule.prefix==''``) the namespace defined by
                namespaceURI is set as the default namespace
            prefix
                The prefix used in the stylesheet for the given
                ``CSSNamespaceRule.uri``.
            cssText
                if no namespaceURI is given cssText must be given to set
                a namespaceURI as this is readonly later on
            parentStyleSheet
                sheet where this rule belongs to

        Do not use as positional but as keyword parameters only!

        If readonly allows setting of properties in constructor only

        format namespace::

            : NAMESPACE_SYM S* [namespace_prefix S*]? [STRING|URI] S* ';' S*
            ;
        """
        self._prefix = u''
        self._namespaceURI = None
        self.atkeyword = u'@namespace'

        super(CSSNamespaceRule, self).__init__()
        
        if namespaceURI:
            self.namespaceURI = namespaceURI
            self.prefix = prefix
            self.seq = [self.prefix, self.namespaceURI]
        elif cssText:
            self.cssText = cssText

        if parentStyleSheet:
            self._parentStyleSheet = parentStyleSheet

        self._readonly = readonly

    def _setNamespaceURI(self, namespaceURI):
        """
        DOMException on setting
    
        :param namespaceURI: the initial value for this rules namespaceURI
        :Exceptions:
            - `NO_MODIFICATION_ALLOWED_ERR`: 
              (CSSRule) Raised if this rule is readonly or a namespaceURI is 
              already set in this rule.
        """
        self._checkReadonly()
        if not self._namespaceURI:
            # initial setting
            self._namespaceURI = namespaceURI
            self.seq = [namespaceURI]
        elif self._namespaceURI != namespaceURI:
            self._log.error(u'CSSNamespaceRule: namespaceURI is readonly.',
                            error=xml.dom.NoModificationAllowedErr)

    namespaceURI = property(lambda self: self._namespaceURI, _setNamespaceURI,
        doc="URI (string!) of the defined namespace.")

    def _setPrefix(self, prefix=None):
        """
        DOMException on setting
        
        :param prefix: the new prefix 
        :Exceptions:
            - `SYNTAX_ERR`: (TODO)
              Raised if the specified CSS string value has a syntax error and
              is unparsable.
            - `NO_MODIFICATION_ALLOWED_ERR`: CSSRule)
              Raised if this rule is readonly.
        """
        self._checkReadonly()
        if not prefix:
            prefix = u''
        else:        
            tokenizer = self._tokenize2(prefix)
            prefixtoken = self._nexttoken(tokenizer, None)
            if not prefixtoken or self._type(prefixtoken) != self._prods.IDENT:
                self._log.error(u'CSSNamespaceRule: No valid prefix "%s".' %
                    self._valuestr(prefix),
                    error=xml.dom.SyntaxErr)
                return
            else:
                prefix = self._tokenvalue(prefixtoken)
        # update seg
        for i, x in enumerate(self.seq):
            if x == self._prefix:
                self.seq[i] = prefix
                break
        else:
            self.seq[0] = prefix # put prefix at the beginning!
        # set new prefix
        oldprefix = self._prefix
        self._prefix = prefix
        
        # update prefixes in stylesheet
        if self.parentStyleSheet:
            try:
                self.parentStyleSheet.namespaces[prefix] = \
                        self.parentStyleSheet.namespaces[oldprefix]
                del self.parentStyleSheet.namespaces[oldprefix]
            except KeyError:
                self.parentStyleSheet.namespaces[prefix] = self._namespaceURI

    prefix = property(lambda self: self._prefix, _setPrefix,
        doc="Prefix used for the defined namespace.")

    def _setParentStyleSheet(self, parentStyleSheet):
        self._parentStyleSheet = parentStyleSheet
        if parentStyleSheet and self._namespaceURI is not None:
            self.parentStyleSheet.namespaces[self.prefix] = self._namespaceURI

    parentStyleSheet = property(lambda self: self._parentStyleSheet, 
                                _setParentStyleSheet,
                                doc=u"Containing CSSStyleSheet.")

    def _getCssText(self):
        """
        returns serialized property cssText
        """
        return cssutils.ser.do_CSSNamespaceRule(self)

    def _setCssText(self, cssText):
        """
        DOMException on setting

        :param cssText: initial value for this rules cssText which is parsed
        :Exceptions:
            - `HIERARCHY_REQUEST_ERR`: (CSSStylesheet)
              Raised if the rule cannot be inserted at this point in the
              style sheet.
            - `INVALID_MODIFICATION_ERR`: (self)
              Raised if the specified CSS string value represents a different
              type of rule than the current one.
            - `NO_MODIFICATION_ALLOWED_ERR`: (CSSRule)
              Raised if the rule is readonly.
            - `SYNTAX_ERR`: (self)
              Raised if the specified CSS string value has a syntax error and
              is unparsable.
        """
        super(CSSNamespaceRule, self)._setCssText(cssText)
        tokenizer = self._tokenize2(cssText)
        attoken = self._nexttoken(tokenizer, None)
        if not attoken or self._type(attoken) != self._prods.NAMESPACE_SYM:
            self._log.error(u'CSSNamespaceRule: No CSSNamespaceRule found: %s' %
                self._valuestr(cssText),
                error=xml.dom.InvalidModificationErr)
        else:
            # for closures: must be a mutable
            new = {
                   'keyword': self._tokenvalue(attoken),
                   'prefix': u'',
                   'uri': None,
                   'valid': True
                   }

            def _ident(expected, seq, token, tokenizer=None):
                # the namespace prefix, optional
                if 'prefix or uri' == expected:
                    new['prefix'] = self._tokenvalue(token)
                    seq.append(new['prefix'])
                    return 'uri'
                else:
                    new['valid'] = False
                    self._log.error(
                        u'CSSNamespaceRule: Unexpected ident.', token)
                    return expected

            def _string(expected, seq, token, tokenizer=None):
                # the namespace URI as a STRING
                if expected.endswith('uri'):
                    new['uri'] = self._tokenvalue(token)[1:-1] # "uri" or 'uri'
                    seq.append(new['uri'])
                    return ';'

                else:
                    new['valid'] = False
                    self._log.error(
                        u'CSSNamespaceRule: Unexpected string.', token)
                    return expected

            def _uri(expected, seq, token, tokenizer=None):
                # the namespace URI as URI which is DEPRECATED
                if expected.endswith('uri'):
                    uri = self._tokenvalue(token)[4:-1].strip() # url(uri)
                    if uri[0] == uri[-1] == '"' or\
                       uri[0] == uri[-1] == "'":
                        uri = uri[1:-1]
                    self._log.warn(
                        u'CSSNamespaceRule: Found namespace definition with url(uri), this may be deprecated in the future, use string format "uri" instead.',
                        token, error = None, neverraise=True)
                    new['uri'] = uri
                    seq.append(new['uri'])
                    return ';'
                else:
                    new['valid'] = False
                    self._log.error(
                        u'CSSNamespaceRule: Unexpected URI.', token)
                    return expected

            def _char(expected, seq, token, tokenizer=None):
                # final ;
                val = self._tokenvalue(token)
                if ';' == expected and u';' == val:
                    return 'EOF'
                else:
                    new['valid'] = False
                    self._log.error(
                        u'CSSNamespaceRule: Unexpected char.', token)
                    return expected

            # "NAMESPACE_SYM S* [namespace_prefix S*]? [STRING|URI] S* ';' S*"
            newseq = []
            valid, expected = self._parse(expected='prefix or uri',
                seq=newseq, tokenizer=tokenizer,
                productions={'IDENT': _ident,
                             'STRING': _string,
                             'URI': _uri,
                             'CHAR': _char})

            # valid set by parse
            valid = valid and new['valid']

            # post conditions
            if not new['uri']:
                valid = False
                self._log.error(u'CSSNamespaceRule: No namespace URI found: %s' %
                    self._valuestr(cssText))

            if expected != 'EOF':
                valid = False
                self._log.error(u'CSSNamespaceRule: No ";" found: %s' %
                    self._valuestr(cssText))

            # set all
            self.valid = valid
            if valid:
                self.atkeyword = new['keyword']
                self._prefix = new['prefix']
                self.namespaceURI = new['uri']
                self.seq = newseq

    cssText = property(fget=_getCssText, fset=_setCssText,
        doc="(DOM attribute) The parsable textual representation.")

    def __repr__(self):
        return "cssutils.css.%s(namespaceURI=%r, prefix=%r)" % (
                self.__class__.__name__, self.namespaceURI, self.prefix)

    def __str__(self):
        return "<cssutils.css.%s object namespaceURI=%r prefix=%r at 0x%x>" % (
                self.__class__.__name__, self.namespaceURI, self.prefix, id(self))
