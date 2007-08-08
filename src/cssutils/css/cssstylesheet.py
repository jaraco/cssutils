"""
CSSStyleSheet implements DOM Level 2 CSS CSSStyleSheet.

Partly also:
    http://www.w3.org/TR/2006/WD-css3-namespace-20060828/

TODO:
    - ownerRule and ownerNode
"""
__all__ = ['CSSStyleSheet']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a5 $LastChangedRevision$'

import xml.dom

import cssutils.stylesheets
import cssutils.tokenize


class CSSStyleSheet(cssutils.stylesheets.StyleSheet):
    """
     The CSSStyleSheet interface is a concrete interface used to represent
     a CSS style sheet i.e., a style sheet whose content type is
     "text/css".

    Properties
    ==========
    cssRules: of type CSSRuleList, (DOM readonly)
        The list of all CSS rules contained within the style sheet. This
        includes both rule sets and at-rules.
    namespaces: set
        A set of declared namespaces via @namespace rules. Each
        CSSStyleRule is checked if it uses additional prefixes which are
        not declared. If they are "invalidated".
    ownerRule: of type CSSRule, readonly
        If this style sheet comes from an @import rule, the ownerRule
        attribute will contain the CSSImportRule. In that case, the
        ownerNode attribute in the StyleSheet interface will be None. If
        the style sheet comes from an element or a processing instruction,
        the ownerRule attribute will be None and the ownerNode attribute
        will contain the Node.

    Inherits properties from stylesheet.StyleSheet

    Format
    ======
    stylesheet
      : [ CHARSET_SYM S* STRING S* ';' ]?
        [S|CDO|CDC]* [ import [S|CDO|CDC]* ]*
        [ namespace [S|CDO|CDC]* ]* # according to @namespace WD
        [ [ ruleset | media | page ] [S|CDO|CDC]* ]*
    """
    type = 'text/css'

    def __init__(self, href=None, media=None,
                 title=u'', disabled=None,
                 ownerNode=None, parentStyleSheet=None,
                 readonly=False):

        super(CSSStyleSheet, self).__init__(
                self.type, href, media, title, disabled,
                ownerNode, parentStyleSheet)

        self.cssRules = cssutils.css.CSSRuleList()
        self.namespaces = set()
        self._readonly = readonly


    def __checknamespaces(self, stylerule, namespaces):
        """
        checks if all namespaces used in stylerule have been declared
        """
        notdeclared = set()
        for s in stylerule.selectorList:
            for prefix in s.namespaces:
                if not prefix in namespaces:
                    notdeclared.add(prefix)
        return notdeclared


    def _getCssText(self):
        return cssutils.ser.do_stylesheet(self)

    def _setCssText(self, cssText):
        """
        (cssutils)
        Parses cssText and overwrites the whole stylesheet.

        cssText
            textual text to set

        DOMException on setting

        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if the rule is readonly.
        - SYNTAX_ERR:
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        - NAMESPACE_ERR:
          If a namespace prefix is found which is not declared.
        """
        self._checkReadonly()

        tokens = self._tokenize(cssText, _fullSheet=True)

        newcssRules = cssutils.css.CSSRuleList()
        newnamespaces = set()

        # @charset only once at beginning
        if tokens and tokens[0].type == self._ttypes.CHARSET_SYM:
            charsetruletokens, endi = self._tokensupto(tokens)
            charsetrule = cssutils.css.CSSCharsetRule()
            charsetrule.cssText = charsetruletokens
            newcssRules.append(charsetrule)
            i = endi + 1 # ?
        else:
            i = 0
        expected = '@import' # @namespace | any
        imax = len(tokens)
        while i < imax:
            t = tokens[i]

            if t.type == self._ttypes.EOF:
                break

            # ignore
            if t.type in (self._ttypes.S, self._ttypes.CDO, self._ttypes.CDC):
                pass

            # unexpected: } ;
            elif t.type in (self._ttypes.SEMICOLON,
                            self._ttypes.LBRACE, self._ttypes.RBRACE):
                self._log.error(u'CSSStyleSheet: Syntax Error',t)

            # simply add
            elif self._ttypes.COMMENT == t.type:
                newcssRules.append(cssutils.css.CSSComment(t))

            # @charset only at beginning
            elif self._ttypes.CHARSET_SYM == t.type:
                atruletokens, endi = self._tokensupto(tokens[i:])
                i += endi
                self._log.error(u'CSSStylesheet: CSSCharsetRule only allowed at beginning of stylesheet.',
                    t, xml.dom.HierarchyRequestErr)

            # @import before any StyleRule and @rule except @charset
            elif self._ttypes.IMPORT_SYM == t.type:
                atruletokens, endi = self._tokensupto(tokens[i:])
                if expected == '@import':
                    atrule = cssutils.css.CSSImportRule()
                    atrule.cssText = atruletokens
                    newcssRules.append(atrule)
                else:
                    self._log.error(
                        u'CSSStylesheet: CSSImportRule not allowed here.',
                        t, xml.dom.HierarchyRequestErr)
                i += endi

            # @namespace before any StyleRule and
            #  before @rule except @charset, @import
            elif self._ttypes.NAMESPACE_SYM == t.type:
                atruletokens, endi = self._tokensupto(tokens[i:])
                if expected in ('@import', '@namespace'):
                    atrule = cssutils.css.CSSNamespaceRule()
                    atrule.cssText = atruletokens
                    newcssRules.append(atrule)
                    newnamespaces.add(atrule.prefix)
                else:
                    self._log.error(
                        u'CSSStylesheet: CSSNamespaceRule not allowed here.',
                        t, xml.dom.HierarchyRequestErr)
                i += endi
                expected = '@namespace' # now no @import anymore!

            # @media
            elif self._ttypes.MEDIA_SYM == t.type:
                atruletokens, endi = self._tokensupto(tokens[i:])
                atrule = cssutils.css.CSSMediaRule()
                atrule.cssText = atruletokens
                newcssRules.append(atrule)
                i += endi
                expected = 'any'

            # @page
            elif self._ttypes.PAGE_SYM == t.type:
                atruletokens, endi = self._tokensupto(tokens[i:])
                atrule = cssutils.css.CSSPageRule()
                atrule.cssText = atruletokens
                newcssRules.append(atrule)
                i += endi
                expected = 'any'

            # @unknown, insert in any case (but after @charset)
            elif self._ttypes.ATKEYWORD == t.type:
                atruletokens, endi = self._tokensupto(tokens[i:])
                atrule = cssutils.css.CSSUnknownRule()
                atrule.cssText = atruletokens
                newcssRules.append(atrule)
                i += endi

            else: # probable StyleRule
                ruletokens, endi = self._tokensupto(
                    tokens[i:], blockendonly=True)
                rule = cssutils.css.CSSStyleRule()
                rule.cssText = ruletokens
                notdeclared = self.__checknamespaces(rule, newnamespaces)
                if notdeclared:
                    rule.valid = False
                    self._log.error(
                        u'CSSStylesheet: CSSStyleRule uses undeclared namespace prefixes: %s.' %
                        ', '.join(notdeclared),
                        t, xml.dom.NamespaceErr)
                newcssRules.append(rule)
                i += endi
                expected = 'any'

            i += 1

        self.cssRules = newcssRules
        for r in self.cssRules:
            r.parentStyleSheet = self
        self.namespaces = newnamespaces

    cssText = property(_getCssText, _setCssText,
            "(cssutils) a textual representation of the stylesheet")


    def deleteRule(self, index):
        """
        Used to delete a rule from the style sheet.

        index
            of the rule to remove in the StyleSheet's rule list

        DOMException

        - INDEX_SIZE_ERR: (self)
          Raised if the specified index does not correspond to a rule in
          the style sheet's rule list.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this style sheet is readonly.
        """
        self._checkReadonly()

        try:
            self.cssRules[index].parentStyleSheet = None # detach
            del self.cssRules[index] # delete from StyleSheet
        except IndexError:
            raise xml.dom.IndexSizeErr(
                u'CSSStyleSheet: %s is not a valid index in the rulelist of length %i' % (
                index, self.cssRules.length))


    def insertRule(self, rule, index=None):
        """
        Used to insert a new rule into the style sheet. The new rule now
        becomes part of the cascade.

        Rule may be a string or a valid CSSRule.

        rule
            a parsable DOMString (cssutils: or Rule object)
        index
            of the rule before the new rule will be inserted.
            If the specified index is equal to the length of the
            StyleSheet's rule collection, the rule will be added to the end
            of the style sheet.
            If index is not given or None rule will be appended to rule
            list.

        returns the index within the stylesheet's rule collection

        DOMException

        - HIERARCHY_REQUEST_ERR: (self)
          Raised if the rule cannot be inserted at the specified index
          e.g. if an @import rule is inserted after a standard rule set
          or other at-rule.
        - INDEX_SIZE_ERR: (not raised at all)
          Raised if the specified index is not a valid insertion point.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this style sheet is readonly.
        - SYNTAX_ERR: (rule)
          Raised if the specified rule has a syntax error and is
          unparsable.
        """
        self._checkReadonly()

        # check position
        if index is None:
            index = len(self.cssRules)
        elif index < 0 or index > self.cssRules.length:
            raise xml.dom.IndexSizeErr(
                u'CSSStyleSheet: Invalid index %s for CSSRuleList with a length of %s.' % (
                    index, self.cssRules.length))

        # parse
        if isinstance(rule, basestring):
            tempsheet = CSSStyleSheet()
            tempsheet.cssText = rule
            if len(tempsheet.cssRules) != 1 or (tempsheet.cssRules and
             not isinstance(tempsheet.cssRules[0], cssutils.css.CSSRule)):
                self._log.error(u'CSSStyleSheet: Invalid Rule: %s' % rule)
                return
            rule = tempsheet.cssRules[0]
        elif not isinstance(rule, cssutils.css.CSSRule):
            self._log.error(u'CSSStyleSheet: Not a CSSRule: %s' % rule)
            return

        # CHECK HIERARCHY
        # @charset
        if isinstance(rule, cssutils.css.CSSCharsetRule):
            if index != 0 or (self.cssRules and
             isinstance(self.cssRules[0], cssutils.css.CSSCharsetRule)):
                self._log.error(
                    u'CSSStylesheet: @charset only allowed once at the beginning of a stylesheet.',
                    error=xml.dom.HierarchyRequestErr)
                return
            else:
                self.cssRules.insert(index, rule)
                rule.parentStyleSheet = self

        # @unknown or comment
        elif isinstance(rule, cssutils.css.CSSUnknownRule) or \
           isinstance(rule, cssutils.css.CSSComment):
            if index == 0 and self.cssRules and \
             isinstance(self.cssRules[0], cssutils.css.CSSCharsetRule):
                self._log.error(
                    u'CSSStylesheet: @charset must be the first rule.',
                    error=xml.dom.HierarchyRequestErr)
                return
            else:
                self.cssRules.insert(index, rule)
                rule.parentStyleSheet = self

        # @import
        elif isinstance(rule, cssutils.css.CSSImportRule):
            # after @charset
            if index == 0 and self.cssRules and \
               isinstance(self.cssRules[0], cssutils.css.CSSCharsetRule):
                self._log.error(
                    u'CSSStylesheet: Found @charset at index 0.',
                    error=xml.dom.HierarchyRequestErr)
                return
            # before @namespace, @media and stylerule
            for r in self.cssRules[:index]:
                if isinstance(r, cssutils.css.CSSNamespaceRule) or \
                   isinstance(r, cssutils.css.CSSMediaRule) or \
                   isinstance(r, cssutils.css.CSSPageRule) or \
                   isinstance(r, cssutils.css.CSSStyleRule):
                    self._log.error(
                        u'CSSStylesheet: Found @namespace, @media, @page or StyleRule before index %s.' %
                        index,
                        error=xml.dom.HierarchyRequestErr)
                    return
            self.cssRules.insert(index, rule)
            rule.parentStyleSheet = self

        # @namespace
        elif isinstance(rule, cssutils.css.CSSNamespaceRule):
            # after @charset and @import
            for r in self.cssRules[index:]:
                if isinstance(r, cssutils.css.CSSCharsetRule) or \
                   isinstance(r, cssutils.css.CSSImportRule):
                    self._log.error(
                        u'CSSStylesheet: Found @charset or @import after index %s.' %
                        index,
                        error=xml.dom.HierarchyRequestErr)
                    return
            # before @media and stylerule
            for r in self.cssRules[:index]:
                if isinstance(r, cssutils.css.CSSMediaRule) or \
                    isinstance(r, cssutils.css.CSSPageRule) or \
                    isinstance(r, cssutils.css.CSSStyleRule):
                    self._log.error(
                        u'CSSStylesheet: Found @media, @page or StyleRule before index %s.' %
                        index,
                        error=xml.dom.HierarchyRequestErr)
                    return
            self.cssRules.insert(index, rule)
            rule.parentStyleSheet = self
            self.namespaces.add(rule.prefix)

        # all other
        else:
            for r in self.cssRules[index:]:
                if isinstance(r, cssutils.css.CSSCharsetRule) or \
                   isinstance(r, cssutils.css.CSSImportRule) or \
                   isinstance(r, cssutils.css.CSSNamespaceRule):
                    self._log.error(
                        u'CSSStylesheet: Found @charset, @import or @namespace before index %s.' %
                        index,
                        error=xml.dom.HierarchyRequestErr)
                    return
            self.cssRules.insert(index, rule)
            rule.parentStyleSheet = self

        return index


    def addRule(self, rule):
        "DEPRECATED, use appendRule instead"
        import warnings
        warnings.warn(
            '``addRule`` is deprecated: Use ``insertRule(rule)``.',
            DeprecationWarning)
        return self.insertRule(rule)


    def _getsetOwnerRuleDummy(self):
        """
        NOT IMPLEMENTED YET
        If this style sheet comes from an @import rule, the ownerRule
        attribute will contain the CSSImportRule. In that case, the
        ownerNode attribute in the StyleSheet interface will be null. If
        the style sheet comes from an element or a processing instruction,
        the ownerRule attribute will be null and the ownerNode attribute
        will contain the Node.
        """
        raise NotImplementedError()

    ownerRule = property(_getsetOwnerRuleDummy, _getsetOwnerRuleDummy,
                         doc="(DOM attribute) NOT IMPLEMENTED YET")


    def setSerializer(self, cssserializer):
        """
        Sets Serializer used for output of this stylesheet
        """
        if isinstance(cssserializer, cssutils.CSSSerializer):
            cssutils.ser = cssserializer
        else:
            raise ValueError(u'Serializer must be an instance of cssutils.CSSSerializer.')

    def setSerializerPref(self, pref, value):
        """
        Sets Preference of CSSSerializer used for output of this
        stylesheet. See cssutils.serialize.Preferences for possible
        preferences to be set.
        """
        cssutils.ser.prefs.__setattr__(pref, value)

    def __repr__(self):
        return "<cssutils.css.%s object title=%r href=%r at 0x%x>" % (
                self.__class__.__name__, self.title, self.href, id(self))


if __name__ == '__main__':
    print "CSSStyleSheet"
    c = CSSStyleSheet(href=None,
                        #
                        media="all",
                        title="test",
                        disabled=None,
                        ownerNode=None,
                        parentStyleSheet=None)
    c.cssText = u'''@\\namespace n1 "utf-8";
       |a[n1|b], n2|c {}
    '''
    print c.cssText
##    print "title: ", c.title
##    print "type: ", c.type
##    print c.cssRules
##    c.addRule(cssutils.css.CSSImportRule('x'))
