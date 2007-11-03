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

Cssutils gives a WARNING about an unknown CSS2 Property "rotation" but
keeps any property (if syntactical correct).

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

Cssutils again will issue WARNING about invalid CSS2 property values.

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
__all__ = ['CSSStyleDeclaration', 'Property']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssutils
from cssproperties import CSS2Properties
from property import Property

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
    valid
        if this declaration is valid, currently to CSS 2.1 (?)
    wellformed
        if this declaration is syntactically ok

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
        self.valid = False
        self.wellformed = False
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
                 'valid', 'wellformed', 
                 'seq', 'parentRule', '_parentRule', 'cssText',
                 '_readonly']
        known.extend(CSS2Properties._properties)
        if n in known:
            super(CSSStyleDeclaration, self).__setattr__(n, v)
        else:
            raise AttributeError(
                'Unknown CSS Property, ``CSSStyleDeclaration.setProperty("%s")`` MUST be used.'
                % n)

    def __iter__(self):
        "CSSStyleDeclaration is iterable, see __items()"
        return CSSStyleDeclaration.__items(self)

    def __items(self):
        """
        the iterator

        returns in contrast to calling item(index) all property objects so
        effectively the same as ``getProperties(all=True)``
        """
        properties = self.getProperties(all=True)
        for property in properties:
            yield property

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
        self.setProperty(CSSName, value)
        # TODO:
#        if 'background-image' == CSSName:
#            for p in self._properties():
#                if p.name == 'background':
#                    print p
#            self.setProperty(CSSName, value)
#        else:
#            self.setProperty(CSSName, value)

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
        self._checkReadonly()
        tokenizer = self._tokenize2(cssText)

        # for closures: must be a mutable
        new = {'valid': True,
               'wellformed': True,
               'char': None
        }                    
        def ident(expected, seq, token, tokenizer=None):
            # a property
            if new['char']:
                # maybe an IE hack?
                token = (token[0], u'%s%s' % (new['char'], token[1]), 
                         token[2], token[3])

            tokens = self._tokensupto2(tokenizer, starttoken=token,
                                       semicolon=True)
            if self._tokenvalue(tokens[-1]) == u';':
                tokens.pop()
            property = Property()
            property.cssText = tokens
            if property.wellformed:
                seq.append(property)
            else:
                self._log.error(u'CSSStyleDeclaration: Syntax Error in Property: %s'
                                % self._valuestr(tokens))

            new['char'] = None
            return expected

        def char(expected, seq, token, tokenizer=None):
            # maybe an IE hack?
            new['valid'] = False # wellformed is set later
            self._log.error(u'CSSStyleDeclaration: Unexpected CHAR.', token)
            c = self._tokenvalue(token)
            if c in u'$':
                self._log.info(u'Trying to use (invalid) CHAR %r in Property name' %
                                  c)
                new['char'] = c

        # [Property: Value;]* Property: Value?
        newseq = []
        wellformed, expected = self._parse(expected=None,
            seq=newseq, tokenizer=tokenizer,
            productions={'IDENT': ident, 'CHAR': char})
        valid = new['valid']

        # wellformed set by parse
        # post conditions
        if new['char']:
            valid =wellformed = False
            self._log.error(u'Could not use unexpected CHAR %r' % new['char'])            
        
        if wellformed:
            self.seq = newseq
            self.wellformed = wellformed
            self.valid = valid

    cssText = property(_getCssText, _setCssText,
        doc="(DOM) A parsable textual representation of the declaration\
        block excluding the surrounding curly braces.")

    def getCssText(self, separator=None):
        """
        returns serialized property cssText, each property separated by
        given ``separator`` which may e.g. be u'' to be able to use
        cssText directly in an HTML style attribute. ";" is always part of
        each property (except the last one) and can **not** be set with
        separator!
        """
        return cssutils.ser.do_css_CSSStyleDeclaration(self, separator)

    def _getParentRule(self):
        return self._parentRule

    def _setParentRule(self, parentRule):
        self._parentRule = parentRule

    parentRule = property(_getParentRule, _setParentRule,
        doc="(DOM) The CSS rule that contains this declaration block or\
        None if this CSSStyleDeclaration is not attached to a CSSRule.")

    def getProperties(self, name=None, all=False):
        """
        returns a list of Property objects set in this declaration in order
        they have been set e.g. in the original stylesheet

        name
            optional name of properties which are requested (a filter).
            Only properties with this (normalized) name are returned.
        all=False
            if False (DEFAULT) only the effective properties (the ones set
            last) are returned. So if a name is given only one property
            is returned.

            if True all properties including properties set multiple times with
            different values or priorities for different UAs are returned.
        """
        nname = self._normalize(name)
        properties = []
        done = set()
        for x in reversed(self.seq):
            if isinstance(x, Property):
                isname = (bool(nname) == False) or (x.normalname == nname)
                stilltodo = x.normalname not in done
                if isname and stilltodo:
                    properties.append(x)
                    if not all:
                        done.add(x.normalname)

        properties.reverse()
        return properties

    def getPropertyCSSValue(self, name, normalize=True):
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
        nname = self._normalize(name)
        if nname in self._SHORTHANDPROPERTIES:
            self._log.debug(
                u'CSSValue for shorthand property "%s" should be None, this may be implemented later.' %
                nname, neverraise=True)

        properties = self.getProperties(name, all=(not normalize))
        for property in reversed(properties):
            if normalize and property.normalname == nname:
                return property.cssValue
            elif property.name == name:
                return property.cssValue
        return None

    def getPropertyValue(self, name, normalize=True):
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
        nname = self._normalize(name)
        properties = self.getProperties(name, all=(not normalize))
        for property in reversed(properties):
            if normalize and property.normalname == nname:
                return property.value
            elif property.name == name:
                return property.value
        return u''

    def getPropertyPriority(self, name, normalize=True):
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
        nname = self._normalize(name)
        properties = self.getProperties(name, all=(not normalize))
        for property in reversed(properties):
            if normalize and property.normalname == nname:
                return property.priority
            elif property.name == name:
                return property.priority
        return u''

    def removeProperty(self, name, normalize=True):
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
        nname = self._normalize(name)
        newseq = []
        r = u''
        isdone = False
        for x in reversed(self.seq):
            if isinstance(x, Property):
                if not isdone and normalize and x.normalname == nname:
                    r = x.cssValue.cssText
                    isdone = True
                elif not isdone and x.name == name:
                    r = x.cssValue.cssText
                    isdone = True
                else:
                    newseq.append(x)
            else:
                newseq.append(x)
        newseq.reverse()
        self.seq = newseq
        return r

    def setProperty(self, name, value, priority=u'', normalize=True):
        """
        (DOM)
        Used to set a property value and priority within this declaration
        block.

        name
            of the CSS property to set (in W3C DOM the parameter is called
            "propertyName")

            If a property with this name is present it will be reset

            The name is normalized if normalize=True

        value
            the new value of the property
        priority
            the optional priority of the property (e.g. "important")

        DOMException on setting

        - SYNTAX_ERR: (self)
          Raised if the specified value has a syntax error and is
          unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this declaration is readonly or the property is
          readonly.
        """
        self._checkReadonly()

        newp = Property(name, value, priority)
        if not newp.wellformed:
            self._log.warn(u'Invalid Property: %s: %s %s'
                    % (name, value, priority))
        else:
            nname = self._normalize(name)
            properties = self.getProperties(name, all=(not normalize))
            for property in reversed(properties):
                if normalize and property.normalname == nname:
                    property.cssValue = newp.cssValue.cssText
                    property.priority = newp.priority
                    break
                elif property.name == name:
                    property.cssValue = newp.cssValue.cssText
                    property.priority = newp.priority
                    break
            else:
                self.seq.append(newp)

    def __nnames(self):
        nnames = set()
        for x in self.seq:
            if isinstance(x, Property):
                nnames.add(x.normalname)
        return nnames

    def item(self, index):
        """
        **NOTE**:
        Compare to ``for property in declaration`` which works on **all**
        properties set in this declaration and not just the effecitve ones.

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

        ATTENTION:
        Only properties with a different normalname are counted. If two
        properties with the same normalname are present in this declaration
        only the last set (and effectively *in style*) is used.

        ``item()`` and ``length`` work on the same set here.
        """
        nnames = self.__nnames()
        orderednnames = []
        for x in reversed(self.seq):
            nname = x.normalname
            if isinstance(x, Property) and nname in nnames:
                nnames.remove(nname)
                orderednnames.append(nname)
        orderednnames.reverse()
        try:
            return orderednnames[index]
        except IndexError:
            return u''

    def _getLength(self):
        return len(self.__nnames())

    length = property(_getLength,
        doc="(DOM) The number of distince properties that have been explicitly\
        in this declaration block. The range of valid indices is 0 to\
        length-1 inclusive. These are properties with the same ``normalname``\
        only. ``item()`` and ``length`` work on the same set here.")

    def __repr__(self):
        return "cssutils.css.%s()" % (
                self.__class__.__name__)

    def __str__(self):
        return "<cssutils.css.%s object length=%r (all: %r) at 0x%x>" % (
                self.__class__.__name__, self.length,
                len(self.getProperties(all=True)), id(self))
