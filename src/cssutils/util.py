"""base classes for css and stylesheets packages
"""
__all__ = []
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

from itertools import ifilter
import re
import types
import xml.dom
import cssutils
from tokenize2 import Tokenizer

class ListSeq(object):
    """
    (EXPERIMENTAL)
    A base class used for list classes like css.SelectorList or 
    stylesheets.MediaList

    adds list like behaviour running on inhering class' property ``seq``
    
    - item in x => bool
    - len(x) => integer
    - get, set and del x[i]
    - for item in x
    - append(item)
    
    some methods must be overwritten in inheriting class
    """
    def __init__(self):
        self.seq = [] # does not need to use ``Seq`` as simple list only

    def __contains__(self, item):
        return item in self.seq

    def __delitem__(self, index):
        del self.seq[index]

    def __getitem__(self, index):
        return self.seq[index]

    def __iter__(self):
        def gen():
            for x in self.seq:
                yield x
        return gen()

    def __len__(self):
        return len(self.seq)

    def __setitem__(self, index, item):
        "must be overwritten"
        raise NotImplementedError

    def append(self, item):
        "must be overwritten"
        raise NotImplementedError


class Base(object):
    """
    Base class for most CSS and StyleSheets classes
    
    **Superceded by Base2 which is used for new seq handling class.** 
    See cssutils.util.Base2

    Contains helper methods for inheriting classes helping parsing
    
    ``_normalize`` is static as used by Preferences.
    """
    __tokenizer2 = Tokenizer()
    _log = cssutils.log
    _prods = cssutils.tokenize2.CSSProductions

    # for more on shorthand properties see 
    # http://www.dustindiaz.com/css-shorthand/
    # format: shorthand: [(propname, mandatorycheck?)*]
    _SHORTHANDPROPERTIES = {
            u'background': [],
            u'border': [],
            u'border-left': [], 
            u'border-right': [],
            u'border-top': [], 
            u'border-bottom': [],
            u'border-color': [], 
            u'border-style': [], 
            u'border-width': [],
            u'cue': [],
            u'font': [],
#                      [('font-weight', True), 
#                      ('font-size', True),
#                      ('line-height', False), 
#                      ('font-family', True)],
            u'list-style': [],
            u'margin': [],
            u'outline': [],
            u'padding': [],
            u'pause': []
            }

    # simple escapes, all non unicodes
    __escapes = re.compile(ur'(\\[^0-9a-fA-F])').sub
    # all unicode (see cssproductions "unicode")
    __unicodes = re.compile(ur'\\[0-9a-fA-F]{1,6}[\t|\r|\n|\f|\x20]?').sub

    @staticmethod
    def _normalize(x):
        """
        normalizes x, namely:

        - remove any \ before non unicode sequences (0-9a-zA-Z) so for 
          x=="c\olor\" return "color" (unicode escape sequences should have
          been resolved by the tokenizer already)
        - lowercase
        """
        if x:
            def removeescape(matchobj):
                return matchobj.group(0)[1:]
            x = Base.__escapes(removeescape, x)
            return x.lower()        
        else:
            return x

    def _checkReadonly(self):
        "raises xml.dom.NoModificationAllowedErr if rule/... is readonly"
        if hasattr(self, '_readonly') and self._readonly:
            raise xml.dom.NoModificationAllowedErr(
                u'%s is readonly.' % self.__class__)
            return True
        return False

    def _splitNamespacesOff(self, text_namespaces_tuple):
        """
        returns tuple (text, dict-of-namespaces) or if no namespaces are 
        in cssText returns (cssText, {})
        
        used in Selector, SelectorList, CSSStyleRule, CSSMediaRule and
        CSSStyleSheet
        """
        if isinstance(text_namespaces_tuple, tuple):
            return text_namespaces_tuple[0], _SimpleNamespaces(
                                                    text_namespaces_tuple[1])
        else:
            return text_namespaces_tuple, _SimpleNamespaces()

    def _tokenize2(self, textortokens):
        """
        returns tokens of textortokens which may already be tokens in which
        case simply returns input
        """
        if not textortokens:
            return None
        elif isinstance(textortokens, basestring):
            # needs to be tokenized
            return self.__tokenizer2.tokenize(
                 textortokens)
        elif types.GeneratorType == type(textortokens):
            # already tokenized
            return textortokens
        elif isinstance(textortokens, tuple):
            # a single token (like a comment)
            return [textortokens]
        else:
            # already tokenized but return generator
            return (x for x in textortokens)

    def _nexttoken(self, tokenizer, default=None):
        "returns next token in generator tokenizer or the default value"
        try:
            return tokenizer.next()
        except (StopIteration, AttributeError):
            return default

    def _type(self, token):
        "returns type of Tokenizer token"
        if token:
            return token[0]
        else:
            return None

    def _tokenvalue(self, token, normalize=False):
        "returns value of Tokenizer token"
        if token and normalize:
            return Base._normalize(token[1])
        elif token:
            return token[1]
        else:
            return None

    def _tokensupto2(self,
                     tokenizer,
                     starttoken=None,
                     blockstartonly=False,
                     blockendonly=False,
                     mediaendonly=False,
                     semicolon=False,
                     propertynameendonly=False,
                     propertyvalueendonly=False,
                     propertypriorityendonly=False,
                     selectorattendonly=False,
                     funcendonly=False,
                     listseponly=False, # ,
                     keepEnd=True,
                     keepEOF=True):
        """
        returns tokens upto end of atrule and end index
        end is defined by parameters, might be ; } ) or other

        default looks for ending "}" and ";"
        """
        ends = u';}'
        brace = bracket = parant = 0 # {}, [], ()

        if blockstartonly: # {
            ends = u'{'
            brace = -1 # set to 0 with first {
        elif blockendonly: # }
            ends = u'}'
            brace = 1
        elif mediaendonly: # }
            ends = u'}'
            brace = 1 # rules } and mediarules }
        elif semicolon:
            ends = u';'
        elif propertynameendonly: # : and ; in case of an error
            ends = u':;'
        elif propertyvalueendonly: # ; or !important
            ends = (u';', u'!')
        elif propertypriorityendonly: # ;
            ends = u';'
        elif selectorattendonly: # ]
            ends = u']'
            if starttoken and self._tokenvalue(starttoken) == u'[':
                bracket = 1
        elif funcendonly: # )
            ends = u')'
            parant = 1
        elif listseponly: # ,
            ends = u','

        resulttokens = []
        if starttoken:
            resulttokens.append(starttoken)
        if tokenizer:
            for token in tokenizer:
                typ, val, line, col = token
                if 'EOF' == typ:
                    if keepEOF and keepEnd:
                        resulttokens.append(token)
                    break
                if u'{' == val: 
                    brace += 1
                elif u'}' == val: 
                    brace -= 1
                elif u'[' == val: 
                    bracket += 1
                elif u']' == val: 
                    bracket -= 1
                # function( or single (
                elif u'(' == val or \
                     Base._prods.FUNCTION == typ: 
                    parant += 1
                elif u')' == val: 
                    parant -= 1
                    
                if val in ends and (brace == bracket == parant == 0):
                    if keepEnd:
                        resulttokens.append(token)
                    break
                else:
                    resulttokens.append(token)

        return resulttokens

    def _valuestr(self, t):
        """
        returns string value of t (t may be a string, a list of token tuples
        or a single tuple in format (type, value, line, col).
        Mainly used to get a string value of t for error messages.
        """
        if not t:
            return u''
        elif isinstance(t, basestring):
            return t
        else:
            return u''.join([x[1] for x in t])

    def __adddefaultproductions(self, productions):
        """
        adds default productions if not already present, used by 
        _parse only
        
        each production should return the next expected token
        normaly a name like "uri" or "EOF"
        some have no expectation like S or COMMENT, so simply return
        the current value of self.__expected
        """
        def ATKEYWORD(expected, seq, token, tokenizer=None):
            "TODO: add default impl for unexpected @rule?"
            return expected

        def COMMENT(expected, seq, token, tokenizer=None):
            "default implementation for COMMENT token adds CSSCommentRule"
            seq.append(cssutils.css.CSSComment([token]))
            return expected

        def S(expected, seq, token, tokenizer=None):
            "default implementation for S token, does nothing"
            return expected

        def EOF(expected=None, seq=None, token=None, tokenizer=None):
            "default implementation for EOF token"
            return 'EOF'

        p = {'ATKEYWORD': ATKEYWORD,
             'COMMENT': COMMENT,
             'S': S,
             'EOF': EOF # only available if fullsheet
             }
        p.update(productions)
        return p

    def _parse(self, expected, seq, tokenizer, productions, default=None):
        """
        puts parsed tokens in seq by calling a production with
            (seq, tokenizer, token)

        expected
            a name what token or value is expected next, e.g. 'uri'
        seq
            to add rules etc to
        tokenizer
            call tokenizer.next() to get next token
        productions
            callbacks {tokentype: callback}
        default
            default callback if tokentype not in productions

        returns (wellformed, expected) which the last prod might have set
        """
        wellformed = True
        if tokenizer:
            prods = self.__adddefaultproductions(productions)
            for token in tokenizer:
                p = prods.get(token[0], default)
                if p:
                    expected = p(expected, seq, token, tokenizer)
                else:
                    wellformed = False
                    self._log.error(u'Unexpected token (%s, %s, %s, %s)' % token)
                    
        return wellformed, expected


