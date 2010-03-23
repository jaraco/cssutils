====================
scripts
====================


The provided scripts are available as a standalone script which is installed in the default PYTHONHOME/scripts directory. Additionally an API for the functionality of the scripts is provided for use in programs.

``CSSParse``
============
Script version of ``cssutils.parseString()``, ``cssutils.parseFile()`` and ``cssutils.parseUrl()``.

Usage: cssparse-script.py [options] filename1.css [filename2.css ...]
        [>filename_combined.css] [2>parserinfo.log]

Options:
  -h, --help            show this help message and exit
  -s, --string          parse given string
  -u URL, --url=URL     parse given url
  -e ENCODING, --encoding=ENCODING
                        encoding of the file or override encoding found
  -m, --minify          minify parsed CSS
  -d, --debug           activate debugging output


``CSSCapture``
==============
``CSSCapture`` downloads all referenced CSS stylesheets of a given URL and saves them to a given target directory.

programmatic use
----------------
example::

    >>> url = 'http://cthedot.de'
    >>> from cssutils.script import CSSCapture
    >>> capturer = CSSCapture(ua=None, log=None, defaultloglevel=logging.INFO)
    >>> stylesheetlist = capturer.capture(url)
    >>> print stylesheetlist
    [cssutils.css.CSSStyleSheet(href=u'http://cthedot.de/css/default.css', media=None, title=None),
     cssutils.css.CSSStyleSheet(href=u'http://cthedot.de/static/alternate1.css', media=None, title=u'red'),
     cssutils.css.CSSStyleSheet(href=u'http://cthedot.de/static/alternate2.css', media=None, title=u'blue')]

script use
----------
Usage: csscapture-script.py [options] URL

Options:
  -h, --help            show this help message and exit
  -d, --debug           show debug messages during capturing
  -m, --minified        saves minified version of captured files
  -n, --notsave         if given files are NOT saved, only log is written
  -s SAVETO, --saveto=SAVETO
                        saving retrieved files to "saveto", defaults to "_CSSCapture_SAVED"
  -u UA, --useragent=UA
                        useragent to use for request of URL, default is urllib2s default

The following example outputs a list of stylesheets found with title and href of the found stylesheet. (``PYTHONHOME/Scripts`` should be on your ``PATH``.  Additional log output is not shown.)::

    > csscapture http://cthedot.de/static/cssutils/examples/capturefrom.html -n

    1.
        encoding: 'utf-8'
        title: u'html 1: link1'
        href: u'http://cthedot.de/css/default.css'
    2.
        encoding: 'utf-8'
        title: u'html 2: style1'
        href: None
    3.
        encoding: 'utf-8'
        title: u'HTML 2.1: @import'
        href: u'http://cthedot.de/static/cssutils/examples/inlineimport1.css'
    4.
        encoding: 'utf-8'
        title: u'html 3: link2'
        href: u'http://cthedot.de/static/cssutils/examples/link1.css'
    5.
        encoding: 'utf-8'
        title: u'link1: s1'
        href: u'http://cthedot.de/static/cssutils/examples/linkimport1.css'
    6.
        encoding: 'utf-8'
        title: None
        href: u'http://cthedot.de/static/cssutils/examples/css/linkimportimport1.css'
    7.
        encoding: 'utf-8'
        title: None
        href: u'http://cthedot.de/static/cssutils/examples/css/linkimportimport2.css'
    8.
        encoding: 'iso-8859-1'
        title: u'link1: s2'
        href: u'http://cthedot.de/static/cssutils/examples/linkimport2.css'
    9.
        encoding: 'utf-8'
        title: u'html 4: style2'
        href: None
    10.
        encoding: 'utf-8'
        title: None
        href: u'http://cthedot.de/static/cssutils/examples/css/inlineimport2.css'
    11.
        encoding: 'utf-8'
        title: None
        href: u'http://cthedot.de/static/cssutils/examples/css/inlineimportimport1.css'

``CSSCombine``
==============
``csscombine`` may be used to combine several sheets loaded from a main sheet via @import rules. Nested @import rules are resolved from cssutils 0.9.6a1.

The resulting combined sheet (optionally minified) is send to stdout, info and error messages are handled by the normal cssutils log.

``csscombine`` may also be used to change the encoding of the stylesheet if a target encoding is given.

programmatic use
----------------
example::

	>>> from cssutils.script import csscombine
	>>> proxypath = 'sheets/import.css'
	>>> print csscombine(path=proxypath, sourceencoding=None, targetencoding='utf-8', minify=False)
	INFO    Combining files from None
	INFO    Processing @import u'import/import2.css'
	INFO    Processing @import u'../import3.css'
	INFO    @import: Adjusting paths for u'../import3.css'
	INFO    Processing @import u'import-impossible.css'
	INFO    @import: Adjusting paths for u'import-impossible.css'
	WARNING Cannot combine imported sheet with given media as other rules then comments or stylerules found cssutils.css.CSSNamespaceRule(namespaceURI=u'y', prefix=u''), keeping u'@import "import-impossible.css" print;'
	INFO    @import: Adjusting paths for u'import/import2.css'
	INFO    Using target encoding: 'utf-8'
	@charset "utf-8";
	/* START @import "import/import2.css" */
	@import "import-impossible.css" print;
	/* START @import "../import3.css" */
	/* import3 */
	.import3 {
	    /* from ./import/../import3.css */
	    background: url(images/example3.gif);
	    background: url(images/example3.gif);
	    background: url(import/images2/example2.gif);
	    background: url(import/images2/example2.gif);
	    background: url(images/example3.gif)
	    }
	/* START @import "import-impossible.css" */
	.import2 {
	    /* sheets/import2.css */
	    background: url(http://example.com/images/example.gif);
	    background: url(//example.com/images/example.gif);
	    background: url(/images/example.gif);
	    background: url(import/images2/example.gif);
	    background: url(import/images2/example.gif);
	    background: url(images/example.gif);
	    background: url(images/example.gif)
	    }
	.import {
	    /* ./import.css */
	    background-image: url(images/example.gif)
	    }


script use
----------
Usage: csscombine-script.py [options] [path]

Options:
  -h, --help            show this help message and exit
  -u URL, --url=URL     URL to parse (path is ignored if URL given)
  -s SOURCEENCODING, --sourceencoding=SOURCEENCODING
                        encoding of input, defaulting to "css". If given
                        overwrites other encoding information like @charset
                        declarations
  -t TARGETENCODING, --targetencoding=TARGETENCODING
                        encoding of output, defaulting to "UTF-8"
  -m, --minify          saves minified version of combined files, defaults to
                        False