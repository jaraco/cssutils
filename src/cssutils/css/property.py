"""Property is a single CSS property in a CSSStyleDeclaration

Internal use only, may be removed in the future!
"""
__all__ = []
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a1, SVN revision $LastChangedRevision$'

import xml.dom 

import cssutils
import cssproperties

class _Property(cssutils.util.Base):
    """
    (cssutils) a CSS property in a StyleDeclaration of a CSSStyleRule

    Properties
    ==========
    cssValue
        the relevant CSSValue instance for this property
    name
        of the property
    normalname
        normalized name of the property, e.g. "color" when name is "c\olor"
    value
        the string value of the property
    priority
        of the property (currently only "!important" or None)
    seqs
        3 lists for seq of name, value and
        priority (empty or [!important] currently)
    valid
        if this Property is valid

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
        
        self.css2values = cssproperties.cssvalues

        self.seqs = [[], [], []]
        self.valid = True
        self.name = name
        self.value = value
        self.priority = priority


    def __repr__(self):
        return '<Property> %s: %s %s' % (self.name, self.value, self.priority)


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
    

    def _getCssValue(self):
        raise NotImplementedError()
        
    cssValue = property(_getCssValue,
        doc="(cssutils readonly) CSSValue object of this property")   


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
            if newname not in self.css2values:
                self._log.info(u'Property: No CSS2 Property: "%s".' %
                         newname, neverraise=True)
            
        else:
            self._log.error(u'Property: No name found: "%s".' % name)

    name = property(_getName, _setName,
        doc="(cssutils) Name of this property")   


    def _getValue(self):
        return cssutils.ser.do_css_Propertyvalue(self.seqs[1])

    def _setValue(self, value):
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
          Raised if the specified value has a syntax error and is
          unparsable.
        """
        tokens = self._tokenize(value)
        if self.__invalidToken(tokens, 'value'):
            return
        hasvalue = None
        newseq = []
        for i in range(0, len(tokens)):
            t = tokens[i]
            if self._ttypes.S == t.type: # add single space
                if newseq and newseq[-1] == u' ':
                    pass
                else:
                    newseq.append(u' ')
            elif self._ttypes.COMMENT == t.type: # just add
                newseq.append(cssutils.css.CSSComment(t))
            elif t.type in (self._ttypes.SEMICOLON, self._ttypes.IMPORTANT_SYM) or\
                 t.value in u':':
                 self._log.error(u'Property: Value syntax error.', t)
                 return
            else:
                hasvalue = t.value 
                newseq.append(hasvalue)
        if hasvalue: # check if a value at all...
            self.seqs[1] = newseq

            # validate
            if self.name in self.css2values:
                _v = u''.join([x for x in newseq if not isinstance(
                                   x, cssutils.css.CSSComment)]).strip()
                if not self.css2values[self.name](_v):
                    self._log.warn(u'Property: Invalid value for CSS2 property %s: %s' %
                         (self.name, _v), neverraise=True)

            
        else:
            self._log.error(u'Property: Unknown value syntax: "%s".' % value)
        
    value = property(_getValue, _setValue,
        doc="(cssutils) Value of this property")   


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
            "!"{w}"important"	{return IMPORTANT_SYM;}

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


if __name__ == '__main__':
    p = _Property(u'color', 'red', '! important')
    print p.name, p.value, p.priority
