what is it
----------
A Python package to parse and build CSS Cascading Style Sheets.
(Not a renderer though!)

about this release
------------------
0.9.8 is the latest stable release.

main changes
------------
since last stable release 0.9.7
	- Python 3 support. Sadly Python 2.4 support is gone with this release as
	  it is too complex to have 3.x and <=2.4 support.
	- some API changes mainly for CSS values. Removed already DEPRECATED stuff.
	- validation can be disabled now
	- performance improvements
	- lots of minor bugfixes and improvements
	- moved source code from Google Code over to BitBucket
	
	see the CHANGELOG for a complete list of changes.

since last alpha release:
    - FEATURE: Feature Request (#4) to be able to disable validation of a stylesheet has been implemented. Add Parameter ``validate=False`` for parsing (only for parsing of stylesheets not single styledeclarations yet).

    + BUGFIX: Fixed #5 Unicode escaping inside strings. Thanks to Simon Sapin
    + BUGFIX: The integer is optional in counter-reset and counter-increment, and not only on the first counter. Thanks to Simon Sapin
    + BUGFIX: Fix for unicode replacements by Denis Bilenko, thanks!  https://bitbucket.org/cthedot/cssutils/pull-request/1/fix-a-bug-in-regex-which-accidentally

    - IMPROVEMENT: ``parseStyle`` moved to CSSParser, thanks to Simon Sapin

license
-------
cssutils is published under the LGPL version 3 or later, see
http://cthedot.de/cssutils/

If you have other licensing needs please let me know.

download
--------
For download options see http://cthedot.de/cssutils/

cssutils needs Python 2.5 and higher or Jython 2.5 and higher (tested with
Python 2.7.2(x64), 2.6.5(x64), 2.5.4(x32) and Jython 2.5.1 on Win7x64
only). Python 2.4 is no longer supported.


Bug reports (via BitBucket), comments, etc are very much appreciated! Thanks.

Christof