"""
CSSStyleSheet implements DOM Level 2 CSS CSSStyleSheet.

Partly also:
    - http://dev.w3.org/csswg/cssom/#the-cssstylesheet
    - http://www.w3.org/TR/2006/WD-css3-namespace-20060828/

TODO:
    - ownerRule and ownerNode
"""
__all__ = ['CSSStyleSheet']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssutils.stylesheets

class CSSStyleSheet(cssutils.stylesheets.StyleSheet):
    """
    The CSSStyleSheet interface represents a CSS style sheet.

    Properties
    ==========
    CSSOM
    -----
    cssRules
        of type CSSRuleList, (DOM readonly)
    ownerRule
        of type CSSRule, readonly (NOT IMPLEMENTED YET)

    Inherits properties from stylesheet.StyleSheet

    cssutils
    --------
    cssText: string
        a textual representation of the stylesheet
    prefixes: set
        A set of declared prefixes via @namespace rules. Each
        CSSStyleRule is checked if it uses additional prefixes which are
        not declared. If they do they are "invalidated".

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
        self.prefixes = set()
        self._readonly = readonly

#    def __checkprefixes(self, stylerule, prefixes):
#        """
#        checks if all prefixes used in stylerule have been declared
#        """
#        notdeclared = set()
#        for s in stylerule.selectorList:
#            for prefix in s.prefixes:
#                if not prefix in prefixes:
#                    notdeclared.add(prefix)
#        return notdeclared

    def _getCssText(self):
        return cssutils.ser.do_CSSStyleSheet(self)

    def _setCssText(self, cssText):
        """
        (cssutils)
        Parses ``cssText`` and overwrites the whole stylesheet.

        DOMException on setting

        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if the rule is readonly.
        - SYNTAX_ERR:
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        - NAMESPACE_ERR:
          If a namespace prefix is found which is not declared.
        """
        # stylesheet  : [ CDO | CDC | S | statement ]*;
        self._checkReadonly()
        tokenizer = self._tokenize2(cssText)
        newseq = cssutils.css.CSSRuleList()
        # for closures: must be a mutable
        new = { 'prefixes': set() }

        def S(expected, seq, token, tokenizer=None):
            # @charset must be at absolute beginning of style sheet
            if expected == 0:
                return 1
            else: 
                return expected

        def charsetrule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSCharsetRule()
            rule.cssText = self._tokensupto2(tokenizer, token)
            if expected > 0 or len(seq) > 0:
                self._log.error(
                    u'CSSStylesheet: CSSCharsetRule only allowed at beginning of stylesheet.',
                    token, xml.dom.HierarchyRequestErr)
            else:
                if rule.valid:
                    seq.append(rule)
            return 1

        def importrule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSImportRule()
            rule.cssText = self._tokensupto2(tokenizer, token)
            if expected > 1:
                self._log.error(
                    u'CSSStylesheet: CSSImportRule not allowed here.',
                    token, xml.dom.HierarchyRequestErr)
            else:
                if rule.valid:
                    seq.append(rule)
            return 1

        def namespacerule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSNamespaceRule()
            rule.cssText = self._tokensupto2(tokenizer, token)
            if expected > 2:
                self._log.error(
                    u'CSSStylesheet: CSSNamespaceRule not allowed here.',
                    token, xml.dom.HierarchyRequestErr)
            else:
                if rule.valid:
                    seq.append(rule)
                    new['prefixes'].add(rule.prefix)
            return 2

        def pagerule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSPageRule()
            rule.cssText = self._tokensupto2(tokenizer, token)
            if rule.valid:
                seq.append(rule)
            return 3

        def mediarule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSMediaRule()
            rule.cssText = self._tokensupto2(tokenizer, token)
            if rule.valid:
                seq.append(rule)
            return 3

        def unknownrule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSUnknownRule()
            rule.cssText = self._tokensupto2(tokenizer, token)
            if rule.valid:
                seq.append(rule)
            return expected

        def ruleset(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSStyleRule()
            rule.cssText = self._tokensupto2(tokenizer, token)
            
            # check namespaces
            notdeclared = set()           
            for selector in rule.selectorList.seq:
                for prefix in selector.prefixes:
                    if not prefix in new['prefixes']:
                        notdeclared.add(prefix)
            if notdeclared:
                rule.valid = False
                self._log.error(
                    u'CSSStylesheet: CSSStyleRule uses undeclared namespace prefixes: %s.' %
                    u', '.join(notdeclared), error=xml.dom.NamespaceErr)

            if rule.valid:
                seq.append(rule)
            return 3

        # expected:
        # ['CHARSET', 'IMPORT', 'NAMESPACE', ('PAGE', 'MEDIA', ruleset)]
        valid, expected = self._parse(0, newseq, tokenizer,
            {'S': S,
             'CDO': lambda *ignored: None,
             'CDC': lambda *ignored: None,
             'CHARSET_SYM': charsetrule,
             'IMPORT_SYM': importrule,
             'NAMESPACE_SYM': namespacerule,
             'PAGE_SYM': pagerule,
             'MEDIA_SYM': mediarule,
             'ATKEYWORD': unknownrule
             }, 
             default=ruleset)

        self.cssRules = newseq
        self.prefixes = new['prefixes']
        for r in self.cssRules:
            r.parentStyleSheet = self

        #print '\nNEWSEQ:\n', newseq
        #print self.prefixes

        return

        # -----------------

        newcssRules = cssutils.css.CSSRuleList()

        while i < imax:
            t = tokens[i]

#            if t.type == self._ttypes.EOF:
#                break
#
#            # ignore
#            if t.type in (self._ttypes.S, self._ttypes.CDO, self._ttypes.CDC):
#                pass

            # unexpected: } ;
            if t.type in (self._ttypes.SEMICOLON,
                            self._ttypes.LBRACE, self._ttypes.RBRACE):
                self._log.error(u'CSSStyleSheet: Syntax Error',t)

#            # simply add
#            elif self._ttypes.COMMENT == t.type:
#                newcssRules.append(cssutils.css.CSSComment(t))

#            # @charset only at beginning
#            elif self._ttypes.CHARSET_SYM == t.type:
#                atruletokens, endi = self._tokensupto(tokens[i:])
#                i += endi
#                self._log.error(u'CSSStylesheet: CSSCharsetRule only allowed at beginning of stylesheet.',
#                    t, xml.dom.HierarchyRequestErr)

#            # @import before any StyleRule and @rule except @charset
#            elif self._ttypes.IMPORT_SYM == t.type:
#                atruletokens, endi = self._tokensupto(tokens[i:])
#                if expected == '@import':
#                    atrule = cssutils.css.CSSImportRule()
#                    atrule.cssText = atruletokens
#                    newcssRules.append(atrule)
#                else:
#                    self._log.error(
#                        u'CSSStylesheet: CSSImportRule not allowed here.',
#                        t, xml.dom.HierarchyRequestErr)
#                i += endi

#            # @namespace before any StyleRule and
#            #  before @rule except @charset, @import
#            elif self._ttypes.NAMESPACE_SYM == t.type:
#                atruletokens, endi = self._tokensupto(tokens[i:])
#                if expected in ('@import', '@namespace'):
#                    atrule = cssutils.css.CSSNamespaceRule()
#                    atrule.cssText = atruletokens
#                    newcssRules.append(atrule)
#                    newnamespaces.add(atrule.prefix)
#                else:
#                    self._log.error(
#                        u'CSSStylesheet: CSSNamespaceRule not allowed here.',
#                        t, xml.dom.HierarchyRequestErr)
#                i += endi
#                expected = '@namespace' # now no @import anymore!

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
                notdeclared = self.__checkprefixes(rule, newprefixes)
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
        self.prefixes = newprefixes

    cssText = property(_getCssText, _setCssText,
            "(cssutils) a textual representation of the stylesheet")

    def deleteRule(self, index):
        """
        Used to delete a rule from the style sheet.

        index
            of the rule to remove in the StyleSheet's rule list. For an
            index < 0 **no** INDEX_SIZE_ERR is raised but rules for
            normal Python lists are used. E.g. ``deleteRule(-1)`` removes
            the last rule in cssRules.

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
            a parsable DOMString (cssutils: or CSSRule object)
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
        - INDEX_SIZE_ERR: (self)
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
            self.prefixes.add(rule.prefix)

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

    def _getsetOwnerRuleDummy(self):
        """
        NOT IMPLEMENTED YET

        CSSOM
        -----
        The ownerRule  attribute, on getting, must return the CSSImportRule
        that caused this style sheet to be imported (if any). Otherwise, if
        no CSSImportRule caused it to be imported the attribute must return
        null.
        """
        raise NotImplementedError()

    ownerRule = property(_getsetOwnerRuleDummy, _getsetOwnerRuleDummy,
                         doc="(DOM attribute) NOT IMPLEMENTED YET")

    def replaceUrls(self, replacer):
        """
        **EXPERIMENTAL**

        Utility method to replace all url(urlstring) values in
        CSSImportRules and CSSStyleDeclaration objects (properties).

        ``replacer`` must be a function which is called with a single
        argument ``urlstring`` which is the current value of url()
        excluding ``url(`` and ``)``. It still may have surrounding
        single or double quotes though.
        """
        for importrule in [
            r for r in self.cssRules if hasattr(r, 'href')]:
            importrule.href = replacer(importrule.href)

        def setProperty(v):
            if v.CSS_PRIMITIVE_VALUE == v.cssValueType and\
               v.CSS_URI == v.primitiveType:
                    v.setStringValue(v.CSS_URI,
                                     replacer(v.getStringValue()))

        def styleDeclarations(base):
            "recurive function to find all CSSStyleDeclarations"
            styles = []
            if hasattr(base, 'cssRules'):
                for rule in base.cssRules:
                    styles.extend(styleDeclarations(rule))
            elif hasattr(base, 'style'):
                styles.append(base.style)
            return styles

        for style in styleDeclarations(self):
            for p in style:
                v = p.cssValue
                if v.CSS_VALUE_LIST == v.cssValueType:
                    for item in v:
                        setProperty(item)
                elif v.CSS_PRIMITIVE_VALUE == v.cssValueType:
                    setProperty(v)

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
        return "cssutils.css.%s(href=%r, title=%r)" % (
                self.__class__.__name__, self.href, self.title)

    def __str__(self):
        return "<cssutils.css.%s object title=%r href=%r at 0x%x>" % (
                self.__class__.__name__, self.title, self.href, id(self))