class Seq(object):
    """
    property seq of Base2 inheriting classes, holds a list of Item objects.
    
    used only by Selector for now
    
    is normally readonly, only writable during parsing
    """
    def __init__(self, readonly=True):
        """
        only way to write to a Seq is to initialize it with new items
        each itemtuple has (value, type, line) where line is optional
        """
        self.__seq = []
        self._readonly = readonly
        
    def __delitem__(self, i):
        del self.__seq[i]

    def __getitem__(self, i):
        return self.__seq[i]

    def __iter__(self):
        return iter(self.__seq)

    def __len__(self):
        return len(self.__seq)
        
    def append(self, val, typ, line=None):
        "if not readonly add new Item()"
        if self._readonly:
            raise AttributeError('Seq is readonly.')
        else:
            self.__seq.append(Item(val, typ, line))

    def replace(self, index=-1, val=None, typ=None, line=None):
        """
        if not readonly replace Item at index with new Item or
        simply replace value or type
        """
        if self._readonly:
            raise AttributeError('Seq is readonly.')
        else:
            self.__seq[index] = Item(val, typ, line)

    def __repr__(self):
        "returns a repr same as a list of tuples of (value, type)"
        return u'cssutils.%s.%s([\n    %s])' % (self.__module__, 
                                          self.__class__.__name__, 
            u',\n    '.join([u'(%r, %r)' % (item.type, item.value)
                          for item in self.__seq]
            ))
    def __str__(self):
        return "<cssutils.%s.%s object length=%r at 0x%x>" % (
                self.__module__, self.__class__.__name__, len(self), id(self))

