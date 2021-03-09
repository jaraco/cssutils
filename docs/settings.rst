====================
extra settings
====================
A single and **experimental** setting currently only:

It is possible to at least parse sheets with Microsoft only property values for
 ``filter`` which start with ``progid:DXImageTransform.Microsoft.[...](``.
 
To enable these you need to set::

    >>> from cssutils import settings
    >>> settings.set('DXImageTransform.Microsoft', True)
    >>> cssutils.ser.prefs.useMinified()
    >>> text = 'a {filter: progid:DXImageTransform.Microsoft.BasicImage( rotation = 90 )}'
    >>> print cssutils.parseString(text).cssText
    a{filter:progid:DXImageTransform.Microsoft.BasicImage(rotation=90)}
    >>>

This currently is a **major hack** but if you like to minimize sheets in the wild which use this kind of CSS cssutils at least can parse and reserialize them.
Also you cannot reset this change until you restart your program.

As these filter values are case sensitive there are in no way normalized either.
Neither are values like ``expression(...)`` or ``alpha(...)`` anymore which are
parsable without settings this specific switch.
