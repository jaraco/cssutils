"""Testcases for cssutils.scripts.csscombine"""
__version__ = '$Id$'

from cssutils.scripts import csscombine
import basetest
import cssutils
import os
import urllib

class CSSCombine(basetest.BaseTestCase):

    C = '@namespace s2"uri";s2|sheet-1{top:1px}s2|sheet-2{top:2px}proxy{top:3px}' 


    def test_combine(self):
        "scripts.csscombine"        
        # path, SHOULD be keyword argument!
        csspath = os.path.join(os.path.dirname(__file__), '..', '..', 
                               'sheets', 'csscombine-proxy.css')
        combined = csscombine(csspath)
        self.assertEqual(combined, self.C)
        combined = csscombine(path=csspath, targetencoding='ascii')
        self.assertEqual(combined, '@charset "ascii";' + self.C)

        # url
        cssurl = u'file:' + urllib.pathname2url(os.path.abspath(csspath))
        combined = csscombine(url=cssurl)
        self.assertEqual(combined, self.C)
        combined = csscombine(url=cssurl, targetencoding='ascii')
        self.assertEqual(combined, '@charset "ascii";' + self.C)

        cssutils.log.raiseExceptions = True 


if __name__ == '__main__':
    import unittest
    unittest.main()
