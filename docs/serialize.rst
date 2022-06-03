.. module:: cssutils.serialize

.. index::
    single: ser, cssutils.ser
    object: cssutils.ser

===============
serializing CSS
===============
To serialize any stylesheet use::

	print sheet.cssText
	
Also most other objects have a similar property which contains the *text* content of each object. Some use a slightly different name (e.g. ``selectorText``) but all use the global serializer::

	>>> sheet = cssutils.parseString('a, b { color: green }')
	>>> print sheet.cssRules[0].cssText
	a, b {
	    color: green
	    }
	>>> print sheet.cssRules[0].selectorText
	a, b
	>>> print sheet.cssRules[0].selectorList[1].selectorText
	b


.. _Preferences:

.. index::
    single: cssutils.ser.prefs
    object: cssutils.ser.prefs

``Preferences``
===============
Quite a few preferences of the cssutils serializer may be tweaked.

To set a preference use::

    cssutils.ser.prefs.PREFNAME = NEWVALUE

Preferences are always used *globally*, so for all stylesheets until preferences are set again.


.. autoclass:: cssutils.serialize.Preferences
   :members:
   :inherited-members:



``CSSSerializer``
=================
There is a single global serializer used throughout the library. You may configure it by setting specific Preferences_ or completely replace it with your own.

A custom serializer must implement all methods the default one provides. Easiest would be to subclass :class:`cssutils.serialize.CSSSerializer`.

To set a new serializer, use::

    cssutils.setSerializer(serializer)

You may also set ``cssutils.ser`` directly but the above method is the preferred one.

For most cases adjusting the ``cssutils.ser.prefs`` of the default serializer should be sufficient though.

.. autoclass:: cssutils.serialize.CSSSerializer


