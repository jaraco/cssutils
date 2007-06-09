"""
testcases for cssutils.css.CSSRuleList
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a1, SVN revision $LastChangedRevision$'


import basetest

import cssutils


class CSSRuleListTestCase(basetest.BaseTestCase):

    def test_init(self):
        "CSSRuleList init"
        r = cssutils.css.CSSRuleList()
        self.assertEqual(0, r.length)
        self.assertEqual(None, r.item(2))

        # subclasses list!
        r.append(0)
        r.append(1)
        self.assertEqual(2, r.length)
        self.assertEqual(1, r.item(1))
        self.assertEqual(None, r.item(2))


if __name__ == '__main__':
    import unittest
    unittest.main() 