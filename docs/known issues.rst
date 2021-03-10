Known Issues
============

- validation is not complete. Properties using ``calc()`` for example will be reported invalid but may well be valid. They are *wellformed* however and will be parsed and serialized properly.

- comments may not survive parsing in all cases

- ``CSSStyleSheet.cssText`` is a serialized byte string (**not** unicode string) currently. This may change in the future.

- ``CSS2Properties`` not implemented completely (setting a shorthand property does not set related properties like setting margin does not set margin-left etc). Also the return values are not as defined in the specification as no normalizing is done yet. Prefer to use ``style['property']`` over ``style.property``.

- The ``seq`` attribute of most classes does not hinder you to add invalid items. It will probably become readonly. **Never write to it!**

   **Content of ``seq`` will most likely change completely, seq is more of an internal property and should not be used in client code yet**

- although cssutils tries to preserve CSS hacks not all are (and some - mainly syntactically invalid ones - will probably never be). The following hacks are known to **not** be preserved:

  star hack (without any whitespace)
    ``*html`` syntactically invalid
  star7 hack (without any whitespace)
    ``html*#test-span`` (IMHO invalidated by the missing WS between html and "*")

  The main problem for cssutils users is that some stylesheets in the wild are not parsable without loosing some information, a pretty print for these sheets is simply not possible with cssutils (actually with hardly any css parser...).

  Generally **syntactically valid (wellformed) stylesheets** should be preserved completely (otherwise it will be a bug in cssutils itself). Invalid stylesheets will probably loose some information like to above ``*html`` hack. Most of these hacks may be rewritten while still be working, e.g. ``* html`` should work same to ``*html``. Until cssutils 0.9.5b2 the invalid IE-specific CSS hack using ``$propertyname`` was preserved but its usage was already discouraged (and if e.g. specifying ``color`` and ``$color`` these properties are **not the same** for cssutils (but are for IE...).
  **These kind of invalid hacks are not kept during parsing anymore since cssutils 0.9.5b3!**
  In almost any case it is possible to use at least syntactically valid CSS while still working around different browser implementations.

- when PyXML is installed not all tests may run through (see issue #34 for details) as PyXMLs implementation of ``xml.dom.DOMException`` differs from the default (minidom and I guess others) implemtation. Nothing really to worry about...