class Item(object):
    """
    an item in the seq list of classes (successor to tuple items in old seq)
    
    each item has attributes:
    
    type
        a sematic type like "element", "attribute"
    value
        the actual value which may be a string, number etc or an instance
        of e.g. a CSSComment
    *line*
        **NOT IMPLEMENTED YET, may contain the line in the source later**
    """
    def __init__(self, value, type, line=None):
        self.__value = value
        self.__type = type
        self.__line = line

    type = property(lambda self: self.__type)
    value = property(lambda self: self.__value)
    line = property(lambda self: self.__line)
    
    def __repr__(self):
        return "cssutils.%s.%s(value=%r, type=%r, line=%r)" % (
                self.__module__, self.__class__.__name__, 
                self.__value, self.__type, self.__line)

class Base2(Base):
    """
    Base class for new seq handling, used by Selector for now only
    """
    def __init__(self):
        self._seq = Seq()

    def _setSeq(self, newseq):
        """
        sets newseq and makes it readonly
        """
        newseq._readonly = True
        self._seq = newseq

    seq = property(fget=lambda self: self._seq, 
                   fset=_setSeq, 
                   doc="seq for most classes")
    
    def _tempSeq(self, readonly=False):
        "get a writeable Seq() which is added later"  
        return Seq(readonly=readonly)
    

