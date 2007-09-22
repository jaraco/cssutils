"""Property is a single CSS property in a CSSStyleDeclaration

Internal use only, may be removed in the future!
"""
__all__ = []
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssutils
import cssproperties
from cssvalue import CSSValue

class Property(cssutils.util.Base):
    """
    (cssutils) a CSS property in a StyleDeclaration of a CSSStyleRule

    Properties
    ==========
    cssText
        A parsable textual representation
    name
        of the property
    normalname
        normalized name of the property, e.g. "color" when name is "c\olor"
    cssValue
        the relevant CSSValue instance for this property
    priority
        of the property (currently only "!important" or None)
    seqs
        combination of a list for seq of name, a CSSValue object, and
        a list for seq of  priority (empty or [!important] currently)
    valid
        if this Property is valid

    DEPRECATED: value
        the string value of the property, use cssValue.cssText instead!

    Format
    ======
    ::

        property = name
          : IDENT S*
          ;

        expr = value
          : term [ operator term ]*
          ;
        term
          : unary_operator?
            [ NUMBER S* | PERCENTAGE S* | LENGTH S* | EMS S* | EXS S* | ANGLE S* |
              TIME S* | FREQ S* | function ]
          | STRING S* | IDENT S* | URI S* | hexcolor
          ;
        function
          : FUNCTION S* expr ')' S*
          ;
        /*
         * There is a constraint on the color that it must
         * have either 3 or 6 hex-digits (i.e., [0-9a-fA-F])
         * after the "#"; e.g., "#000" is OK, but "#abcd" is not.
         */
        hexcolor
          : HASH S*
          ;

        prio
          : IMPORTANT_SYM S*
          ;

    """
    def __init__(self, name=None, value=None, priority=None):
        """
        inits property

        name
            a property name string
        value
            a property value string
        priority
            an optional priority string
        """
        super(Property, self).__init__()

        self.seqs = [[], None, []]
        self.valid = True
        if name:
            self.name = name
        else:
            self._name = u''
        if value:
            self.cssValue = value
        else:
            self.seqs[1] = CSSValue()
        self.priority = priority

#    def __invalidToken(self, tokens, x):
#        """
#        raises SyntaxErr if an INVALID token in tokens
#
#        x
#            name, value or priority, used for error message
#
#        returns True if INVALID found, else False
#        """
#        for t in tokens:
#            if t.type == self._ttypes.INVALID:
#                self._log.error(u'Property: Invalid token found in %s.' % x, t)
#                return True
#        return False

    def _getCssText(self):
        """
        returns serialized property cssText
        """
        return cssutils.ser.do_Property(self)

    def _setCssText(self, cssText):
        """
        DOMException on setting

        - NO_MODIFICATION_ALLOWED_ERR: (CSSRule)
          Raised if the rule is readonly.
        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        """
        pass
