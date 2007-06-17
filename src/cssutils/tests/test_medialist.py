# -*- coding: iso-8859-1 -*-
"""
testcases for cssutils.stylesheets.MediaList
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a1, $LastChangedRevision$'

import xml.dom

import basetest

import cssutils.stylesheets


class MediaListTestCase(basetest.BaseTestCase):

    def setUp(self):
        super(MediaListTestCase, self).setUp()
        self.r = cssutils.stylesheets.MediaList()


    def test_set(self):
        "MediaList.mediaText 1"
        ml = cssutils.stylesheets.MediaList()

        self.assertEqual(0, ml.length)
        self.assertEqual(u'all', ml.mediaText)

        ml.mediaText = u' print   , screen '        
        self.assertEqual(2, ml.length)
        self.assertEqual(u'print, screen', ml.mediaText)

        ml.mediaText = u' print , all  , screen '        
        self.assertEqual(1, ml.length)
        self.assertEqual(u'all', ml.mediaText)

        self.assertRaises(xml.dom.InvalidCharacterErr,
                          ml._setMediaText, u'test')

    def test_append(self):
        "MediaList.append() 1"
        ml = cssutils.stylesheets.MediaList()

        ml.appendMedium(u'print')
        self.assertEqual(1, ml.length)
        self.assertEqual(u'print', ml.mediaText)

        ml.appendMedium(u'screen')
        self.assertEqual(2, ml.length)
        self.assertEqual(u'print, screen', ml.mediaText)

        # automatic del and append!        
        ml.appendMedium(u'print')
        self.assertEqual(2, ml.length)
        self.assertEqual(u'screen, print', ml.mediaText)

        # automatic del and append!        
        ml.appendMedium(u'SCREEN')
        self.assertEqual(2, ml.length)
        self.assertEqual(u'print, screen', ml.mediaText)

    def test_appendAll(self):
        "MediaList.append() 2"
        ml = cssutils.stylesheets.MediaList()
        ml.appendMedium(u'print')
        ml.appendMedium(u'tv')
        self.assertEqual(2, ml.length)
        self.assertEqual(u'print, tv', ml.mediaText)

        ml.appendMedium(u'all')
        self.assertEqual(1, ml.length)
        self.assertEqual(u'all', ml.mediaText)

        ml.appendMedium(u'print')
        self.assertEqual(1, ml.length)
        self.assertEqual(u'all', ml.mediaText)

        self.assertRaises(xml.dom.InvalidCharacterErr, ml.appendMedium, u'test')

    def test_delete(self):
        "MediaList.deleteMedium()"
        ml = cssutils.stylesheets.MediaList()

        self.assertRaises(xml.dom.NotFoundErr, ml.deleteMedium, u'all')
        self.assertRaises(xml.dom.NotFoundErr, ml.deleteMedium, u'test')

        ml.appendMedium(u'print')
        ml.deleteMedium(u'print')
        ml.appendMedium(u'tV')
        ml.deleteMedium(u'Tv')
        self.assertEqual(0, ml.length)
        self.assertEqual(u'all', ml.mediaText)

    def test_item(self):
        "MediaList.item()"
        ml = cssutils.stylesheets.MediaList()
        ml.appendMedium(u'print')
        ml.appendMedium(u'screen')

        self.assertEqual(u'print', ml.item(0))
        self.assertEqual(u'screen', ml.item(1))
        self.assertEqual(None, ml.item(2))
    
    def test_handheld(self):
        "MediaList handheld"
        ml = cssutils.stylesheets.MediaList()

        ml.mediaText = u' handheld , all  , screen '        
        self.assertEqual(1, ml.length)
        # keeps all explicitly set incl ,
        self.assertEqual(5, len(ml.seq)) # ?
        self.assertEqual(u'handheld, all', ml.mediaText)

    def test_mediaText(self):
        "MediaList.mediaText 2"
        tests = {
            u'': u'all',
            u'ALL': u'all',
            u'Tv': u'tv',
            u'all': None,
            u'all, handheld': None,
            u'tv': None,
            u'tv, handheld, print': None,
            }
        self.do_equal_r(tests, att='mediaText')

        tests = {
            u'all;': xml.dom.SyntaxErr,
            u'UNKNOWN': xml.dom.SyntaxErr,
            }
        self.do_raise_p(tests)

    def test_comments(self):
        "MediaList.mediaText comments"
        tests = {
            u'/*1*/tv/*2*/, /*3*/handheld/*4*/, tv': None,
            }
        self.do_equal_r(tests, att='mediaText')

        
if __name__ == '__main__':
    import unittest
    unittest.main() 