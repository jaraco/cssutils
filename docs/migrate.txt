=================
version migration
=================

---------
from last
---------

0.9.8 incompatible changes
==========================

CSS Values
----------
0.9.8 deprecates or better removes support for ``css.Value``, ``css.ValueList``, ``css.PrimitiveValue`` and subclasses. They are all replaced by ``css.PropertyValue``, which contains a list of ``css.Value`` objects. See docs for these for details.

Changes in more detail:

- ``css.CSSStyleDeclaration.getCSSValue`` return ``css.Property.propertyValue`` now!
- added ``css.Property.propertyValue``
- deprecated ``css.Property.cssValue`` which now is more or less ``css.Property.propertyValue``
- removed ``css.Value``, ``css.ValueList``, ``css.PrimitiveValue``
- added ``css.PropertyValue`` which contains a list of ``css.Value`` or more specific subclass objects like ``css.DimensionValue``, ``css.CSSFunction`` etc
- renamed ``css.ExpressionValue`` to ``css.MSValue`` as it contains Microsoft IE specific values only anyway
- ``css.CSSFunction``, ``css.CSSVariable``, ``css.MSValue`` are now subclasses of ``css.Value``


-------
archive
-------

0.9.7 incompatible changes
==========================
- Replaced init parameter and attribute ``css.Selector.parentList`` with ``css.Selector.parent``

- Removed ``css.Property.parentStyle`` which was deprecated for some times now in favor of ``css.Property.parent``

- ``CSSRule`` constants have been changed due to a change in the CSSOM spec. The actual integer values **SHOULD NOT** be used anyway! **Please do always use the ``CSSRule`` constants which are present in ALL CSSRule and subclass objects like CSSStyleRule, CSSImportRule etc.!**

- Renamed ``cssutils.ser.prefs.keepUnkownAtRules`` to ``cssutils.ser.prefs.keepUnkownAtRules`` due to misspelling, see Issue #37. A DeprecationWarning is issued on use.


0.9.6 incompatible changes
==========================

Exception handling with position information
--------------------------------------------
This actually is **not** an incompatible change (but was during some alpha releases):

``xml.dom.DOMException``\ s raised do now contain infos about the position where the exception occured.

You may access these infos with ``msg, line, col = e.args[0], e.line, e.col``. ``str(e)`` does work as expected and contains the error message only.


CSSValue / Property has been rewritten
--------------------------------------
- moved validating of a property from ``CSSValue`` to ``Property``
- removed ``CSSValue.valid`` as it does not make sense anymore
- ``CSSPrimitiveValue.getStringValue()`` returns a STRING without quotes or for URIs a value without surrounding ``url(...)`` now

minor API changes
-----------------
+ moved ``cssutils.css.cssproperties.cssvalues`` to ``cssutils.profiles.css2``

+ ``cssutils.utils.Base`` and ``cssutils.utils.Base2`` have been changed and will be removed in favor of new ``cssutils.utils.NewBase``. These are all internal helper classes and should not be used in client code anyway but ye be warned...

+ A few private attributes have been changed. It is best to not use these anyway but if you have:
    - removed private init parameter ``CSSValue._propertyName``
    - private attribute ``CSSValue._value`` contains ``(value, type)`` now. Do not use as it may change again!

+ The API has been cleaned up resulting in *DEPRECATED* attributes and methods being removed:
    - removed ``Property.normalname`` (DEPRECATED from 0.9.5 ), use ``Property.name`` instead
    - removed ``CSSStyleSheet.replaceUrls``, use ``cssutils.replaceUrls()`` instead

----

0.9.5 incompatible changes
==========================
cssutils 0.9.5 introduced some minor incompatible API changes. Reason for most changes is that for most cases the new default behaviour makes more sense.


