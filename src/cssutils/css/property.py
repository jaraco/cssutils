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

class _Property(cssutils.util.Base):
    """
    (cssutils) a CSS property in a StyleDeclaration of a CSSStyleRule

    Properties
    ==========
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
    def __init__(self, name, value, priority=None):
        """
        inits property
        """
        super(_Property, self).__init__()

        self.seqs = [[], None, []]
        self.valid = True
        self.name = name
        self.cssValue = value
        self.priority = priority

    def __invalidToken(self, tokens, x):
        """
        raises SyntaxErr if an INVALID token in tokens

        x
            name, value or priority, used for error message

        returns True if INVALID found, else False
        """
        for t in tokens:
            if t.type == self._ttypes.INVALID:
                self._log.error(u'Property: Invalid token found in %s.' % x, t)
                return True
        return False

    def _getName(self):
        try:
            return self._name
        except AttributeError:
            return u''

    def _setName(self, name):
        """
        Format
        ======
        property = name
          : IDENT S*
          ;

        DOMException on setting

        - SYNTAX_ERR: (self)
          Raised if the specified name has a syntax error and is
          unparsable.
        """
        tokens = self._tokenize(name)
        if self.__invalidToken(tokens, 'name'):
            return
        newname = newnormalname = None
        newseq = []
        t = None # used later
        for i in range(0, len(tokens)):
            t = tokens[i]
            if self._ttypes.S == t.type: # ignore
                pass

            elif self._ttypes.COMMENT == t.type: # just add
                newseq.append(cssutils.css.CSSComment(t))

            elif self._ttypes.IDENT == t.type and not newname:
                newname = t.value.lower()
                newnormalname = t.normalvalue
                newseq.append(newname)

            else:
                self._log.error(u'Property: Syntax error in name.', t)
                return

        if newname:
            self._name = newname
            self.normalname = newnormalname
            self.seqs[0] = newseq

            # validate
            if newname not in cssproperties.cssvalues:
                self._log.info(u'Property: No CSS2 Property: "%s".' %
                         newname, t, neverraise=True)

        else:
            self._log.error(u'Property: No name found: "%s".' % name, t)

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
        try:
            return self._priority
        except AttributeError:
            return u''

    def _setPriority(self, priority):
        """
        priority
            currently "!important" to set an important priority
            or None or the empty string to set no priority only

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
        if priority is None or priority == u'':
            self._priority = u''
            self.seqs[2] = []
        else:
            tokens = self._tokenize(priority)
            if self.__invalidToken(tokens, 'priority'):
                return

            newpriority = None
            for t in tokens:
                if t.type in (self._ttypes.S, self._ttypes.COMMENT): # ignored
                    pass
                elif self._ttypes.IMPORTANT_SYM == t.type and not newpriority:
                    newpriority = t.value.lower()
                else:
                    self._log.error(u'Property: Unknown priority.', t)
                    return

            if newpriority:
                self._priority = newpriority
                self.seqs[2] = ['!important']
            else:
                self._log.error(u'Property: Unknown priority: "%s".' % priority)

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
    p = _Property(u'color', 'red', '! important')
    print p.name, p.cssValue, p.priority
