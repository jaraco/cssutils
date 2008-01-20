"""SelectorList is a list of CSS Selector objects.

TODO
    - ??? CSS2 gives a special meaning to the comma (,) in selectors.
        However, since it is not known if the comma may acquire other
        meanings in future versions of CSS, the whole statement should be
        ignored if there is an error anywhere in the selector, even though
        the rest of the selector may look reasonable in CSS2.

        Illegal example(s):

        For example, since the "&" is not a valid token in a CSS2 selector,
        a CSS2 user agent must ignore the whole second line, and not set
        the color of H3 to red:
"""
__all__ = ['SelectorList']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssutils
from selector import Selector

class SelectorList(cssutils.util.Base, cssutils.util.ListSeq):
    """
    (cssutils) a list of Selectors of a CSSStyleRule

    Properties
    ==========
    length: of type unsigned long, readonly
        The number of Selector elements in the list.
    parentRule: of type CSSRule, readonly
        The CSS rule that contains this declaration block or None if this
        CSSStyleDeclaration is not attached to a CSSRule.
    selectorText: of type DOMString
        The textual representation of the selector for the rule set. The
        implementation may have stripped out insignificant whitespace while
        parsing the selector.
    seq:
        A list of interwoven Selector objects and u','
    wellformed
        if this selectorlist is wellformed regarding the Selector spec
    """
    def __init__(self, selectorText=None, parentRule=None, readonly=False):
        """
        initializes SelectorList with optional selectorText
        """
        super(SelectorList, self).__init__()
        
        self.wellformed = False
        self.parentRule = parentRule
        if selectorText:
            self.selectorText = selectorText
        self._readonly = readonly

    def __prepareset(self, newSelector):
        # used by appendSelector and __setitem__
        self._checkReadonly()
        
        if not isinstance(newSelector, Selector):
            newSelector = Selector(newSelector, parentList=self)

        if newSelector.wellformed:
            newSelector.parentList = self
            return newSelector

    def __setitem__(self, index, newSelector):
        """
        overwrites ListSeq.__setitem__
        
        Any duplicate Selectors are **not** removed.
        """
        newSelector = self.__prepareset(newSelector)
        if newSelector:
            self.seq[index] = newSelector
        # TODO: remove duplicates?    
        
    def appendSelector(self, newSelector):
        """
        Append newSelector (is a string will be converted to a new
        Selector. A duplicate Selector is removed.
        
        Returns new Selector or None if newSelector is no wellformed 
        Selector.

        DOMException on setting

        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error
          and is unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this rule is readonly.
        """
        newSelector = self.__prepareset(newSelector)
        if newSelector:
            self.wellformed = True
            seq = self.seq[:]
            del self.seq[:]
            for s in seq:
                if s.selectorText != newSelector.selectorText:
                    self.seq.append(s)
            self.seq.append(newSelector)
            return newSelector

    def append(self, newSelector):
        "overwrites ListSeq.append"
        self.appendSelector(newSelector)

    length = property(lambda self: len(self),
        doc="The number of Selector elements in the list.")

    def _getSelectorText(self):
        "returns serialized format"
        return cssutils.ser.do_css_SelectorList(self)

    def _setSelectorText(self, selectorText):
        """
        selectortext
            comma-separated list of selectors

        DOMException on setting

        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error
          and is unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this rule is readonly.
        """
        self._checkReadonly()
        wellformed = True
        tokenizer = self._tokenize2(selectorText)
        newseq = []

        expected = True
        while True:
            # find all upto and including next ",", EOF or nothing
            selectortokens = self._tokensupto2(tokenizer, listseponly=True)
            if selectortokens:
                if self._tokenvalue(selectortokens[-1]) == ',':
                    expected = selectortokens.pop()
                else:
                    expected = None

                selector = Selector(selectortokens, parentList=self)
                if selector.wellformed:
                    newseq.append(selector)
                else:
                    wellformed = False
                    self._log.error(u'SelectorList: Invalid Selector: %s' %
                                    self._valuestr(selectortokens))
            else:
                break

        # post condition
        if u',' == expected:
            wellformed = False
            self._log.error(u'SelectorList: Cannot end with ",": %r' %
                            self._valuestr(selectorText))
        elif expected:
            wellformed = False
            self._log.error(u'SelectorList: Unknown Syntax: %r' %
                            self._valuestr(selectorText))
        if wellformed:
            self.wellformed = wellformed
            self.seq = newseq
#            for selector in newseq:
#                 self.appendSelector(selector)

    def _setParentRule(self, parentRule):
        self._parentRule = parentRule

    parentRule = property(lambda self: self._parentRule, _setParentRule,
        doc="(DOM) The CSS rule that contains this SelectorList or\
        None if this SelectorList is not attached to a CSSRule.")
    
    selectorText = property(_getSelectorText, _setSelectorText,
        doc="""(cssutils) The textual representation of the selector for
            a rule set.""")
    
    def __repr__(self):
        return "cssutils.css.%s(selectorText=%r)" % (
                self.__class__.__name__, self.selectorText)

    def __str__(self):
        return "<cssutils.css.%s object selectorText=%r at 0x%x>" % (
                self.__class__.__name__, self.selectorText, id(self))

    def __getusedprefixes(self):
        """
        used internally to check is namespaces in CSSStyleSheet are
        changing
        """
        prefixes = set()
        for s in self:
            prefixes.update(s._usedprefixes)
        return prefixes
    
    _usedprefixes = property(__getusedprefixes, doc='INTERNAL USE')
