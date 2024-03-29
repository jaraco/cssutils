========================
Package ``cssutils.css``
========================
.. module:: cssutils.css

Classes implementing `DOM Level 2 CSS <http://www.w3.org/TR/DOM-Level-2-Style/css.html>`_ and `CSS Module: Namespaces (W3C Working Draft 28 August 2006) <http://www.w3.org/TR/css3-namespace/>`_


``CSSStyleSheet``
=================
A CSSStyleSheet contains all rules. It consists of the different CSS rules like :class:`~cssutils.css.CSSImportRule`, :class:`~cssutils.css.CSSStyleRule` etc. It also defines the encoding of the style sheet used for serialization. The encoding might by set with an :class:`~cssutils.css.CSSCharsetRule` rule or simpler with the :attr:`~cssutils.css.CSSStyleSheet.encoding` attribute. The serialized sheet may be obtained from :attr:`~cssutils.css.CSSStyleSheet.cssText`. All rules are present in :attr:`~cssutils.css.CSSStyleSheet.cssRules`, a stylesheet iterates on its rules so this might be easier. Namespaces are available via :attr:`~cssutils.css.CSSStyleSheet.namespaces` (do not rely on prefixes, see http://www.w3.org/TR/REC-xml-names/ how these work). Variables are available via :attr:`~cssutils.css.CSSStyleSheet.variables` which is a :class:`~cssutils.css.CSSVariablesDeclaration` and contains **all** available variables including the ones defined in imported style sheets. Changes to this object do NOT change the parent sheet!

.. autoclass:: cssutils.css.CSSStyleSheet
   :members:
   :inherited-members:

CSS rules
=========
``CSSRule``
-----------
.. autoclass:: cssutils.css.CSSRule
    :members:
    :inherited-members:

``CSSRuleList``
---------------
.. autoclass:: cssutils.css.CSSRuleList
   :members:
   :inherited-members:

``CSSCharsetRule``
------------------
.. autoclass:: cssutils.css.CSSCharsetRule
   :members:
   :inherited-members:

``CSSFontFaceRule``
-------------------
.. autoclass:: cssutils.css.CSSFontFaceRule
   :members:
   :inherited-members:

``CSSImportRule``
-----------------
.. autoclass:: cssutils.css.CSSImportRule
   :members:
   :inherited-members:

``CSSMediaRule``
----------------
.. autoclass:: cssutils.css.CSSMediaRule
   :members:
   :inherited-members:

``CSSNamespaceRule``
--------------------
.. autoclass:: cssutils.css.CSSNamespaceRule
   :members:
   :inherited-members:


``CSSPageRule``
---------------
.. autoclass:: cssutils.css.CSSPageRule
   :members:
   :inherited-members:

``MarginRule``
---------------
.. autoclass:: cssutils.css.MarginRule
   :members:
   :inherited-members:


``CSSStyleRule``
----------------
.. autoclass:: cssutils.css.CSSStyleRule
   :members:
   :inherited-members:

``CSSVariablesRule``
--------------------
.. autoclass:: cssutils.css.CSSVariablesRule
   :members:
   :inherited-members:

``CSSComment``
--------------
.. autoclass:: cssutils.css.CSSComment
   :members:
   :inherited-members:


Selector related classes: ``SelectorList`` and ``Selector``
===========================================================

``SelectorList``
----------------
.. autoclass:: cssutils.css.SelectorList
   :members:
   :inherited-members:

``Selector``
------------
.. autoclass:: cssutils.css.Selector
   :members:
   :inherited-members:



Style related classes: ``CSSStyleDeclaration``, ``Property``, values etc
==============================================================================================
``CSSVariablesDeclaration``
---------------------------
.. autoclass:: cssutils.css.CSSVariablesDeclaration
   :members:
   :inherited-members:

``CSSStyleDeclaration``
-----------------------
.. autoclass:: cssutils.css.CSSStyleDeclaration
   :members:
   :inherited-members:

The official DOM provides no method to obtain all values set for a property. Cssutils from 0.9.4 implements the additional method :meth:`~cssutils.css.CSSStyleDeclaration.getProperties`, example::

    >>> cssText = '''background: white url(paper.png) scroll; /* for all UAs */
    ... background: white url(ledger.png) fixed; /* for UAs that do fixed backgrounds */
    ... '''
    >>> # omit comments for this example
    >>> cssutils.ser.prefs.keepComments = False
    >>> style = cssutils.css.CSSStyleDeclaration(cssText=cssText)
    >>> print style.cssText
    background: white url(paper.png) scroll;
    background: white url(ledger.png) fixed;
    >>> # work with properties:
    >>> proplist = style.getProperties('background', all=True)
    >>> proplist
    [cssutils.css.Property(name='background', value=u'white url(paper.png) scroll', priority=u''), cssutils.css.Property(name='background', value=u'white url(ledger.png) fixed', priority=u'')]
    >>> for prop in proplist: print prop.value
    white url(paper.png) scroll
    white url(ledger.png) fixed
    >>> # overwrite the current property, to overwrite all iterate over proplist
    >>> style['background'] = ('red', '!important')
    >>> # importance in DOM ist 'important' but '!important' works too
    >>> print style['background'], style.getPropertyPriority('background')
    red important
    >>> print style.cssText
    background: white url(paper.png) scroll;
    background: red !important;
    >>> # output only "effective" properties
    >>> cssutils.ser.prefs.keepAllProperties = False
    >>> print style.cssText
    background: red !important;

``Property``
------------
.. autoclass:: cssutils.css.Property
   :members:
   :inherited-members:



Values
------
cssutils 0.9.8 features a new and hopefully simplified but
more consistent API which also will hopefully be more stable in API and code.
Please check out the development, alpha and beta versions of release 0.9.8 and
report any shortcomings you may see or any special API requests you'd like to
see in the new API.

A simple example:
    >>> css = 'normal 1em/5 Arial, sans-serif, url(example.gif), func(1,2/*comm*/)'
    >>> pv = cssutils.css.PropertyValue(css)
    >>> print pv.cssText
    >>> for i, v in enumerate(pv):
    >>>     print i, v
    normal 1em/5 Arial, sans-serif, url(example.gif), func(1, 2 /*comm*/)
    0 <cssutils.css.Value object type=IDENT value='normal' cssText=u'normal' at ...>
    1 <cssutils.css.DimensionValue object type=DIMENSION value=1 dimension='em' cssText=u'1em' at ...>
    2 <cssutils.css.DimensionValue object type=NUMBER value=5 dimension=None cssText=u'5' at ...>
    3 <cssutils.css.Value object type=IDENT value='Arial' cssText=u'Arial' at ...>
    4 <cssutils.css.Value object type=IDENT value='sans-serif' cssText=u'sans-serif' at...>
    5 <cssutils.css.URIValue object type=URI value='example.gif' uri='example.gif' cssText=u'url(example.gif)' at ...>
    6 <cssutils.css.CSSFunction object type=FUNCTION value=u'func(1, 2)' cssText=u'func(1, 2 /*comm*/)' at ...>


``PropertyValue``
~~~~~~~~~~~~~~~~~
.. autoclass:: cssutils.css.PropertyValue
    :members:
    :inherited-members:

``Value``
~~~~~~~~~~~~
.. autoclass:: cssutils.css.Value
    :members:
    :inherited-members:

``ColorValue``
~~~~~~~~~~~~~~~~~~
.. autoclass:: cssutils.css.ColorValue
    :members:
    :inherited-members:

``DimensionValue``
~~~~~~~~~~~~~~~~~~
.. autoclass:: cssutils.css.DimensionValue
    :members:
    :inherited-members:

``URIValue``
~~~~~~~~~~~~~~~
.. autoclass:: cssutils.css.URIValue
    :members:
    :inherited-members:

``CSSFunction``
~~~~~~~~~~~~~~~
.. autoclass:: cssutils.css.CSSFunction
    :members:
    :inherited-members:

``CSSCalc``
~~~~~~~~~~~~~~~~~~
.. autoclass:: cssutils.css.CSSCalc
    :members:
    :inherited-members:

``CSSVariable``
~~~~~~~~~~~~~~~~~~
.. autoclass:: cssutils.css.CSSVariable
    :members:
    :inherited-members:

``MSValue``
~~~~~~~~~~~~~~~~~~~
was ``ExpressionValue`` until 0.9.7.

.. autoclass:: cssutils.css.MSValue
    :members:
    :inherited-members:


removed classes
---------------
- ``CSSValue``
- ``CSSPrimitiveValue``
- ``CSSValueList``



Additional Info
===============
Some classes in this package support standard Python idioms like iteration on certain attributes::

    >>> import cssutils
    >>> sheet = cssutils.css.CSSStyleSheet()
    >>> sheet.cssText = '@charset "ascii";a { color: green }'
    >>> for rule in sheet:
    ...     print rule
    ...
    <cssutils.css.CSSCharsetRule object encoding='ascii' at 0x2ce7
    <cssutils.css.CSSStyleRule object selector=u'a' style=u'color:
    s=<cssutils.util._Namespaces object at 0x02CE7B30> at 0x2ce7d3

``for in`` is supported by :class:`~cssutils.css.CSSStyleSheet` and  :class:`~cssutils.css.CSSMediaRule` (iterating over the contained :class:`~cssutils.css.CSSRule` objects, :class:`~cssutils.css.CSSStyleDeclaration` (over the names of the contained :class:`~cssutils.css.Property` objects), ``~cssutils.css.CSSValueList`` (over the ``~cssutils.css.CSSValue`` objects in the list).


