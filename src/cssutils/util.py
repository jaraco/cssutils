"""base classes for css and stylesheets packages
"""
__all__ = []
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a1, SVN revision $LastChangedRevision$'

import xml.dom

import cssutils

  
class Base(object):
    """
    Base class for
    - css.CSSRule
    - css.Selectors
    - stylesheets.MediaList
    """
    def __init__(self):
        """
        adds tokenizer, log and ttypes to instances
        """
        self._tokenizer = cssutils.tokenize.Tokenizer()
        self._log = self._tokenizer.log
        self._ttypes = self._tokenizer.ttypes

    
    def _checkReadonly(self):
        "raises xml.dom.NoModificationAllowedErr if rule/... is readonly"
        if hasattr(self, '_readonly') and self._readonly:
            raise xml.dom.NoModificationAllowedErr(
                u'%s is readonly.' % self.__class__)


    def _normalize(self, x):
        """
        normalizes x, used in Token for normalizedvalue and
        CSSStyleDeclaration currently

        uses util.normalize function
        """
        return normalize(x)
    
    
    def _tokenize(self, textortokens):
        """
        helper
        returns tokens (of textortokens)
        """
        if isinstance(textortokens, list):
            tokens = textortokens # already tokenized
        elif isinstance(textortokens, cssutils.token.Token):
            tokens = [textortokens] # comment is a single token
        elif isinstance(textortokens, basestring):
            tokens = self._tokenizer.tokenize(textortokens) # already string
        else:
            if textortokens is not None:
                textortokens = unicode(textortokens)
            tokens = self._tokenizer.tokenize(textortokens)
        return tokens


    def _valuestr(self, t):
        """
        returns string value of t (t may be string of tokenlist)
        """
        if isinstance(t, basestring):
            return t
        else:
            return ''.join([x.value for x in t])


    # deprecated method
    def getFormatted(self, indent=4, offset=0):
        "DEPRECATED"
        import warnings
        warnings.warn('Use property cssText or mediaText of %s instead.' %
                      self.__class__, DeprecationWarning)
        return self.cssText

    pprint = getFormatted


def normalize(x):
    # TODO: only no simple escapes???
    return x.replace(u'\\', u'').lower()