#        valid = True
#        tokenizer = self._tokenize2(cssText)
#
#        newseq = []
#        # for closures: must be a mutable
#        new = {
#               'name': None,
#               'value': None,
#               'priority': None,
#               'valid': True
#               }
#
#        def _ident(expected, seq, token, tokenizer=None):
#            # name or priotity: "important"
#            if 'name' == expected:
#                new['name'] = self._tokenvalue(token)
#                #seq.append(new['prefix'])
#                return ':'
#            elif u'important' == expected == val:
#                new['priority'] = u'!important'
#                #seq.append(new['prefix'])
#                return ':'
#            else:
#                new['valid'] = False
#                self._log.error(
#                    u'Property: Unexpected ident.', token)
#                return expected
#
#        def _char(expected, seq, token, tokenizer=None):
#            # ":" or "!"
#            val = self._tokenvalue(token)
#            if u':' == expected == val:
#                # do value
#
#                return 'EOF or !'
#            if expected.endswith('!') and u'!' == val:
#                return 'important'
#            else:
#                new['valid'] = False
#                self._log.error(
#                    u'CSSNamespaceRule: Unexpected char.', token)
#                return expected
#
#        # main loop: name: value* [! S* important]
#        valid, expected = self._parse(expected='name',
#            seq=newseq, tokenizer=tokenizer,
#            productions={'IDENT': _ident,
#                         'CHAR': _char})
#
#        # valid set by parse
#        valid = valid and new['valid']
#
#        # post conditions
#        if not new['name']:
#            valid = False
#            self._log.error(u'Property: No name found: %s' %
#                self._valuestr(cssText))
#
#        if not new['value']:
#            valid = False
#            self._log.error(u'Property: No value found: %s' %
#                self._valuestr(cssText))
#
#        if expected == 'important':
#            valid = False
#            self._log.error(u'Property: "!" but not "important": %s' %
#                self._valuestr(cssText))
#        elif expected != 'EOF':
#            valid = False
#            self._log.error(u'Property: No ";" found: %s' %
#                self._valuestr(cssText))
#
#        # set all
#        self.valid = valid
#        if valid:
#            self.atkeyword = new['keyword']
#            self.prefix = new['prefix']
#            self.uri = new['uri']
#            self.seq = newseq
#
    cssText = property(fget=_getCssText, fset=_setCssText,
        doc="A parsable textual representation.")

    def _getName(self):
        return self._name

    def _setName(self, name):
        """
        DOMException on setting

        - SYNTAX_ERR: (self)
          Raised if the specified name has a syntax error and is
          unparsable.
        """
        # for closures: must be a mutable
        new = {'name': None, 'valid': True}

        def _ident(expected, seq, token, tokenizer=None):
            # name
            if 'name' == expected:
                new['name'] = self._tokenvalue(token)
                seq.append(new['name'])
                return 'EOF'
            else:
                new['valid'] = False
                self._log.error(u'Property: Unexpected ident.', token)
                return expected

        newseq = []
        valid, expected = self._parse(expected='name',
            seq=newseq, tokenizer=self._tokenize2(name),
            productions={'IDENT': _ident})
        valid = valid and new['valid']

        # post conditions
        if not new['name']:
            valid = False
            self._log.error(u'Property: No name found: %s' %
                self._valuestr(name))

        # OK
        else:
            self._name = new['name']
            self.normalname = self._normalize(self._name)
            self.seqs[0] = newseq

            # validate
            if self.normalname not in cssproperties.cssvalues:
                self._log.info(u'Property: No CSS2 Property: "%s".' %
                         new['name'], neverraise=True)

    name = property(_getName, _setName,
        doc="(cssutils) Name of this property")

    def _getCSSValue(self):
        return self.seqs[1]

    def _setCSSValue(self, cssText):
        """
        see css.CSSValue

        DOMException on setting?

        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error
          (according to the attached property) or is unparsable.
        - TODO: INVALID_MODIFICATION_ERR:
          Raised if the specified CSS string value represents a different
          type of values than the values allowed by the CSS property.
        """
        cssvalue = CSSValue(cssText=cssText, _propertyName=self.name)
        if cssvalue._value:
            self.seqs[1] = cssvalue

    cssValue = property(_getCSSValue, _setCSSValue,
        doc="(cssutils) CSSValue object of this property")

    def _getPriority(self):
        return cssutils.ser.do_Property_priority(self.seqs[2])

    def _setPriority(self, priority):
        """
        priority
            a string

        Format
        ======
        ::

            prio
              : IMPORTANT_SYM S*
              ;

            "!"{w}"important"   {return IMPORTANT_SYM;}

        DOMException on setting

        - SYNTAX_ERR: (self)
          Raised if the specified priority has a syntax error and is
          unparsable.
          In this case a priority not equal to None, "" or "!{w}important".
        """
        # for closures: must be a mutable
        new = {'priority': u'', 'valid': True}

        def _char(expected, seq, token, tokenizer=None):
            # "!"
            val = self._tokenvalue(token)
            if u'!' == expected == val:
                seq.append(val)
                return 'important'
            else:
                new['valid'] = False
                self._log.error(u'Property: Unexpected char.', token)
                return expected

        def _important(expected, seq, token, tokenizer=None):
            # "important"
            if 'important' == expected:
                new['priority'] = self._tokenvalue(token)
                seq.append(new['priority'])
                return 'EOF'
            else:
                new['valid'] = False
                self._log.error(u'Property: Unexpected ident.', token)
                return expected

        newseq = []
        valid, expected = self._parse(expected='!',
            seq=newseq, tokenizer=self._tokenize2(priority),
            productions={'CHAR': _char, 'IMPORTANT_SYM': _important})

        valid = valid and new['valid']

        # post conditions
        if priority and not new['priority']:
            valid = False
            self._log.info(u'Property: Invalid priority: %r.' %
                    self._valuestr(priority))

        if valid:
            self._priority = new['priority']
            self._normalpriority = self._normalize(self._priority)
            self.seqs[2] = newseq

    priority = property(_getPriority, _setPriority,
        doc="(cssutils) Priority of this property")

    def __repr__(self):
        return "cssutils.css.property.%s(name=%r, value=%r, priority=%r)" % (
                self.__class__.__name__,
                self.name, self.cssValue.cssText, self.priority)

    def __str__(self):
        return "<%s.%s object name=%r value=%r priority=%r at 0x%x>" % (
                self.__class__.__module__, self.__class__.__name__,
                self.name, self.cssValue.cssText, self.priority, id(self))

    # DEPRECATED
    def _getValue(self):
        import warnings
        warnings.warn(
            'value is deprecated, use cssValue instead.',
            DeprecationWarning)
        if self.cssValue: return self.cssValue._value
        else: return u''
    def _setValue(self, value):
        import warnings
        warnings.warn(
            'value is deprecated, use cssValue instead.',
            DeprecationWarning)
        self.cssValue.cssText = value
    value = property(_getValue, _setValue,
                     doc="DEPRECATED use cssValue instead")


if __name__ == '__main__':
    p = Property(u'color', 'red', '! important')
    print p.name, p.cssValue, p.priority
