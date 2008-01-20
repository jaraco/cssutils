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
    encoding
        reflects the encoding of an @charset rule or 'utf-8' (default)
        if set to ``None``
    namespaces
        a dict of {prefix: namespaceURI} mapping

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
        self.cssRules.append = self.insertRule
        self.cssRules.extend = self.insertRule
        
        self._namespaces = {}  
        self._readonly = readonly

    def __iter__(self):
        """
        generator which iterates over cssRules.
        """
        for rule in self.cssRules:
            yield rule
    
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
        
        # save namespaces as these may be reset during setting of cssText
        CURRENTNAMESPACES = self._namespaces
        # used during setting (CSSStyleRule and CSSMediaRule)
        self._namespaces = {}
        
        tokenizer = self._tokenize2(cssText)
        newseq = [] #cssutils.css.CSSRuleList()
        # for closures: must be a mutable
        new = {}

        def S(expected, seq, token, tokenizer=None):
            # @charset must be at absolute beginning of style sheet
            if expected == 0:
                return 1
            else: 
                return expected

        def charsetrule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSCharsetRule()
            rule.parentStyleSheet = self
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
            rule.parentStyleSheet = self
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
            rule.parentStyleSheet = self
            rule.cssText = self._tokensupto2(tokenizer, token)
            if expected > 2:
                self._log.error(
                    u'CSSStylesheet: CSSNamespaceRule not allowed here.',
                    token, xml.dom.HierarchyRequestErr)
            else:
                if rule.valid:
                    seq.append(rule)
                    # special case, normally would use new['namespaces']
                    self._namespaces[rule.prefix] = rule.namespaceURI
            return 2

        def fontfacerule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSFontFaceRule()
            rule.parentStyleSheet = self
            rule.cssText = self._tokensupto2(tokenizer, token)
            if rule.valid:
                seq.append(rule)
            return 3

        def pagerule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSPageRule()
            rule.parentStyleSheet = self
            rule.cssText = self._tokensupto2(tokenizer, token)
            if rule.valid:
                seq.append(rule)
            return 3

        def mediarule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSMediaRule()
            rule.parentStyleSheet = self
            rule.cssText = self._tokensupto2(tokenizer, token)
            if rule.valid:
                seq.append(rule)
            return 3

        def unknownrule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSUnknownRule()
            rule.parentStyleSheet = self
            rule.cssText = self._tokensupto2(tokenizer, token)
            if rule.valid:
                seq.append(rule)
            return expected

        def ruleset(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSStyleRule()
            rule.parentStyleSheet = self
            rule.cssText = self._tokensupto2(tokenizer, token)
            
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
             'FONT_FACE_SYM': fontfacerule,
             'IMPORT_SYM': importrule,
             'NAMESPACE_SYM': namespacerule,
             'PAGE_SYM': pagerule,
             'MEDIA_SYM': mediarule,
             'ATKEYWORD': unknownrule
             }, 
             default=ruleset)

        if valid:
            del self.cssRules[:]
            for r in newseq:
                self.cssRules.append(r)
            # normally: self._namespaces = new['namespaces']
            # but this is set before!
            for r in self.cssRules:
                # set for CSSComment, for others this is set before
                r.parentStyleSheet = self
        else:
            # reset namespaces
            self._namespaces = CURRENTNAMESPACES

    cssText = property(_getCssText, _setCssText,
            "(cssutils) a textual representation of the stylesheet")

    def _setEncoding(self, encoding):
        """
        sets encoding of charset rule if present or inserts new charsetrule
        with given encoding. If encoding if None removes charsetrule if 
        present.
        """ 
        try:
            rule = self.cssRules[0]
        except IndexError:
            rule = None
        if rule and rule.CHARSET_RULE == rule.type:
            if encoding:
                rule.encoding = encoding
            else: 
                self.deleteRule(0)
        elif encoding:
            self.insertRule(cssutils.css.CSSCharsetRule(encoding=encoding), 0)            
    
    def _getEncoding(self):
        "return encoding if @charset rule if given or default of 'utf-8'"
        try:
            return self.cssRules[0].encoding
        except (IndexError, AttributeError):
            return 'utf-8'

    encoding = property(_getEncoding, _setEncoding,
            "(cssutils) reflects the encoding of an @charset rule or 'UTF-8' (default) if set to ``None``")

    namespaces = property(lambda self: self._namespaces, 
                          doc="Namespaces used in this CSSStyleSheet (READONLY)")

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
        - NAMESPACE_ERR: (TODO)
          Raised if removing this rule would result in an invalid StyleSheet
        """
        self._checkReadonly()
            
        try:
            r = self.cssRules[index] 
        except IndexError:
            raise xml.dom.IndexSizeErr(
                u'CSSStyleSheet: %s is not a valid index in the rulelist of length %i' % (
                index, self.cssRules.length))
        else:
            if r.type == r.NAMESPACE_RULE:
                # check if namespacerule and check if needed
                "TODO"
                #raise xml.dom.NamespaceErr(
                #    u'CSSStyleSheet: Namespace defined in this rule is needed, cannot remove.')
                
            r.parentStyleSheet = None # detach
            del self.cssRules[index] # delete from StyleSheet

    def insertRule(self, rule, index=None):
        """
        Used to insert a new rule into the style sheet. The new rule now
        becomes part of the cascade.

        Rule may be a string or a valid CSSRule or a CSSRuleList.

        rule
            a parsable DOMString 
            
            in cssutils also a CSSRule or a CSSRuleList
            
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
        elif isinstance(rule, cssutils.css.CSSRuleList):
            for i, r in enumerate(rule):
                self.insertRule(r, index + i)
            return index
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
                        u'CSSStylesheet: Cannot insert @import here, found @namespace, @media, @page or CSSStyleRule before index %s.' %
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
                        u'CSSStylesheet: Cannot insert @namespace here, found @charset or @import after index %s.' %
                        index,
                        error=xml.dom.HierarchyRequestErr)
                    return
            # before @media and stylerule
            for r in self.cssRules[:index]:
                if isinstance(r, cssutils.css.CSSMediaRule) or \
                    isinstance(r, cssutils.css.CSSPageRule) or \
                    isinstance(r, cssutils.css.CSSStyleRule):
                    self._log.error(
                        u'CSSStylesheet: Cannot insert @namespace here, found @media, @page or CSSStyleRule before index %s.' %
                        index,
                        error=xml.dom.HierarchyRequestErr)
                    return
            self.cssRules.insert(index, rule)
            rule.parentStyleSheet = self
            self._namespaces[rule.prefix] = rule.namespaceURI

        # all other
        else:
            for r in self.cssRules[index:]:
                if isinstance(r, cssutils.css.CSSCharsetRule) or \
                   isinstance(r, cssutils.css.CSSImportRule) or \
                   isinstance(r, cssutils.css.CSSNamespaceRule):
                    self._log.error(
                        u'CSSStylesheet: Cannot insert rule here, found @charset, @import or @namespace before index %s.' %
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

        Utility method to replace all ``url(urlstring)`` values in 
        ``CSSImportRules`` and ``CSSStyleDeclaration`` objects (properties).

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
            for p in style.getProperties(all=True):
                v = p.cssValue
                if v.CSS_VALUE_LIST == v.cssValueType:
                    for item in v:
                        setProperty(item)
                elif v.CSS_PRIMITIVE_VALUE == v.cssValueType:
                    setProperty(v)

    def setSerializer(self, cssserializer):
        """
        Sets the global Serializer used for output of all stylesheet
        output.
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
        return "<cssutils.css.%s object title=%r href=%r encoding=%r at 0x%x>" % (
                self.__class__.__name__, self.title, self.href, self.encoding,
                id(self))
