"""Testcase for cssutils imports"""

before = len(locals()) # to check is only exp amount is imported
from cssutils import *
after = len(locals()) # to check is only exp amount is imported

import unittest

class CSSutilsImportTestCase(unittest.TestCase):

    def test_import_all(self):
        "from cssutils import *"
        import cssutils

        act = globals()
        exp = {'CSSParser': CSSParser,
               'CSSSerializer': CSSSerializer,
               'css': cssutils.css,
               'stylesheets': cssutils.stylesheets,
        }
        exptotal = before + len(exp) + 1
        # imports before + * + "after"
        self.assert_(after == exptotal, 'too many imported')

        found = 0
        for e in exp:
            self.assert_(e in act, '%s not found' %e)
            self.assert_(act[e] == exp[e], '%s not the same' %e)
            found += 1
        self.assert_(found == len(exp))

if __name__ == '__main__':
    import unittest
    unittest.main()
