=========
profiles
=========

.. index::
    single: profile

``cssutils.profile``
====================
A global object ``cssutils.profile`` is used for validation of all properties. It is an instance of :class:`cssutils.profiles.Profiles`. Add or remove new profile definitions here.

Most important method is :meth:`cssutils.profiles.Profiles.addProfile` (use ``cssutils.profile.addProfile``) to add new properties to cssutils and the setting of ``defaultProfiles``.



Example of how to add a new profile::

    >>> import cssutils
    >>> sheet = cssutils.parseString('x { -test-custommacro: x }')
    >>> print sheet.cssRules[0].style.getProperties()[0].valid
    False
    >>> M1 = {
    ...      'testvalue': 'x'
    ...      }
    >>> P1 = {
    ...    '-test-tokenmacro': '({num}{w}){1,2}',
    ...    '-test-macro': '{ident}|{percentage}',
    ...    '-test-custommacro': '{testvalue}',
    ...    # custom validation function
    ...    '-test-funcval': lambda(v): int(v) > 0
    ...      }
    >>> cssutils.profile.addProfile('test', P1, M1)
    >>> sheet = cssutils.parseString('x { -test-custommacro: x }')
    >>> print sheet.cssRules[0].style.getProperties()[0].valid
    True

An additional per CSSStyleSheet setting of a profile may be added soon.

**Please note: This might change again, but only slightly as it has been refactored in 0.9.6a2.**


.. index::
    single: defaultProfiles
    single: macros
    single: properties

``cssutils.profiles.macros`` and ``cssutils.profiles.properties``
=================================================================
Two dictionaries which contain macro and property definitions for the predefined property profiles.

Both use the additional macros defined in ``Profiles._TOKEN_MACROS`` and ``Profiles._MACROS`` which contain basic macros for definition of new properties. Things like `ident`, `name` or `hexcolor` are defined there and may be used in any new property definition as these two macro sets defined in ``Profiles`` are added to any custom macro definition given. You may overwrite these basic macros with your own macros or simply define your own macros and use only these.

Use ``cssutils.profiles.macros`` if you need any other predefined macro or ``cssutils.profiles.properties`` if you want to add any known property to your custom property profile.


``cssutils.profiles.Profiles``
==============================
.. autoclass:: cssutils.profiles.Profiles
    :members:
    :inherited-members:
