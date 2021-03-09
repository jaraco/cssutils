.. module:: cssutils.parse

===========
parsing CSS
===========
Options to parse a given stylesheet: Get an instance of :class:`cssutils.CSSParser` and use the provided ``parse*`` methods or for simpler parsing use the ``parse*`` `convienience functions`_.



Convienience Functions
======================
Shortcuts for initializing a new :class:`cssutils.CSSParser` and use its ``parse*`` methods. Parsing a stylesheet this way does not raise any exceptions if an error occurs but parses CSS as defined in the specifications. If you need advanced parser handline use :class:`cssutils.CSSParser` directly.

``parseString``
---------------
.. autofunction:: cssutils.parseString(cssText, encoding=None, href=None, media=None, title=None, validate=None)

``parseFile``
-------------
.. autofunction:: cssutils.parseFile(filename, encoding=None, href=None, media=None, title=None, validate=None)

``parseUrl``
------------
.. autofunction:: cssutils.parseUrl(href, encoding=None, media=None, title=None, validate=None)


Working with inline styles
==========================
``parseStyle``
--------------
.. autofunction:: cssutils.parseStyle(cssText, encoding='utf-8')


``CSSParser``
=============
The parser is reusable.

.. autoclass:: cssutils.CSSParser
   :members:
   :inherited-members:
   

The URL Fetcher
---------------
If you want to control how imported stylesheets are read you may define a custom URL fetcher (e.g. would be needed on Google AppEngine as urllib2, which is normally used, is not available. A GAE specific fetcher is included in cssutils from 0.9.5a1 though.)

A custom URL fetcher may be used during parsing via ``CSSParser.setFetcher(fetcher)`` (or as an init parameter). The so customized parser is reusable. The fetcher is called when an ``@import`` rule is found and the referenced stylesheet is about to be retrieved.

Example::

    def fetcher(url):
        return 'ascii', '/*test*/'

    parser = cssutils.CSSParser(fetcher=fetcher)
    parser.parse...

Example 2 with a fetcher returning a unicode string::

    def fetcher(url):
        return None, u'/*test*/'

    parser = cssutils.CSSParser(fetcher=fetcher)
    parser.parse...

To omit parsing of imported sheets just define a fetcher like ``lambda url: None`` (A single ``None`` is sufficient but returning ``None, None`` would be clearer).

You may also define a fetcher which overrides the internal encoding for imported sheets with a fetcher that returns a (normally HTTP) encoding depending e.g on the URL.
