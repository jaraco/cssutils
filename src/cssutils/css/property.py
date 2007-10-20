"""Property is a single CSS property in a CSSStyleDeclaration

Internal use only, may be removed in the future!
"""
__all__ = ['Property']
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
        a parsable textual representation of this property
    name
        of the property
    normalname
        normalized name of the property, e.g. "color" when name is "c\olor"
    cssValue
        the relevant CSSValue instance for this property
    value
        the string value of the property, same as cssValue.cssText
    priority
        of the property (currently only "!important" or None)
    seqs
        combination of a list for seq of name, a CSSValue object, and
        a list for seq of  priority (empty or [!important] currently)
    valid
        if this Property is valid
    wellformed
        if this Property is syntactically ok

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
    def __init__(self, name=None, value=None, priority=None, _mediaQuery=False):
        """
        inits property

        name
            a property name string
        value
            a property value string
        priority
            an optional priority string
        _mediaQuery boolean
            if True value is optional as used by MediaQuery objects
        """
        super(Property, self).__init__()

        self.seqs = [[], None, []]
        self.valid = False
        self.wellformed = False
        self._mediaQuery = _mediaQuery

        if name:
            self.name = name 
        else:
            self._name = u''
            self.normalname = u''
            
        if value:
            self.cssValue = value
        else:
            self.seqs[1] = CSSValue()
            
        self.priority = priority

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
        # check and prepare tokenlists for setting
        tokenizer = self._tokenize2(cssText)
        nametokens = self._tokensupto2(tokenizer, propertynameendonly=True)
        valuetokens = self._tokensupto2(tokenizer, propertyvalueendonly=True)
        prioritytokens = self._tokensupto2(tokenizer, propertypriorityendonly=True)

        wellformed = True
        if nametokens:
            
            if self._mediaQuery and not valuetokens:
                # MediaQuery may consist of name only
                self.name = nametokens
                self.cssValue = None
                self.priority = None
                return

            # remove colon from nametokens
            colontoken = nametokens.pop()
            if self._tokenvalue(colontoken) != u':':
                wellformed = False
                self._log.error(u'Property: No ":" after name found: %r' %
                                self._valuestr(cssText), colontoken)
            elif not nametokens:
                wellformed = False
                self._log.error(u'Property: No property name found: %r.' %
                            self._valuestr(cssText), colontoken)

            if valuetokens:
                if self._tokenvalue(valuetokens[-1]) == u'!':
                    # priority given, move "!" to prioritytokens
                    prioritytokens.insert(0, valuetokens.pop(-1))
            else:
                wellformed = False
                self._log.error(u'Property: No property value found: %r.' %
                                self._valuestr(cssText), colontoken)

            if wellformed:
                self.wellformed = True
                self.name = nametokens
                self.cssValue = valuetokens
                self.priority = prioritytokens

        else:
            self._log.error(u'Property: No property name found: %r.' %
                            self._valuestr(cssText))

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
        new = {'name': None, 
               'wellformed': True}

        def _ident(expected, seq, token, tokenizer=None):
            # name
            if 'name' == expected:
                new['name'] = self._tokenvalue(token)
                seq.append(new['name'])
                return 'EOF'
            else:
                new['wellformed'] = False
                self._log.error(u'Property: Unexpected ident.', token)
                return expected

        newseq = []
        wellformed, expected = self._parse(expected='name',
                                           seq=newseq, 
                                           tokenizer=self._tokenize2(name),
                                           productions={'IDENT': _ident})
        wellformed = wellformed and new['wellformed']

        # post conditions
        if not new['name']:
            wellformed = False
            self._log.error(u'Property: No name found: %s' %
                self._valuestr(name))

        if wellformed:
            self.wellformed = True
            self._name = new['name']
            self.normalname = self._normalize(self._name)
            self.seqs[0] = newseq

            # validate
            if self.normalname not in cssproperties.cssvalues:
                self.valid = False
                self._log.info(u'Property: No CSS2 Property: "%s".' %
                         new['name'], neverraise=True)
            else:
                self.valid = True
        else:
            self.wellformed = False

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
        if self._mediaQuery and not cssText:
            self.seqs[1] = CSSValue()
        else:
            cssvalue = CSSValue(cssText=cssText, _propertyName=self.name)
            if cssvalue._value and cssvalue.wellformed:
                self.wellformed = self.wellformed and cssvalue.wellformed
                self.seqs[1] = cssvalue
                self.valid = self.valid and cssvalue.valid
            else:
                self.wellformed = cssvalue.wellformed

    cssValue = property(_getCSSValue, _setCSSValue,
        doc="(cssutils) CSSValue object of this property")

    def _getValue(self):
        if self.cssValue: return self.cssValue._value
        else: return u''

    def _setValue(self, value):
        self.cssValue.cssText = value

    value = property(_getValue, _setValue,
                     doc="The textual value of this Properties cssValue.")

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
        if self._mediaQuery:
            self._priority = u''
            if priority:
                self._log.error(u'Property: No priority in a MediaQuery - ignored.')
            return

        # for closures: must be a mutable
        new = {'priority': u'', 
               'wellformed': True}

        def _char(expected, seq, token, tokenizer=None):
            # "!"
            val = self._tokenvalue(token)
            if u'!' == expected == val:
                seq.append(val)
                return 'important'
            else:
                new['wellformed'] = False
                self._log.error(u'Property: Unexpected char.', token)
                return expected

        def _ident(expected, seq, token, tokenizer=None):
            # "important"
            val = self._tokenvalue(token)
            normalval = self._tokenvalue(token, normalize=True)
            if 'important' == expected == normalval:
                new['priority'] = val
                seq.append(val)
                return 'EOF'
            else:
                new['wellformed'] = False
                self._log.error(u'Property: Unexpected ident.', token)
                return expected

        newseq = []
        wellformed, expected = self._parse(expected='!',
                                           seq=newseq, 
                                           tokenizer=self._tokenize2(priority),
                                           productions={'CHAR': _char, 
                                                        'IDENT': _ident})
        wellformed = wellformed and new['wellformed']

        # post conditions
        if priority and not new['priority']:
            wellformed = False
            self._log.info(u'Property: Invalid priority: %r.' %
                    self._valuestr(priority))

        if wellformed:
            self.wellformed = self.wellformed and wellformed
            self._priority = new['priority']
            self._normalpriority = self._normalize(self._priority)
            self.seqs[2] = newseq
            
            # validate
            if self._normalpriority not in (u'', u'important'):
                self.valid = False
                self._log.info(u'Property: No CSS2 priority value: %r.' %
                    self._normalpriority, neverraise=True)
        
    priority = property(_getPriority, _setPriority,
        doc="(cssutils) Priority of this property")

    def __repr__(self):
        return "cssutils.css.%s(name=%r, value=%r, priority=%r)" % (
                self.__class__.__name__,
                self.name, self.cssValue.cssText, self.priority)

    def __str__(self):
        return "<%s.%s object name=%r value=%r priority=%r at 0x%x>" % (
                self.__class__.__module__, self.__class__.__name__,
                self.name, self.cssValue.cssText, self.priority, id(self))