class Deprecated(object):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    It accepts a single paramter ``msg`` which is shown with the warning.
    It should contain information which function or method to use instead.
    """
    def __init__(self, msg):
        self.msg = msg

    def __call__(self, func):
        def newFunc(*args, **kwargs):
            import warnings
            warnings.warn("Call to deprecated method %r. %s" %
                            (func.__name__, self.msg),
                            category=DeprecationWarning,
                            stacklevel=2)
            return func(*args, **kwargs)
        newFunc.__name__ = func.__name__
        newFunc.__doc__ = func.__doc__
        newFunc.__dict__.update(func.__dict__)
        return newFunc
    
class _Namespaces(object):
    """
    A dictionary like wrapper for @namespace rules used in a CSSStyleSheet.
    Works on effective namespaces, so e.g. if::
    
        @namespace p1 "uri";
        @namespace p2 "uri";
    
    only the second rule is effective and kept.
    
    namespaces
        a dictionary {prefix: namespaceURI} containing the effective namespaces 
        only. These are the latest set in the CSSStyleSheet.
    parentStyleSheet
        the parent CSSStyleSheet
    """
    def __init__(self, parentStyleSheet, *args):
        "no initial values are set, only the relevant sheet is"
        self.parentStyleSheet = parentStyleSheet
    
    def __contains__(self, prefix):
        return prefix in self.namespaces
    
    def __delitem__(self, prefix):
        "deletes CSSNamespaceRule(s) with rule.prefix == prefix"
        delrule = self.__findrule(prefix)
        for i, rule in enumerate(ifilter(lambda r: r.type == r.NAMESPACE_RULE, 
                            self.parentStyleSheet.cssRules)):
            if rule == delrule:
                self.parentStyleSheet.deleteRule(i)
                return

        raise xml.dom.NamespaceErr('Prefix %r not found.' % prefix)
            
    def __getitem__(self, prefix):
        try:
            return self.namespaces[prefix]
        except KeyError, e:
            raise xml.dom.NamespaceErr('Prefix %r not found.' % prefix)
    
    def __iter__(self):
        return self.namespaces.__iter__()
    
    def __len__(self):
        return len(self.namespaces)

    def __setitem__(self, prefix, namespaceURI):
        "replaces prefix or sets new rule, may raise NoModificationAllowedErr"
        rule = self.__findrule(prefix)
        if not rule:
            self.parentStyleSheet.insertRule(cssutils.css.CSSNamespaceRule(
                                                    prefix=prefix,
                                                    namespaceURI=namespaceURI),
                                  inOrder=True)
        else:
            if prefix in self.namespaces:
                rule.namespaceURI = namespaceURI # raises NoModificationAllowedErr
            if namespaceURI in self.namespaces.values():
                rule.prefix = prefix

    def __findrule(self, prefix):
        # returns namespace rule where prefix == key
        for rule in ifilter(lambda r: r.type == r.NAMESPACE_RULE, 
                            reversed(self.parentStyleSheet.cssRules)):
            if rule.prefix == prefix:
                return rule

    def __getNamespaces(self):
        namespaces = {}
        for rule in ifilter(lambda r: r.type == r.NAMESPACE_RULE, 
                            reversed(self.parentStyleSheet.cssRules)):
            if rule.namespaceURI not in namespaces.values():
                namespaces[rule.prefix] = rule.namespaceURI
        return namespaces
        
    namespaces = property(__getNamespaces, 
        doc=u'Holds only effetive @namespace rules in self.parentStyleSheets'
             '@namespace rules.')
    
#    def deleteByNamespaceURI(self, namespaceURI):
#        """
#        Deletes CSSNamespaceRule(s) with rule.namespaceURI == namespaceURI        
#        
#        Raises xml.dom.NamespaceErr if the namespace is in use but all 
#        namespacerules which have been set with the same uri are boiled down to
#        the effective one
#        """
#        deleted = False
#        i = 0
#        rules = self.parentStyleSheet.cssRules
#        while i < len(rules):
#            if rules[i].type == rules[i].NAMESPACE_RULE and \
#               rules[i].namespaceURI == namespaceURI:
#                self.parentStyleSheet.deleteRule(i)
#                deleted = True
#            else:
#                i += 1
#                
#        if not deleted:
#            raise KeyError('Namespace URI "%s" not present in style sheet.' % 
#                           namespaceURI)
                
    def get(self, prefix, default):
        return self.namespaces.get(prefix, default)

    def items(self):
        return self.namespaces.items()

    def keys(self):
        return self.namespaces.keys()

    def values(self):
        return self.namespaces.values()
    
    def prefixForNamespaceURI(self, namespaceURI):
        """
        returns effective prefix for given namespaceURI or raises IndexError 
        if this cannot be found"""
        for prefix, uri in self.namespaces.items():
            if uri == namespaceURI:
                return prefix
        raise IndexError(u'NamespaceURI %r not found.' % namespaceURI)

    def __str__(self):
        return u"<cssutils.util.%s object parentStyleSheet=%r namespaces=%r "\
               u"at 0x%x>" % (
                self.__class__.__name__, str(self.parentStyleSheet), 
                self.namespaces, id(self))

  
class _SimpleNamespaces(_Namespaces):
    """
    namespaces used in objects like Selector as long as they are not connected
    to a CSSStyleSheet
    """
    def __init__(self, *args):
        self.__namespaces = dict(*args)   
    
    def __setitem__(self, prefix, namespaceURI):
        self.__namespaces[prefix] = namespaceURI
            
    namespaces = property(lambda self: self.__namespaces, 
                          doc=u'Dict Wrapper for self.sheets @namespace rules.')
           
    def __str__(self):
        return u"<cssutils.util.%s object namespaces=%r at 0x%x>" % (
                self.__class__.__name__, self.namespaces, id(self))
