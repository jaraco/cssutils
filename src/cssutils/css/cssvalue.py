"""CSSValue implements DOM Level 2 CSS CSSValue.

TODO
    parsing and exception raising
    setting of correct CSSValueType

    pprint of value/unit e.g.   3 px  5px ->  3px 5px
    simplify colors if possible e.g. #ffaa55 ->  #fa5
    simplify values:    0px; ->  0;
"""
__all__ = ['CSSValue']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a5, $LastChangedRevision$'

import xml.dom

import cssutils


class CSSValue(cssutils.util.Base):
    """
    The CSSValue interface represents a simple or a complex value.
    A CSSValue object only occurs in a context of a CSS property

    Properties
    ==========
    cssText
        A string representation of the current value.
    cssValueType
        A (readonly) code defining the type of the value.

    seq: a list (cssutils)
        All parts of this style declaration including CSSComments

    _value
        value without any comments, used by Property to validate
    """

    CSS_INHERIT = 0
    """
    The value is inherited and the cssText contains "inherit".
    """
    CSS_PRIMITIVE_VALUE = 1
    """
    The value is a primitive value and an instance of the
    CSSPrimitiveValue interface can be obtained by using binding-specific
    casting methods on this instance of the CSSValue interface.
    """
    CSS_VALUE_LIST = 2
    """
    The value is a CSSValue list and an instance of the CSSValueList
    interface can be obtained by using binding-specific casting
    methods on this instance of the CSSValue interface.
    """
    CSS_CUSTOM = 3
    """
    The value is a custom value.
    """

    def __init__(self, cssText=u'inherit', readonly=False):
        """
        (cssutils)
        inits a new CSS Value

        cssText
            the parsable cssText of the value
        readonly
            defaults to False
        """
        super(CSSValue, self).__init__()

        self.seq = []
        self._value = u''
        self._linetoken = None # used for line report only
        self.cssText = cssText
        self._readonly = readonly


    def __invalidToken(self, tokens, x):
        """
        raises SyntaxErr if an INVALID token in tokens

        x
            used for error message

        returns True if INVALID found, else False
        """
        for t in tokens:
            if t.type == self._ttypes.INVALID:
                self._log.error(u'CSSValue: Invalid token found in %s.' % x, t)
                return True
        return False


    def _getCssText(self):
        return cssutils.ser.do_css_CSSvalue(self)

    def _setCssText(self, cssText):
        """
        Format
        ======
        ::

            expr = value
              : term [ operator term ]*
              ;
            term
              : unary_operator?
                [ NUMBER S* | PERCENTAGE S* | LENGTH S* | EMS S* | EXS S* |
                  ANGLE S* | TIME S* | FREQ S* | function ]
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

        DOMException on setting

        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error
          (according to the attached property) or is unparsable.
        - TODO: INVALID_MODIFICATION_ERR:
          Raised if the specified CSS string value represents a different
          type of values than the values allowed by the CSS property.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this value is readonly.
        """
        self._checkReadonly()

        tokens = self._tokenize(cssText)
        if self.__invalidToken(tokens, 'value'):
            self._log.error(
                u'CSSValue: Unknown value syntax: "%s".' % self._valuestr(
                    cssText))
            return

        hasvalue = False
        newseq = []
        i, imax = 0, len(tokens)
        while i < imax:
            t = tokens[i]
            if self._ttypes.S == t.type: # add single space
                if not newseq or newseq[-1] == u' ':
                    pass # not 1st and no 2 spaces after each other
                else:
                    newseq.append(u' ')
            elif self._ttypes.COMMENT == t.type: # just add
                newseq.append(cssutils.css.CSSComment(t))
            elif t.type in (
                self._ttypes.SEMICOLON, self._ttypes.IMPORTANT_SYM) or\
                u':' == t.value:
                self._log.error(u'CSSValue: Syntax error.', t)
                return
            elif t.type == self._ttypes.FUNCTION:
                _functokens, endi = self._tokensupto(
                    tokens, funcendonly=True)
                _func = []
                for _t in _functokens:
                    _func.append(_t.value)
                newseq.append(u''.join(_func))
                i += endi #-1
                hasvalue = True
            else:
                newseq.append(t.value)
                hasvalue = True

            i += 1

        if hasvalue:
            self.seq = newseq
            self._value = u''.join([x for x in newseq if not isinstance(
                               x, cssutils.css.CSSComment)]).strip()

            if tokens:
                self._linetoken = tokens[0] # used for line report

            if self._value == u'inherit':
                self._cssValueType = CSSValue.CSS_INHERIT
            else:
                self._cssValueType = CSSValue.CSS_CUSTOM

        else:
            self._log.error(
                u'CSSValue: Unknown syntax or no value: "%s".' % self._valuestr(
                    cssText).strip())


    cssText = property(_getCssText, _setCssText,
        doc="A string representation of the current value.")


    def _getCssValueType(self):
        "readonly"
        return self._cssValueType

    cssValueType = property(_getCssValueType,
        doc="A code defining the type of the value as defined above.")
