"""
testcases for cssutils.codec
"""
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-08-20 22:09:16 +0200 (Mo, 20 Aug 2007) $'
__version__ = '$LastChangedRevision: 258 $'

import unittest

import codecs

from cssutils import codec


try:
    codecs.lookup("utf-32")
except LookupError:
    haveutf32 = False
else:
    haveutf32 = True


class Queue(object):
    """
    queue: write bytes at one end, read bytes from the other end
    """
    def __init__(self):
        self._buffer = ""

    def write(self, chars):
        self._buffer += chars

    def read(self, size=-1):
        if size<0:
            s = self._buffer
            self._buffer = ""
            return s
        else:
            s = self._buffer[:size]
            self._buffer = self._buffer[size:]
            return s


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

    def test_decoder(self):
        def checkauto(encoding, input=u'@charset "x";g\xfcrk\u20ac{}'):
            outputencoding = encoding
            if outputencoding == "utf-8-sig":
                outputencoding = "utf-8"
            # Check stateless decoder
            d = codecs.getdecoder("css")
            self.assertEqual(d(input.encode(encoding))[0], input.replace('"x"', '"%s"' % outputencoding))

            # Check stateless decoder with specified encoding
            self.assertEqual(d(input.encode(encoding), encoding=encoding)[0], input.replace('"x"', '"%s"' % outputencoding))

            # Check incremental decoder
            id = codecs.getincrementaldecoder("css")()
            self.assertEqual("".join(id.iterdecode(input.encode(encoding))), input.replace('"x"', '"%s"' % outputencoding))

            # Check incremental decoder with specified encoding
            id = codecs.getincrementaldecoder("css")(encoding)
            self.assertEqual("".join(id.iterdecode(input.encode(encoding))), input.replace('"x"', '"%s"' % outputencoding))

            # Check stream reader
            q = Queue()
            sr = codecs.getreader("css")(q)
            result = []
            for c in input.encode(encoding):
                q.write(c)
                result.append(sr.read())
            self.assertEqual("".join(result), input.replace('"x"', '"%s"' % outputencoding))

        # Autodetectable encodings
        checkauto("utf-8-sig")
        checkauto("utf-16")
        checkauto("utf-16-le")
        checkauto("utf-16-be")
        if haveutf32:
            checkauto("utf-32")
            checkauto("utf-32-le")
            checkauto("utf-32-be")

        def checkdecl(encoding, input=u'@charset "%s";g\xfcrk{}'):
            # Check stateless decoder with encoding autodetection
            d = codecs.getdecoder("css")
            input = input % encoding
            self.assertEqual(d(input.encode(encoding))[0], input)

            # Check stateless decoder with specified encoding
            self.assertEqual(d(input.encode(encoding), encoding=encoding)[0], input)

            # Check incremental decoder with encoding autodetection
            id = codecs.getincrementaldecoder("css")()
            self.assertEqual("".join(id.iterdecode(input.encode(encoding))), input)

            # Check incremental decoder with specified encoding
            id = codecs.getincrementaldecoder("css")(encoding)
            self.assertEqual("".join(id.iterdecode(input.encode(encoding))), input)

        # Use correct declaration
        checkdecl("utf-8")
        checkdecl("iso-8859-1", u'@charset "%s";g\xfcrk')
        checkdecl("iso-8859-15")
        checkdecl("cp1252")

        # No recursion
        self.assertRaises(ValueError, '@charset "css";div{}'.decode, "css")


if __name__ == '__main__':
    import unittest
    unittest.main()
