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
    encoding
        reflects the encoding of an @charset rule or 'utf-8' (default)
        if set to ``None``
    ownerRule
        of type CSSRule, readonly (NOT IMPLEMENTED YET)

    Inherits properties from stylesheet.StyleSheet

    cssutils
    --------
    cssText: string
        a textual representation of the stylesheet
    namespaces
        reflects set @namespace rules of this rule.
        A dict of {prefix: namespaceURI} mapping.

    Format
    ======
    stylesheet
      : [ CHARSET_SYM S* STRING S* ';' ]?
        [S|CDO|CDC]* [ import [S|CDO|CDC]* ]*
        [ namespace [S|CDO|CDC]* ]* # according to @namespace WD
        [ [ ruleset | media | page ] [S|CDO|CDC]* ]*
    """
    class __Namespaces(object):
        "similar to a dict used for namespace rule wrapper"
        
        def __init__(self, sheet, *p):
            "no initial values are set, only the relevant sheet is"
            self.sheet = sheet
            self._namespaces = {}
            
        def __findrule(self, key):
            # returns namespace rule where prefix == key
            for r in self.sheet:
                if r.type == r.NAMESPACE_RULE and r.prefix == key:
                    return r
    
        def __contains__(self, key):
            return key in self._namespaces
        
        def __delitem__(self, key):
            "deleted namespace rule with prefix == key"
            rule = self.__findrule(key)
            if rule:
                for i, r in enumerate(self.sheet):
                    if r == rule:
                        break
                self.sheet.deleteRule(i)
                del self._namespaces[key]
            else: 
                raise IndexError('Prefix "%s" not present in style sheet.' % key)
    
        def __getitem__(self, key):
            return self._namespaces[key]
        
        def __iter__(self):
            return self._namespaces.__iter__()
        
        def __len__(self):
            return len(self._namespaces)
    
        def __setitem__(self, key, value):
            "may raise NoModificationAllowedErr"
            r = self.__findrule(key)
            if not r:
                self._namespaces[key] = value
                self.sheet.insertRule(cssutils.css.CSSNamespaceRule(
                                                        prefix=key,
                                                        namespaceURI=value),
                                      inOrder=True)
            else:
                if key in self._namespaces or value in self._namespaces.values():
                    r.namespaceURI = value # raises NoModificationAllowedErr
                self._namespaces[key] = value
    
        def __repr__(self):
            return repr(self._namespaces)
    
        def __str__(self):
            return str(self._namespaces)
    
        def items(self):
            return self._namespaces.items()
    
        def keys(self):
            return self._namespaces.keys()
    
    
    type = 'text/css'

    def __init__(self, href=None, media=None, title=u'', disabled=None,
                 ownerNode=None, parentStyleSheet=None, readonly=False):
        """
        init parameters are the same as for stylesheets.StyleSheet
        """
        super(CSSStyleSheet, self).__init__(
                self.type, href, media, title, disabled,
                ownerNode, parentStyleSheet)

        self.cssRules = cssutils.css.CSSRuleList()
        self.cssRules.append = self.insertRule
        self.cssRules.extend = self.insertRule
        self._namespaces = CSSStyleSheet.__Namespaces(sheet=self)  
        self._readonly = readonly

    def __iter__(self):
        "generator which iterates over cssRules."
        for rule in self.cssRules:
            yield rule
    
    
    def _getCssText(self):
        return cssutils.ser.do_CSSStyleSheet(self)

    def _setCssText(self, cssText):
        """
        (cssutils)
        Parses ``cssText`` and overwrites the whole stylesheet.

        :param cssText: parsable string
        :Exceptions:
            - `NAMESPACE_ERR`:
              If a namespace prefix is found which is not declared.
            - `NO_MODIFICATION_ALLOWED_ERR`: (self)
              Raised if the rule is readonly.
            - `SYNTAX_ERR`:
              Raised if the specified CSS string value has a syntax error and
              is unparsable.
        """
        self._checkReadonly()
                
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

        def COMMENT(expected, seq, token, tokenizer=None):
            "special: sets parent*"
            comment = cssutils.css.CSSComment([token], parentRule=self, 
                                parentStyleSheet=self.parentStyleSheet)
            seq.append(comment)
            return expected
        
        def charsetrule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSCharsetRule(parentStyleSheet=self)
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
            rule = cssutils.css.CSSImportRule(parentStyleSheet=self)
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
            rule = cssutils.css.CSSNamespaceRule(
                                cssText=self._tokensupto2(tokenizer, token),
                                parentStyleSheet=self)
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
            rule = cssutils.css.CSSFontFaceRule(parentStyleSheet=self)
            rule.cssText = self._tokensupto2(tokenizer, token)
            if rule.valid:
                seq.append(rule)
            return 3

        def mediarule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSMediaRule(parentStyleSheet=self)
            rule.cssText = self._tokensupto2(tokenizer, token)
            if rule.valid:
                seq.append(rule)
            return 3

        def pagerule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSPageRule(parentStyleSheet=self)
            rule.cssText = self._tokensupto2(tokenizer, token)
            if rule.valid:
                seq.append(rule)
            return 3

        def unknownrule(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSUnknownRule(parentStyleSheet=self)
            rule.cssText = self._tokensupto2(tokenizer, token)
            if rule.valid:
                seq.append(rule)
            return expected

        def ruleset(expected, seq, token, tokenizer):
            rule = cssutils.css.CSSStyleRule(parentStyleSheet=self)
            rule.cssText = self._tokensupto2(tokenizer, token)
            
            if rule.valid:
                seq.append(rule)
            return 3

        # expected:
        # ['CHARSET', 'IMPORT', 'NAMESPACE', ('PAGE', 'MEDIA', ruleset)]
        wellformed, expected = self._parse(0, newseq, tokenizer,
            {'S': S,
             'COMMENT': COMMENT,
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

        if wellformed:
            del self.cssRules[:]
            for r in newseq:
                self.cssRules.append(r)
            # normally: self._namespaces = new['namespaces']
            # but this is set before!

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
                          doc="Namespaces used in this CSSStyleSheet.")

    def add(self, rule):
        """
        Adds rule to stylesheet at appropriate position. 
        Same as ``sheet.insertRule(rule, inOrder=True)``. 
        """
        return self.insertRule(rule, index=None, inOrder=True)

    def deleteRule(self, index):
        """
        Used to delete a rule from the style sheet.

        :param index:
            of the rule to remove in the StyleSheet's rule list. For an
            index < 0 **no** INDEX_SIZE_ERR is raised but rules for
            normal Python lists are used. E.g. ``deleteRule(-1)`` removes
            the last rule in cssRules.
        :Exceptions:
            - `INDEX_SIZE_ERR`: (self)
              Raised if the specified index does not correspond to a rule in
              the style sheet's rule list.
            - `NAMESPACE_ERR`: (self)
              Raised if removing this rule would result in an invalid StyleSheet
            - `NO_MODIFICATION_ALLOWED_ERR`: (self)
              Raised if this style sheet is readonly.
        """
        self._checkReadonly()
            
        try:
            rule = self.cssRules[index] 
        except IndexError:
            raise xml.dom.IndexSizeErr(
                u'CSSStyleSheet: %s is not a valid index in the rulelist of length %i' % (
                index, self.cssRules.length))
        else:
            if rule.type == rule.NAMESPACE_RULE:
                # check all namespacerule if used
                uris = [r.namespaceURI for r in self if r.type == r.NAMESPACE_RULE]
                useduris = set()
                for r in self:
                    if r.type == r.STYLE_RULE:
                        useduris.update(r.selectorList._getUsedUris())  
                    elif r.type == r.MEDIA_RULE:
                        for x in r:
                            if x.type == x.STYLE_RULE:
                                useduris.update(x.selectorList._getUsedUris())  
                if rule.namespaceURI in useduris and\
                   uris.count(rule.namespaceURI) == 1: 
                    raise xml.dom.NamespaceErr(
                        u'CSSStyleSheet: NamespaceURI defined in this rule is used, cannot remove.')
                    return
                
            rule._parentStyleSheet = None # detach
            del self.cssRules[index] # delete from StyleSheet

    def insertRule(self, rule, index=None, inOrder=False):
        """
        Used to insert a new rule into the style sheet. The new rule now
        becomes part of the cascade.

        :Parameters:
            rule
                a parsable DOMString, in cssutils also a CSSRule or a 
                CSSRuleList
            index
                of the rule before the new rule will be inserted.
                If the specified index is equal to the length of the
                StyleSheet's rule collection, the rule will be added to the end
                of the style sheet.
                If index is not given or None rule will be appended to rule
                list.
            inOrder
                if True the rule will be put to a proper location while 
                ignoring index but without raising HIERARCHY_REQUEST_ERR.
                The resulting index is returned nevertheless                
        :returns: the index within the stylesheet's rule collection
        :Exceptions:
            - `HIERARCHY_REQUEST_ERR`: (self)
              Raised if the rule cannot be inserted at the specified index
              e.g. if an @import rule is inserted after a standard rule set
              or other at-rule.
            - `INDEX_SIZE_ERR`: (self)
              Raised if the specified index is not a valid insertion point.
            - `NO_MODIFICATION_ALLOWED_ERR`: (self)
              Raised if this style sheet is readonly.
            - `SYNTAX_ERR`: (rule)
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
            return

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

        if not rule.valid:
            raise xml.dom.SyntaxErr(u'CSSStyleSheet: Invalid rules cannot be added.')
            return

        # CHECK HIERARCHY
        # @charset
        if rule.type == rule.CHARSET_RULE:
            if inOrder:
                index = 0
                # always first and only
                if (self.cssRules and self.cssRules[0].type == rule.CHARSET_RULE):
                    self.cssRules[0].encoding = rule.encoding
                else:
                    self.cssRules.insert(0, rule)
                    rule._parentStyleSheet = self
            elif index != 0 or (self.cssRules and 
                              self.cssRules[0].type == rule.CHARSET_RULE):
                self._log.error(
                    u'CSSStylesheet: @charset only allowed once at the beginning of a stylesheet.',
                    error=xml.dom.HierarchyRequestErr)
                return
            else:
                self.cssRules.insert(index, rule)
                rule._parentStyleSheet = self

        # @unknown or comment
        elif rule.type in (rule.UNKNOWN_RULE, rule.COMMENT) and not inOrder:
            if index == 0 and self.cssRules and\
               self.cssRules[0].type == rule.CHARSET_RULE:
                self._log.error(
                    u'CSSStylesheet: @charset must be the first rule.',
                    error=xml.dom.HierarchyRequestErr)
                return
            else:
                self.cssRules.insert(index, rule)
                rule._parentStyleSheet = self

        # @import
        elif rule.type == rule.IMPORT_RULE:
            if inOrder:
                # automatic order
                if rule.type in (r.type for r in self):
                    # find last of this type
                    for i, r in enumerate(reversed(self.cssRules)):
                        if r.type == rule.type:
                            index = len(self.cssRules) - i
                            break
                else:
                    # find first point to insert
                    if self.cssRules and self.cssRules[0].type in (rule.CHARSET_RULE,
                                                                   rule.COMMENT):
                        index = 1
                    else: 
                        index = 0
            else:                   
                # after @charset
                if index == 0 and self.cssRules and\
                   self.cssRules[0].type == rule.CHARSET_RULE:
                    self._log.error(
                        u'CSSStylesheet: Found @charset at index 0.',
                        error=xml.dom.HierarchyRequestErr)
                    return
                # before @namespace, @page, @font-face, @media and stylerule
                for r in self.cssRules[:index]:
                    if r.type in (r.NAMESPACE_RULE, r.MEDIA_RULE, r.PAGE_RULE,
                                  r.STYLE_RULE, r.FONT_FACE_RULE):
                        self._log.error(
                            u'CSSStylesheet: Cannot insert @import here, found @namespace, @media, @page or CSSStyleRule before index %s.' %
                            index,
                            error=xml.dom.HierarchyRequestErr)
                        return
            self.cssRules.insert(index, rule)
            rule._parentStyleSheet = self

        # @namespace
        elif rule.type == rule.NAMESPACE_RULE:
            if inOrder:
                if rule.type in (r.type for r in self):
                    # find last of this type
                    for i, r in enumerate(reversed(self.cssRules)):
                        if r.type == rule.type:
                            index = len(self.cssRules) - i
                            break
                else:
                    # find first point to insert
                    for i, r in enumerate(self.cssRules):
                        if r.type in (r.MEDIA_RULE, r.PAGE_RULE, r.STYLE_RULE,
                                      r.FONT_FACE_RULE):
                            index = i # before these
                            break
            else:            
                # after @charset and @import
                for r in self.cssRules[index:]:
                    if r.type in (r.CHARSET_RULE, r.IMPORT_RULE):
                        self._log.error(
                            u'CSSStylesheet: Cannot insert @namespace here, found @charset or @import after index %s.' %
                            index,
                            error=xml.dom.HierarchyRequestErr)
                        return
                # before @media and stylerule
                for r in self.cssRules[:index]:
                    if r.type in (r.MEDIA_RULE, r.PAGE_RULE, r.STYLE_RULE,
                                  r.FONT_FACE_RULE):
                        self._log.error(
                            u'CSSStylesheet: Cannot insert @namespace here, found @media, @page or CSSStyleRule before index %s.' %
                            index,
                            error=xml.dom.HierarchyRequestErr)
                        return
            self.cssRules.insert(index, rule)
            rule._parentStyleSheet = self
            self.namespaces[rule.prefix] = rule.namespaceURI

        # all other
        else:
            if inOrder:
                # after last of this kind or at end of sheet
                if rule.type in (r.type for r in self):
                    # find last of this type
                    for i, r in enumerate(reversed(self.cssRules)):
                        if r.type == rule.type:
                            index = len(self.cssRules) - i
                            break
                    self.cssRules.insert(index, rule)
                else:
                    self.cssRules.append(rule) # to end as no same present 
            else:
                for r in self.cssRules[index:]:
                    if r.type in (r.CHARSET_RULE, r.IMPORT_RULE, r.NAMESPACE_RULE):
                        self._log.error(
                            u'CSSStylesheet: Cannot insert rule here, found @charset, @import or @namespace before index %s.' %
                            index,
                            error=xml.dom.HierarchyRequestErr)
                        return
                self.cssRules.insert(index, rule)
            
            rule._parentStyleSheet = self

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
        for importrule in (r for r in self if r.type == r.IMPORT_RULE):
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
