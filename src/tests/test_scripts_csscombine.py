"""Testcases for cssutils.scripts.csscombine"""
__version__ = '$Id$'

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
        csspath = os.path.join(os.path.dirname(__file__), '..', '..', 
                               'sheets', 'csscombine-proxy.css')
        combined = csscombine(csspath)
        self.assertEqual(combined, self.C)
        combined = csscombine(path=csspath, targetencoding='ascii')
        self.assertEqual(combined, '@charset "ascii";' + self.C)

        # url
        cssurl = cssutils.helper.path2url(csspath)
        combined = csscombine(url=cssurl)
        self.assertEqual(combined, self.C)
        combined = csscombine(url=cssurl, targetencoding='ascii')
        self.assertEqual(combined, '@charset "ascii";' + self.C)

        # cssText
        cssText=open(csspath).read()
        combined = csscombine(cssText=cssText, href=cssurl)
        self.assertEqual(combined, self.C)
        combined = csscombine(cssText=cssText, href=cssurl, 
                              targetencoding='ascii')
        self.assertEqual(combined, '@charset "ascii";' + self.C)
 
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
        self.assertEqual(csscombine(cssText=cssText),
                         '@variables{c:#0f0}a{color:var(c)}')
        self.assertEqual(csscombine(cssText=cssText, 
                                    resolveVariables=True),
                         'a{color:#0f0}')

        # no minify
        self.assertEqual(csscombine(cssText=cssText, minify=False),
                         '@variables {\n    c: #0f0\n    }\n'
                         'a {\n    color: var(c)\n    }')
        self.assertEqual(csscombine(cssText=cssText, minify=False,  
                                    resolveVariables=True),
                         'a {\n    color: #0f0\n    }')
        

if __name__ == '__main__':
    import unittest
    unittest.main()
