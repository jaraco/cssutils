.. image:: https://img.shields.io/pypi/v/cssutils.svg
   :target: https://pypi.org/project/cssutils

.. image:: https://img.shields.io/pypi/pyversions/cssutils.svg

.. image:: https://github.com/jaraco/cssutils/actions/workflows/main.yml/badge.svg
   :target: https://github.com/jaraco/cssutils/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. image:: https://readthedocs.org/projects/cssutils/badge/?version=latest
   :target: https://cssutils.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2024-informational
   :target: https://blog.jaraco.com/skeleton

.. image:: https://tidelift.com/badges/package/pypi/cssutils
   :target: https://tidelift.com/subscription/pkg/pypi-cssutils?utm_source=pypi-cssutils&utm_medium=readme


Overview
========
A Python package to parse and build CSS Cascading Style Sheets. DOM only, not any rendering facilities!

Based upon and partly implementing the following specifications :

`CSS 2.1rev1 <http://www.w3.org/TR/CSS2/>`__
    General CSS rules and properties are defined here
`CSS3 Module: Syntax <http://www.w3.org/TR/css3-syntax/>`__
    Used in parts since cssutils 0.9.4. cssutils tries to use the features from CSS 2.1 and CSS 3 with preference to CSS3 but as this is not final yet some parts are from CSS 2.1
`CSS Fonts Module Level 3 <http://www.w3.org/TR/css3-fonts/>`__
    Added changes and additional stuff (since cssutils v0.9.6)
`MediaQueries <http://www.w3.org/TR/css3-mediaqueries/>`__
    MediaQueries are part of ``stylesheets.MediaList`` since v0.9.4, used in @import and @media rules.
`Namespaces <http://dev.w3.org/csswg/css3-namespace/>`__
    Added in v0.9.1, updated to definition in CSSOM in v0.9.4, updated in 0.9.5 for dev version
`CSS3 Module: Pages Media <http://www.w3.org/TR/css3-page/>`__
    Most properties of this spec are implemented including MarginRules
`Selectors <http://www.w3.org/TR/css3-selectors/>`__
    The selector syntax defined here (and not in CSS 2.1) should be parsable with cssutils (*should* mind though ;) )
`CSS Backgrounds and Borders Module Level 3 <http://www.w3.org/TR/css3-background/>`__, `CSS3 Basic User Interface Module <http://www.w3.org/TR/css3-ui/#resize>`__, `CSS Text Level 3 <http://www.w3.org/TR/css3-text/>`__
    Some validation for properties included, mainly  `cursor`, `outline`, `resize`, `box-shadow`, `text-shadow`
`Variables <http://disruptive-innovations.com/zoo/cssvariables/>`__ / `CSS Custom Properties <http://dev.w3.org/csswg/css-variables/>`__
    Experimental specification of CSS Variables which cssutils implements partly. The vars defined in the newer CSS Custom Properties spec should in main parts be at least parsable with cssutils.

`DOM Level 2 Style CSS <http://www.w3.org/TR/DOM-Level-2-Style/css.html>`__
    DOM for package css. 0.9.8 removes support for CSSValue and related API, see PropertyValue and Value API for now
`DOM Level 2 Style Stylesheets <http://www.w3.org/TR/DOM-Level-2-Style/stylesheets.html>`__
    DOM for package stylesheets
`CSSOM <http://dev.w3.org/csswg/cssom/>`__
    A few details (mainly the NamespaceRule DOM) are taken from here. Plan is to move implementation to the stuff defined here which is newer but still no REC so might change anytime...

The cssutils tokenizer is a customized implementation of `CSS3 Module: Syntax (W3C Working Draft 13 August 2003) <http://www.w3.org/TR/css3-syntax/>`_ which itself is based on the CSS 2.1 tokenizer. It tries to be as compliant as possible but uses some (helpful) parts of the CSS 2.1 tokenizer.

I guess cssutils is neither CSS 2.1 nor CSS 3 compliant but tries to at least be able to parse both grammars including some more real world cases (some CSS hacks are actually parsed and serialized). Both official grammars are not final nor bugfree but still feasible. cssutils aim is not to be fully compliant to any CSS specification (the specifications seem to be in a constant flow anyway) but cssutils *should* be able to read and write as many as possible CSS stylesheets "in the wild" while at the same time implement the official APIs which are well documented. Some minor extensions are provided as well.


Compatibility
=============

cssutils is developed on modern Python versions. Check the package metadata
for compatibilty.

Beware, cssutils is known to be thread unsafe.


Example
=======

.. code-block:: python

    import cssutils

    css = '''/* a comment with umlaut &auml; */
            @namespace html "http://www.w3.org/1999/xhtml";
            @variables { BG: #fff }
            html|a { color:red; background: var(BG) }'''
    sheet = cssutils.parseString(css)

    for rule in sheet:
        if rule.type == rule.STYLE_RULE:
            # find property
            for property in rule.style:
                if property.name == 'color':
                    property.value = 'green'
                    property.priority = 'IMPORTANT'
                    break
            # or simply:
            rule.style['margin'] = '01.0eM' # or: ('1em', 'important')

    sheet.encoding = 'ascii'
    sheet.namespaces['xhtml'] = 'http://www.w3.org/1999/xhtml'
    sheet.namespaces['atom'] = 'http://www.w3.org/2005/Atom'
    sheet.add('atom|title {color: #000000 !important}')
    sheet.add('@import "sheets/import.css";')

    # cssutils.ser.prefs.resolveVariables == True since 0.9.7b2
    print sheet.cssText

results in::

	@charset "ascii";
	@import "sheets/import.css";
	/* a comment with umlaut \E4  */
	@namespace xhtml "http://www.w3.org/1999/xhtml";
	@namespace atom "http://www.w3.org/2005/Atom";
	xhtml|a {
	    color: green !important;
	    background: #fff;
	    margin: 1em
	    }
	atom|title {
	    color: #000 !important
	    }


Kind Request
============

cssutils is far from being perfect or even complete. If you find any bugs (especially specification violations) or have problems or suggestions please put them in the `Issue Tracker <https://github.com/jaraco/cssutils/issues>`_.


Thanks
======

Special thanks to Christof Höke for seminal creation of the library.

Thanks to Simon Sapin, Jason R. Coombs, and Walter Doerwald for patches, help and discussion. Thanks to Kevin D. Smith for the value validating module. Thanks also to Cory Dodt, Tim Gerla, James Dobson and Amit Moscovich for helpful suggestions and code patches. Thanks to Fredrik Hedman for help on port of encutils to Python 3.


For Enterprise
==============

Available as part of the Tidelift Subscription.

This project and the maintainers of thousands of other packages are working with Tidelift to deliver one enterprise subscription that covers all of the open source you use.

`Learn more <https://tidelift.com/subscription/pkg/pypi-cssutils?utm_source=pypi-cssutils&utm_medium=referral&utm_campaign=github>`_.
