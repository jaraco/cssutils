"""Testcases for cssutils.scripts.csscombine"""

from cssutils.script import csscombine
import basetest
import cssutils
import os

class CSSCombine(basetest.BaseTestCase):

    C = '@namespace s2"uri";s2|sheet-1{top:1px}s2|sheet-2{top:2px}proxy{top:3px}' 

    def setUp(self):
        self._saved = cssutils.log.raiseExceptions
    
    def tearDown(self):
        cssutils.log.raiseExceptions = self._saved

    def test_combine(self):
        "scripts.csscombine()"
              
        # path, SHOULD be keyword argument!
        csspath = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                               'sheets', 'csscombine-proxy.css')
        combined = csscombine(csspath)
        self.assertEqual(combined, self.C.encode())
        combined = csscombine(path=csspath, targetencoding='ascii')
        self.assertEqual(combined, ('@charset "ascii";' + self.C).encode())

        # url
        cssurl = cssutils.helper.path2url(csspath)
        combined = csscombine(url=cssurl)
        self.assertEqual(combined, self.C.encode())
        combined = csscombine(url=cssurl, targetencoding='ascii')
        self.assertEqual(combined, ('@charset "ascii";' + self.C).encode())

        # cssText
        # TODO: really need binary or can handle str too?
        cssText=open(csspath, mode="rb").read()
        combined = csscombine(cssText=cssText, href=cssurl)
        self.assertEqual(combined, self.C.encode())
        combined = csscombine(cssText=cssText, href=cssurl, 
                              targetencoding='ascii')
        self.assertEqual(combined, ('@charset "ascii";' + self.C).encode())
 
    def test_combine_resolveVariables(self):
        "scripts.csscombine(minify=..., resolveVariables=...)"
        # no actual imports but checking if minify and resolveVariables work
        cssText = '''
        @variables {
            c: #0f0;
        }
        a {
            color: var(c);
        }
        '''
        # default minify
        self.assertEqual(csscombine(cssText=cssText,
                                    resolveVariables=False),
                         '@variables{c:#0f0}a{color:var(c)}'.encode())
        self.assertEqual(csscombine(cssText=cssText),
                         'a{color:#0f0}'.encode())

        # no minify
        self.assertEqual(csscombine(cssText=cssText, 
                                    minify=False,
                                    resolveVariables=False),
                         '@variables {\n    c: #0f0\n    }\na {\n    color: var(c)\n    }'.encode())
        self.assertEqual(csscombine(cssText=cssText, minify=False),
                         'a {\n    color: #0f0\n    }'.encode())
        

if __name__ == '__main__':
    import unittest
    unittest.main()
