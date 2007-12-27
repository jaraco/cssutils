"""
testcases for cssutils.css.CSSRuleList
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import basetest
import cssutils

class CSSRuleListTestCase(basetest.BaseTestCase):

    def test_init(self):
        "CSSRuleList init"
        r = cssutils.css.CSSRuleList()
        self.assertEqual(0, r.length)
        self.assertEqual(None, r.item(2))
        
        # subclasses list but all setting options like append, extend etc
        # need to be added to an instance of this class by a using class!
        self.assertRaises(NotImplementedError, r.append, 1)


if __name__ == '__main__':
    import unittest
    unittest.main()
