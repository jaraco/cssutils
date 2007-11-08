=============================================
                 cssutils
=============================================
---------------------------------------------
CSS Cascading Style Sheets library for Python
---------------------------------------------
:Author: $LastChangedBy$
:Copyright: 2004-2007 Christof Hoeke
:Date: $LastChangedDate$
:Version: (rev $LastChangedRevision$)

Overview
========
A Python package to parse and build CSS Cascading Style Sheets.

Based upon and partly implements the following specifications (DOM only, not any rendering facilities):

`DOM Level 2 Style CSS <http://www.w3.org/TR/DOM-Level-2-Style/css.html>`__
    DOM for package css
`DOM Level 2 Style Stylesheets <http://www.w3.org/TR/DOM-Level-2-Style/stylesheets.html>`__
    DOM for package stylesheets
`CSSOM <http://dev.w3.org/csswg/cssom/>`__
    A few details (mainly the NamespaceRule DOM) is taken from here. Plan is to move implementation to the stuff defined here which is newer but still no REC so might change anytime...

`CSS 2.1 <http://www.w3.org/TR/CSS21/>`__
    Rules and properties are defined here
`CSS 2.1 Errata  <http://www.w3.org/Style/css2-updates/CR-CSS21-20070719-errata.html>`__
    A few erratas, mainly the definition of CHARSET_SYM tokens
`CSS3 module: Syntax <http://www.w3.org/TR/css3-syntax/>`__
    Used in parts since cssutils 0.9.4 which basically tries to use the features from CSS 2.1 and CSS 3.
`MediaQueries <http://www.w3.org/TR/css3-mediaqueries/>`__
    MediaQueries are part of ``stylesheets.MediaList`` since v0.9.4, used in @import and @media rules.
`Namespaces <http://www.w3.org/TR/css3-namespace/>`__
    Added in v0.9.1 and updated to definition in CSSOM in v0.9.4
`Selectors <http://www.w3.org/TR/css3-selectors/>`__
    The selector syntax defined here (and not in CSS 2.1) should be parsable with cssutils (*should* mind though ;) )

Please visit http://cthedot.de/cssutils/ for full details.


license
=======
Published under the LGPL, see http://cthedot.de/cssutils/license.html


installation
============
From 0.9 cssutils uses EasyInstall. Please find installation instructions and more information about EasyInstall from http://peak.telecommunity.com/DevCenter/EasyInstall#installation-instructions.

After installing EasyInstall simple use::

    > easy_install cssutils

to install the latest version of cssutils.

Alternatively download the provided source distribution. Expand the file and from a command line install with::

    > python setup.py install

Before using EasyInstall the first time or using the sdist please remove any old version which should be installed at PYTHONDIR/Lib/site-packages/cssutils.