logging versus raising
----------------------
Upto 0.9.5rc1 any sheet resulting from parsing via any ``parse*`` function or ``CSSParser(raiseExceptions=False)`` (which is also the default) resulted in the library simply logging any later exceptions and not raising them. 0.9.5rc2 fixes this. Until now the global setting of ``cssutils.log.raiseExceptions=True`` (the default) was overwritten with the value of the CSSParser ``raiseExceptions`` setting which is normally ``False`` any time a ``cssutils.parse*`` function or ``CSSParser.parse*`` method was used. So

until 0.9.5rc1::

    >>> # does not raise during parse
    >>> s = cssutils.parseString('$') # empty but CSSStyleSheet object

    >>> # does not raise either but should:
    >>> s.cssText = '$'
    ERROR   CSSStyleRule: No start { of style declaration found: u'$' [1:2: ]
    # [...]

from 0.9.5rc2::

    >>> # still does not raise during parse
    >>> s = cssutils.parseString('$') # empty but CSSStyleSheet object

    >>> # working with the actual DOM does raise now though
    >>> s.cssText = '$'
    # [...] traceback
    xml.dom.SyntaxErr: CSSStyleRule: No start { of style declaration found: u'$' [1:1: $]

To use the old but false behaviour add the following line at the start to your program::

    >>> cssutils.log.raiseExceptions = False # normally True

**This should only be done in specific cases** as normal raising of exceptions in methods or functions with the CSS DOM is the expected behaviour.


parsing
-------
``parse()`` is *DEPRECATED* in favour of ``parseFile()``. Both methods are still available but ``parse`` will be removed for cssutils 1.0.

All ``parse*`` functions (or ``CSSParser.parse*`` methods) do raise errors from 0.9.5final.

iterating over ``CSSStyleDeclaration``
--------------------------------------
Iterating over ``css.CSSStyleDelcaration`` now yields *effective* properties only and not *all* properties set in the declaration. To retrieve *all* properties use ``CSSStyleDeclaration.getProperties(all=True)``.

example
~~~~~~~
iterating over a CSSStyleDeclaration with ``cssText='color: red; c\olor: green'``

OLD:
    yielded two Property objects with the values ``red`` and ``green``.
NEW since 0.9.5:
    yields one Property only (the actual one used) which has the value ``green``.


``Property.name`` attribute
---------------------------
``Property.name`` until now hold the *literal* value (e.g. ``c\olor`` of a properties name. Now it holds the *normalized* name. ``Property.normalname`` is therefor *DEPRECATED*. To access the unnormalized (literal) name use the new readonly property ``Property.literalname``.

example
~~~~~~~

::

        p = Property(ur'c\olor', 'red')

OLD
    ::

        p.name == ur'c\olor'
        p.normalname == ur'color' # now DEPRECATED

NEW since 0.9.5
    ::

        p.name == ur'color'
        p.literalname == ur'c\olor'

``Property.priority`` attribute
-------------------------------
The value of ``Property.priority`` (or ``CSSStyleDeclatation.getPropertyPriority(p)``) is now ``important`` without a leading ``!`` as defined in the CSS specs.

(``Property._normalpriority`` has been removed, the normalized value that was available here is now in ``Property.priority``. The literal priority value is available in ``Property.literalproperty`` now (analog to ``Property.literalname``). All these values probably should not be used by client code anyway but may be helpful when using CSS hacks.)

example
~~~~~~~
::

    p = Property(u'color', 'red', u'!IMPOR\\TANT')

OLD
    ::

        p.priority == u'!IMPOR\\TANT'
        p._normalpriority == u'!important' # now REMOVED!

NEW since 0.9.5
    ::

        p.priority == u'important'
        p.literalpriority == u'IMPOR\\TANT'

``CSSStyleSheet.replaceUrls(replacer)``
---------------------------------------
Since 0.9.5b1 ``replaceUrls`` has been moved from a method of ``CSSStyleSheet`` to a utility function in cssutils directly.

example
~~~~~~~
::

        def replacer(url):
            "returns new URL"

        sheet = cssutils.parseUrl('http://example.com/test.css')


OLD
    ::

        sheet.replaceUrls(replacer)

NEW since 0.9.5b1
    ::

        cssutils.replaceUrls(sheet, replacer)

