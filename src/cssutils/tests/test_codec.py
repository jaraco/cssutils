"""
testcases for cssutils.codec
"""
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-08-20 22:09:16 +0200 (Mo, 20 Aug 2007) $'
__version__ = '$LastChangedRevision: 258 $'

import unittest

from cssutils import codec

class CodecTestCase(unittest.TestCase):

    def test_detectencoding(self):
        self.assert_(codec._detectencoding('') is None)
        self.assert_(codec._detectencoding('\xef') is None)
        self.assertEqual(codec._detectencoding('\xef\x33'), "utf-8")
        self.assert_(codec._detectencoding('\xef\xbb') is None)
        self.assertEqual(codec._detectencoding('\xef\xbb\x33'), "utf-8")
        self.assertEqual(codec._detectencoding('\xef\xbb\xbf'), "utf-8-sig")
        self.assert_(codec._detectencoding('\xff') is None)
        self.assertEqual(codec._detectencoding('\xff\x33'), "utf-8")
        self.assert_(codec._detectencoding('\xff\xfe') is None)
        self.assertEqual(codec._detectencoding('\xff\xfe\x33'), "utf-16")
        self.assert_(codec._detectencoding('\xff\xfe\x00') is None)
        self.assertEqual(codec._detectencoding('\xff\xfe\x00\x33'), "utf-16")
        self.assertEqual(codec._detectencoding('\xff\xfe\x00\x00'), "utf-32")
        self.assert_(codec._detectencoding('\x00') is None)
        self.assertEqual(codec._detectencoding('\x00\x33'), "utf-8")
        self.assert_(codec._detectencoding('\x00\x00') is None)
        self.assertEqual(codec._detectencoding('\x00\x00\x33'), "utf-8")
        self.assert_(codec._detectencoding('\x00\x00\xfe') is None)
        self.assertEqual(codec._detectencoding('\x00\x00\x00\x33'), "utf-8")
        self.assertEqual(codec._detectencoding('\x00\x00\x00@'), "utf-32-be")
        self.assertEqual(codec._detectencoding('\x00\x00\xfe\xff'), "utf-32")
        self.assert_(codec._detectencoding('@') is None)
        self.assertEqual(codec._detectencoding('@\x33'), "utf-8")
        self.assert_(codec._detectencoding('@\x00') is None)
        self.assertEqual(codec._detectencoding('@\x00\x33'), "utf-8")
        self.assert_(codec._detectencoding('@\x00\x00') is None)
        self.assertEqual(codec._detectencoding('@\x00\x00\x33'), "utf-8")
        self.assertEqual(codec._detectencoding('@\x00\x00\x00'), "utf-32-le")
        self.assert_(codec._detectencoding('@c') is None)
        self.assert_(codec._detectencoding('@ch') is None)
        self.assert_(codec._detectencoding('@cha') is None)
        self.assert_(codec._detectencoding('@char') is None)
        self.assert_(codec._detectencoding('@chars') is None)
        self.assert_(codec._detectencoding('@charse') is None)
        self.assert_(codec._detectencoding('@charset') is None)
        self.assert_(codec._detectencoding('@charset ') is None)
        self.assert_(codec._detectencoding('@charset "') is None)
        self.assert_(codec._detectencoding('@charset "x') is None)
        self.assertEqual(codec._detectencoding('@charset ""'), "")
        self.assertEqual(codec._detectencoding('@charset "x"'), "x")
        self.assert_(codec._detectencoding("@", False) is None)
        self.assertEqual(codec._detectencoding("@", True), "utf-8")
        self.assert_(codec._detectencoding("@c", False) is None)
        self.assertEqual(codec._detectencoding("@c", True), "utf-8")

    def test_fixencoding(self):
        s = u'@charset "'
        self.assert_(codec._fixencoding(s, u"utf-8") is None)

        s = u'@charset "x'
        self.assert_(codec._fixencoding(s, u"utf-8") is None)

        s = u'@charset "x'
        self.assertEqual(codec._fixencoding(s, u"utf-8", True), s)

        s = u'@charset x'
        self.assertEqual(codec._fixencoding(s, u"utf-8"), s)

        s = u'@charset "x"'
        self.assertEqual(codec._fixencoding(s, u"utf-8"), s.replace('"x"', '"utf-8"'))

if __name__ == '__main__':
    import unittest
    unittest.main()
