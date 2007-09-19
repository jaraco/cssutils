# -*- coding: iso-8859-1 -*-
"""
testcases for cssutils.stylesheets.MediaList
"""
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-09-16 00:00:46 +0200 (So, 16 Sep 2007) $'
__version__ = '$LastChangedRevision: 359 $'

import xml.dom
import basetest
import cssutils.stylesheets

class MediaQueryTestCase(basetest.BaseTestCase):

    def setUp(self):
        super(MediaQueryTestCase, self).setUp()
        self.r = cssutils.stylesheets.MediaQuery()

    def test_mediaText(self):
        "MediaQuery.mediaText"
        tests = {
            u'all': u'all',
            }
        self.do_equal_r(tests, att='mediaText')

        tests = {
            u'': xml.dom.SyntaxErr,
            }
        self.do_raise_r(tests, att='_setMediaText')

    def test_mediaType(self):
        "MediaList.mediaType"
        mq = cssutils.stylesheets.MediaQuery()

        self.assertEqual(u'', mq.mediaText)

        for mt in cssutils.stylesheets.MediaQuery.MEDIA_TYPES:
            mq.mediaType = mt
            self.assertEqual(mq.mediaType, mt)
            mq.mediaType = mt.upper()
            self.assertEqual(mq.mediaType, mt)

        mt = u'3D-UNKOwn-MEDIAtype0123'
        mq.mediaType = mt
        self.assertEqual(mq.mediaType, mt.lower())

#    def test_comments(self):
#        "MediaQuery.mediaText comments"
#        tests = {
#            u'/*1*/tv/*2*/, /*3*/handheld/*4*/, tv': None,
#            }
#        self.do_equal_r(tests, att='mediaText')

    def test_reprANDstr(self):
        "MediaQuery.__repr__(), .__str__()"
        mediaText='tv and (color)'

        s = cssutils.stylesheets.MediaQuery(mediaText=mediaText)

        self.assert_(mediaText in str(s))

        s2 = eval(repr(s))
        self.assertEqual(mediaText, s2.mediaText)
        self.assert_(isinstance(s2, s.__class__))


if __name__ == '__main__':
    import unittest
    unittest.main()
