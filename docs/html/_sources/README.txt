======
README
======
-------------------------------------------------------
cssutils: CSS Cascading Style Sheets library for Python
-------------------------------------------------------
:Copyright: 2004-2009 Christof Hoeke

Overview
========
A Python package to parse and build CSS Cascading Style Sheets. DOM only, not any rendering facilities!

Based upon and partly implementing the following specifications :

`CSS 2.1 <http://www.w3.org/TR/CSS21/>`__
    General CSS rules and properties are defined here
`CSS 2.1 Errata  <http://www.w3.org/Style/css2-updates/CR-CSS21-20070719-errata.html>`__
    A few errata, mainly the definition of CHARSET_SYM tokens
`CSS3 Module: Syntax <http://www.w3.org/TR/css3-syntax/>`__
    Used in parts since cssutils 0.9.4. cssutils tries to use the features from CSS 2.1 and CSS 3 with preference to CSS3 but as this is not final yet some parts are from CSS 2.1
`MediaQueries <http://www.w3.org/TR/css3-mediaqueries/>`__
    MediaQueries are part of ``stylesheets.MediaList`` since v0.9.4, used in @import and @media rules.
`Namespaces <http://dev.w3.org/csswg/css3-namespace/>`__
    Added in v0.9.1, updated to definition in CSSOM in v0.9.4, updated in 0.9.5 for dev version
`Selectors <http://www.w3.org/TR/css3-selectors/>`__
    The selector syntax defined here (and not in CSS 2.1) should be parsable with cssutils (*should* mind though ;) )

`DOM Level 2 Style CSS <http://www.w3.org/TR/DOM-Level-2-Style/css.html>`__
    DOM for package css
`DOM Level 2 Style Stylesheets <http://www.w3.org/TR/DOM-Level-2-Style/stylesheets.html>`__
    DOM for package stylesheets
`CSSOM <http://dev.w3.org/csswg/cssom/>`__
    A few details (mainly the NamespaceRule DOM) is taken from here. Plan is to move implementation to the stuff defined here which is newer but still no REC so might change anytime...


The cssutils tokenizer is a customized implementation of `CSS3 Module: Syntax (W3C Working Draft 13 August 2003) <http://www.w3.org/TR/css3-syntax/>`_ which itself is based on the CSS 2.1 tokenizer. It tries to be as compliant as possible but uses some (helpful) parts of the CSS 2.1 tokenizer.

I guess cssutils is neither CSS 2.1 nor CSS 3 compliant but tries to at least be able to parse both grammars including some more real world cases (some CSS hacks are actually parsed and serialized). Both official grammars are not final nor bugfree but still feasible. cssutils aim is not to be fully compliant to any CSS specification (the specifications seem to be in a constant flow anyway) but cssutils *should* be able to read and write as many as possible CSS stylesheets "in the wild" while at the same time implement the official APIs which are well documented. Some minor extensions are provided as well.

Please visit http://cthedot.de/cssutils/ or http://code.google.com/p/cssutils/ for more details.

There is also a low-traffic `cssutils discussion group <http://groups.google.com/group/cssutils>`_.


license
=======
Copyright 2005 - 2009 Christof Hoeke

cssutils is published under the LGPL 3 or later

cssutils is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

cssutils is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with cssutils. If not, see http://www.gnu.org/licenses.


installation
============
From 0.9.0 cssutils uses EasyInstall. Please find installation instructions and more information about EasyInstall from http://peak.telecommunity.com/DevCenter/EasyInstall#installation-instructions.

After installing EasyInstall simply use::

    > easy_install cssutils

to install the latest version of cssutils.

Alternatively download the provided source distribution. Expand the file and from a command line install with::

    > python setup.py install

Before using EasyInstall the first time or using the sdist please remove any old version which should be installed at PYTHONDIR/Lib/site-packages/cssutils.


kind request
============
cssutils is far from being perfect or even complete. If you find any bugs (especially specification violations) or have problems or suggestions please put them in the `Issue Tracker <http://code.google.com/p/cssutils/issues/list>`_ at Google.


thanks
======
Thanks to Walter Doerwald for patches, help and discussion. Thanks to Kevin D. Smith for the value validating module. Thanks also to Cory Dodt, Tim Gerla and James Dobson for helpful suggestions and code patches.

