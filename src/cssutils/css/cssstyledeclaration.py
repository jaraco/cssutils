"""CSSStyleDeclaration implements DOM Level 2 CSS CSSStyleDeclaration and
inherits CSS2Properties

see
    http://www.w3.org/TR/1998/REC-CSS2-19980512/syndata.html#parsing-errors

Unknown properties
------------------
User agents must ignore a declaration with an unknown property.
For example, if the style sheet is::

    H1 { color: red; rotation: 70minutes }

the user agent will treat this as if the style sheet had been::

    H1 { color: red }

Cssutils gives a warning about an unknown CSS2 Property "rotation" but
keeps any property.

Illegal values
--------------
User agents must ignore a declaration with an illegal value. For example::

    IMG { float: left }       /* correct CSS2 */
    IMG { float: left here }  /* "here" is not a value of 'float' */
    IMG { background: "red" } /* keywords cannot be quoted in CSS2 */
    IMG { border-width: 3 }   /* a unit must be specified for length values */

A CSS2 parser would honor the first rule and ignore the rest, as if the
style sheet had been::

    IMG { float: left }
    IMG { }
    IMG { }
    IMG { }

Cssutils again will issue warning about invalid CSS2 property values.

TODO:
    This interface is also used to provide a read-only access to the
    computed values of an element. See also the ViewCSS interface.

    - return computed values and not literal values
    - simplify unit pairs/triples/quadruples
      2px 2px 2px 2px -> 2px for border/padding...
    - normalize compound properties like:
      background: no-repeat left url()  #fff
      -> background: #fff url() no-repeat left
"""
__all__ = ['CSSStyleDeclaration', 'SameNamePropertyList']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom

import cssutils
from cssproperties import CSS2Properties
from property import _Property as Property


class CSSStyleDeclaration(CSS2Properties, cssutils.util.Base):
    """
    The CSSStyleDeclaration class represents a single CSS declaration
    block. This class may be used to determine the style properties
    currently set in a block or to set style properties explicitly
    within the block.

    While an implementation may not recognize all CSS properties within
    a CSS declaration block, it is expected to provide access to all
    specified properties in the style sheet through the
    CSSStyleDeclaration interface.
    Furthermore, implementations that support a specific level of CSS
    should correctly handle CSS shorthand properties for that level. For
    a further discussion of shorthand properties, see the CSS2Properties
    interface.

    Additionally the CSS2Properties interface is implemented.

    Properties
    ==========
    cssText: of type DOMString
        The parsable textual representation of the declaration block
        (excluding the surrounding curly braces). Setting this attribute
        will result in the parsing of the new value and resetting of the
        properties in the declaration block. It also allows the insertion
        of additional properties and their values into the block.
    length: of type unsigned long, readonly
        The number of properties that have been explicitly set in this
        declaration block. The range of valid indices is 0 to length-1
        inclusive.
    parentRule: of type CSSRule, readonly
        The CSS rule that contains this declaration block or None if this
        CSSStyleDeclaration is not attached to a CSSRule.
    seq: a list (cssutils)
        All parts of this style declaration including CSSComments

    $css2propertyname
        All properties defined in the CSS2Properties class are available
        as direct properties of CSSStyleDeclaration with their respective
        DOM name, so e.g. ``fontStyle`` for property 'font-style'.

        These may be used as::

            >>> style = CSSStyleDeclaration(cssText='color: red')
            >>> style.color = 'green'
            >>> print style.color
            green
            >>> del style.color
            >>> print style.color # print empty string

    Format
    ======
    [Property: Value;]* Property: Value?
    """
    def __init__(self, parentRule=None, cssText=u'', readonly=False):
        """
        parentRule
            The CSS rule that contains this declaration block or
            None if this CSSStyleDeclaration is not attached to a CSSRule.
        readonly
            defaults to False
        """
        super(CSSStyleDeclaration, self).__init__()

        self.valid = True

        self.seq = []
        self.parentRule = parentRule
        self.cssText = cssText
        self._readonly = readonly


    def __setattr__(self, n, v):
        """
        Prevent setting of unknown properties on CSSStyleDeclaration
        which would not work anyway. For these
        ``CSSStyleDeclaration.setProperty`` MUST be called explicitly!

        TODO:
            implementation of known is not really nice, any alternative?
        """
        known = ['_tokenizer', '_log', '_ttypes',
                 'valid', 'seq', 'parentRule', '_parentRule', 'cssText',
                 '_readonly']
        known.extend(CSS2Properties._properties)
        if n in known:
            super(CSSStyleDeclaration, self).__setattr__(n, v)
        else:
            raise AttributeError(
                'Unknown CSS Property, ``CSSStyleDeclaration.setProperty("%s")`` MUST be used.'
                % n)

    # overwritten accessor functions for CSS2Properties' properties
    def _getP(self, CSSName):
        """
        (DOM CSS2Properties)
        Overwritten here and effectively the same as
        ``self.getPropertyValue(CSSname)``.

        Parameter is in CSSname format ('font-style'), see CSS2Properties.

        Example::

            >>> style = CSSStyleDeclaration(cssText='font-style:italic;')
            >>> print style.fontStyle
            italic

        """
        return self.getPropertyValue(CSSName)

    def _setP(self, CSSName, value):
        """
        (DOM CSS2Properties)
        Overwritten here and effectively the same as
        ``self.setProperty(CSSname, value)``.

        Only known CSS2Properties may be set this way, otherwise an
        AttributeError is raised.
        For these unknown properties ``setPropertyValue(CSSname, value)``
        has to be called explicitly.
        Also setting the priority of properties needs to be done with a
        call like ``setPropertyValue(CSSname, value, priority)``.

        Example::

            >>> style = CSSStyleDeclaration()
            >>> style.fontStyle = 'italic'
            >>> # or
            >>> style.setProperty('font-style', 'italic', '!important')

        """
        if 'background-image' == CSSName:
#            for p in self._properties():
#                if p.name == 'background':
#                    print p
            self.setProperty(CSSName, value)
        else:
            self.setProperty(CSSName, value)

    def _delP(self, CSSName):
        """
        (cssutils only)
        Overwritten here and effectively the same as
        ``self.removeProperty(CSSname)``.

        Example::

            >>> style = CSSStyleDeclaration(cssText='font-style:italic;')
            >>> del style.fontStyle
            >>> print style.fontStyle # prints u''

        """
        self.removeProperty(CSSName)


    def _getCssText(self):
        """
        returns serialized property cssText
        """
        return cssutils.ser.do_css_CSSStyleDeclaration(self)

    def _setCssText(self, cssText):
        """
        Setting this attribute will result in the parsing of the new value
        and resetting of all the properties in the declaration block
        including the removal or addition of properties.

        DOMException on setting

        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this declaration is readonly or a property is readonly.
        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        """
        def ignoreuptopropend(i, tokens):
            "returns position of ending ;"
            ignoredtokens, endi = self._tokensupto(
                    tokens[i:], propertypriorityendonly=True)
            if ignoredtokens:
                ignored = ''.join([x.value for x in ignoredtokens])
                self._log.error(u'CSSStyleDeclaration: Ignored: "%s".' %
                          self._valuestr(ignoredtokens), t)
            return endi + 1

        self._checkReadonly()
        tokens = self._tokenize(cssText)

        newseq = []
        i, imax = 0, len(tokens)
        while i < imax:
            t = tokens[i]
            if self._ttypes.S == t.type: # ignore
                pass
            elif self._ttypes.COMMENT == t.type: # just add
                newseq.append(cssutils.css.CSSComment(t))
            else:
                # name upto ":" (or ; -> error)
                nametokens, endi = self._tokensupto(
                    tokens[i:], propertynameendonly=True)
                i += endi

                shouldbecolon = nametokens.pop()
                if shouldbecolon.value == u':': # OK: exclude ending :
                    i += 1
                elif shouldbecolon.value == u';': # ERROR: premature ;
                    self._log.error(
                        u'CSSStyleDeclaration: Incomplete Property starting here: %s.' %
                        self._valuestr(tokens[i-1:]), t)
                    i += 1 # exclude ending :
                    continue
                else: # ERROR: no :
                    self._log.error(
                        u'CSSStyleDeclaration: No Propertyname and/or ":" found: %s.' %
                              self._valuestr(tokens[i:]), t)
                    i += ignoreuptopropend(i, tokens)
                    continue

                for x in nametokens:
                    if x.type == self._ttypes.IDENT:
                        break
                else: # ERROR: no name
                    self._log.error(
                        u'CSSStyleDeclaration: No Propertyname found: %s.'
                        % self._valuestr(tokens[i-1:]), t)
                    i += ignoreuptopropend(i, tokens)
                    continue

                # value upto ";" or "!important" or end
                valuetokens, endi = self._tokensupto(
                    tokens[i:], propertyvalueendonly=True)
                i += endi
                if valuetokens and \
                   valuetokens[-1].type == self._ttypes.SEMICOLON:
                    del valuetokens[-1] # exclude ending ;
                    prioritytokens = None
                elif valuetokens and \
                     valuetokens[-1].type == self._ttypes.IMPORTANT_SYM:
                    del valuetokens[-1] # exclude !important

                    # priority upto ; or end
                    prioritytokens, endi = self._tokensupto(
                            tokens[i:], propertypriorityendonly=True)
                    i += endi

                    if prioritytokens and prioritytokens[-1].type == \
                       self._ttypes.SEMICOLON:
                        del prioritytokens[-1] # exclude ending ;
                elif not valuetokens:
                    self._log.error(u'CSSStyleDeclaration: No property value: %s'
                              % self._valuestr(cssText))
                    i += ignoreuptopropend(i, tokens)
                    continue
                else:
                    prioritytokens = None

                self.setProperty(nametokens, valuetokens, prioritytokens,
                                 overwrite=False, _seq=newseq)
            i += 1

        self.seq = newseq

    cssText = property(_getCssText, _setCssText,
        doc="(DOM) The parsable textual representation of the declaration\
        block excluding the surrounding curly braces.")


    def _getLength(self):
        return len([x for x in self.seq if isinstance(x, SameNamePropertyList)])

    length = property(_getLength,
        doc="(DOM) the number of properties that have been explicitly set\
        in this declaration block. The range of valid indices is 0 to\
        length-1 inclusive.")


    def _getParentRule(self):
        return self._parentRule

    def _setParentRule(self, parentRule):
        self._parentRule = parentRule

    parentRule = property(_getParentRule, _setParentRule,
        doc="(DOM) The CSS rule that contains this declaration block or\
        None if this CSSStyleDeclaration is not attached to a CSSRule.")


    def getPropertyCSSValue(self, name):
        """
        (DOM)
        Used to retrieve the object representation of the value of a CSS
        property if it has been explicitly set within this declaration
        block. This method returns None if the property is a shorthand
        property. Shorthand property values can only be accessed and
        modified as strings, using the getPropertyValue and setProperty
        methods.

        name
            of the CSS property

            The name will be normalized (lowercase, no simple escapes) so
            "color", "COLOR" or "C\olor" are all equivalent

        returns CSSValue, the value of the property if it has been
        explicitly set for this declaration block. Returns None if the
        property has not been set.

        for more on shorthand properties see
            http://www.dustindiaz.com/css-shorthand/
        """
        SHORTHAND = [
            u'background',
            u'border',
            u'border-left', u'border-right',
            u'border-top', u'border-bottom',
            u'border-color', u'border-style', u'border-width',
            u'cue',
            u'font',
            u'list-style',
            u'margin',
            u'outline',
            u'padding',
            u'pause']

        normalname = self._normalize(name)

        if normalname in SHORTHAND:
            self._log.info(
                u'CSSValue for shorthand property "%s" should be None, this may be implemented later.' %
                normalname, neverraise=True)

        for pl in self.seq:
            if isinstance(pl, SameNamePropertyList) and \
               pl.name == normalname:
                return pl[pl._currentIndex()].cssValue


    def getPropertyValue(self, name):
        """
        (DOM)
        Used to retrieve the value of a CSS property if it has been
        explicitly set within this declaration block.

        name
            of the CSS property

            The name will be normalized (lowercase, no simple escapes) so
            "color", "COLOR" or "C\olor" are all equivalent

        returns the value of the property if it has been explicitly set
        for this declaration block. Returns the empty string if the
        property has not been set.
        """
        normalname = self._normalize(name)

        for pl in self.seq:
            if isinstance(pl, SameNamePropertyList) and \
               pl.name == normalname:
                return pl[pl._currentIndex()].cssValue._value
        return u''


    def getPropertyPriority(self, name):
        """
        (DOM)
        Used to retrieve the priority of a CSS property (e.g. the
        "important" qualifier) if the property has been explicitly set in
        this declaration block.

        name
            of the CSS property

            The name will be normalized (lowercase, no simple escapes) so
            "color", "COLOR" or "C\olor" are all equivalent

        returns a string representing the priority (e.g. "important") if
        one exists. The empty string if none exists.
        """
        normalname = self._normalize(name)

        for pl in self.seq:
            if isinstance(pl, SameNamePropertyList) and \
               pl.name == normalname:
                return pl[pl._currentIndex()].priority
        return u''


    def getSameNamePropertyList(self, name):
        """
        (cssutils) EXPERIMENTAL
        Used to retrieve all properties set with this name. For cases where
        a property is set multiple times with different values or
        priorities for different UAs::

            background: url(1.gif) fixed;
            background: url(2.gif) scroll;

        name
            of the CSS property

            The name will be normalized (lowercase, no simple escapes) so
            "color", "COLOR" or "C\olor" are all equivalent

        Returns the SameNamePropertyList object if available for the given
        property name, else returns ``None``.
        """
        normalname = self._normalize(name)

        for pl in self.seq:
            if isinstance(pl, SameNamePropertyList) and \
               pl.name == normalname:
                return pl

    def item(self, index):
        """
        (DOM)
        Used to retrieve the properties that have been explicitly set in
        this declaration block. The order of the properties retrieved using
        this method does not have to be the order in which they were set.
        This method can be used to iterate over all properties in this
        declaration block.

        index
            of the property to retrieve, negative values behave like
            negative indexes on Python lists, so -1 is the last element

        returns the name of the property at this ordinal position. The
        empty string if no property exists at this position.
        """
        properties = [x.name for x in self.seq
                      if isinstance(x, SameNamePropertyList)]
        try:
            return properties[index]
        except IndexError:
            return u''

    def removeProperty(self, name):
        """
        (DOM)
        Used to remove a CSS property if it has been explicitly set within
        this declaration block.

        name
            of the CSS property to remove

            The name will be normalized (lowercase, no simple escapes) so
            "color", "COLOR" or "C\olor" are all equivalent

        returns the value of the property if it has been explicitly set for
        this declaration block. Returns the empty string if the property
        has not been set or the property name does not correspond to a
        known CSS property

        raises DOMException

        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this declaration is readonly or the property is
          readonly.
        """
        self._checkReadonly()

        normalname = self._normalize(name)

        r = u''
        for i, pl in enumerate(self.seq):
            if isinstance(pl, SameNamePropertyList) and \
               pl.name == normalname:
                r = pl[pl._currentIndex()].cssValue._value
                del self.seq[i]
                break

        return r


    def setProperty(self, name, value, priority=None, overwrite=True,
                    _seq=None):
        """
        (DOM)
        Used to set a property value and priority within this declaration
        block.

        name
            of the CSS property to set
            (in W3C DOM the parameter is called "propertyName")
            will be normalized in the Property

        value
            the new value of the property
        priority
            the optional priority of the property (e.g. "important")
        _seq
            used by self._setCssText only as in temp seq

        DOMException on setting

        - SYNTAX_ERR: (self)
          Raised if the specified value has a syntax error and is
          unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this declaration is readonly or the property is
          readonly.
        """
        self._checkReadonly()

        if _seq is None: # seq to update
            _seq = self.seq

        newp = Property(name, value, priority)
        if newp.name and newp.cssValue:
            newnormalname = newp.normalname

            # index of pl to exchange or append to, maybe
            index = -1
            for i, pl in enumerate(_seq):
                if isinstance(pl, SameNamePropertyList) and \
                   pl.name == newnormalname:
                    index = i
                    break

            if index == -1:
                # not yet in _seq -> append
                newpl = SameNamePropertyList(newnormalname)
                newpl.append(newp)
                _seq.append(newpl)
            else:
                if overwrite:
                    # empty proplist and add new property
                    del _seq[index][:]
                    _seq[index].append(newp)
                else:
                    # append to pl
                    _seq[index].append(newp)

    def replaceUrls(self, replacer):
        """
        **EXPERIMENTAL**
        
        utility function to replace all url(urlstring) values in a 
        CSSStyleDeclaration.
        
        replacement must be a function which is called with a single 
        argument ``urlstring`` which is the current value of url()
        excluding "url(" and ")". It still may have surrounding single or
        double quotes 
        """
        def set(v):
            if v.CSS_PRIMITIVE_VALUE == v.cssValueType and\
               v.CSS_URI == v.primitiveType:
                    v.setStringValue(v.CSS_URI, 
                                     replacer(v.getStringValue()))
        
        pls = [x for x in self.seq if isinstance(x, SameNamePropertyList)]
        for pl in pls:
            for p in pl:
                v = p.cssValue
                if v.CSS_VALUE_LIST == v.cssValueType:
                    for item in v:
                        set(item)
                elif v.CSS_PRIMITIVE_VALUE == v.cssValueType:
                    set(v)

    def __repr__(self):
        return "cssutils.css.%s()" % (
                self.__class__.__name__)
        
    def __str__(self):
        return "<cssutils.css.%s object length=%r at 0x%x>" % (
                self.__class__.__name__, self.length, id(self))


class SameNamePropertyList(list):
    """
    (cssutils) EXPERIMENTAL

    A list of properties with the same normalname. Used for equivelant
    properties like color, c\olor, co\lor.
    To get the actual Property (latest with the highest priority) use
    SameNamePropertyList[SameNamePropertyList._currentIndex()].

    Properties
    ==========
    name
        normalized Property name (e.g. ``color``)

        see ``token.Token`` for details on "normalized"

    Useful only if all similar named properties should be kept after
    parsing. See ``Serializer.prefs.keepAllProperties``
    """
    def __init__(self, name):
        self.name = cssutils.util.Base._normalize(name)

    def _currentIndex(self):
        """
        returns index of current value of this property
        used by serializer and getValue and getPriority
        """
        importants = [i for (i, p) in enumerate(self)
                      if p.priority]
        if importants:
            return importants[-1]
        else:
            normals = [i for (i, p) in enumerate(self)
                      if not p.priority]
            if normals:
                return normals[-1]

    def __repr__(self):
        return "cssutils.css.%s(name=%r)" % (
                self.__class__.__name__, self.name)
        
    def __str__(self):
        return "<cssutils.css.%s object name=%r at 0x%x>" % (
                self.__class__.__name__, self.name, id(self))
        

if __name__ == '__main__':
    cssutils.css.cssstyledeclaration.Property = Property

    s = cssutils.parseString('''a {
        color: red;
        font-style: italic;
    }''')
    style = s.cssRules[0].style
    print 1, style.fontStyle, style.getPropertyValue('font-style')
    print 1, style.color, style.getPropertyValue('color')

    style.color = 'green'
    style.fontStyle = 'normal'

    print 2, style.fontStyle, style.getPropertyValue('font-style')
    print 2, style.color, style.getPropertyValue('color')

    style.xxx = '1'
