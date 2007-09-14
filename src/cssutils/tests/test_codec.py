"""
testcases for cssutils.codec
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

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

    def test_detectencoding_str(self):
        self.assert_(codec._detectencoding_str('') is None)
        self.assert_(codec._detectencoding_str('\xef') is None)
        self.assertEqual(codec._detectencoding_str('\xef\x33'), "utf-8")
        self.assert_(codec._detectencoding_str('\xef\xbb') is None)
        self.assertEqual(codec._detectencoding_str('\xef\xbb\x33'), "utf-8")
        self.assertEqual(codec._detectencoding_str('\xef\xbb\xbf'), "utf-8-sig")
        self.assert_(codec._detectencoding_str('\xff') is None)
        self.assertEqual(codec._detectencoding_str('\xff\x33'), "utf-8")
        self.assert_(codec._detectencoding_str('\xff\xfe') is None)
        self.assertEqual(codec._detectencoding_str('\xff\xfe\x33'), "utf-16")
        self.assert_(codec._detectencoding_str('\xff\xfe\x00') is None)
        self.assertEqual(codec._detectencoding_str('\xff\xfe\x00\x33'), "utf-16")
        self.assertEqual(codec._detectencoding_str('\xff\xfe\x00\x00'), "utf-32")
        self.assert_(codec._detectencoding_str('\x00') is None)
        self.assertEqual(codec._detectencoding_str('\x00\x33'), "utf-8")
        self.assert_(codec._detectencoding_str('\x00\x00') is None)
        self.assertEqual(codec._detectencoding_str('\x00\x00\x33'), "utf-8")
        self.assert_(codec._detectencoding_str('\x00\x00\xfe') is None)
        self.assertEqual(codec._detectencoding_str('\x00\x00\x00\x33'), "utf-8")
        self.assertEqual(codec._detectencoding_str('\x00\x00\x00@'), "utf-32-be")
        self.assertEqual(codec._detectencoding_str('\x00\x00\xfe\xff'), "utf-32")
        self.assert_(codec._detectencoding_str('@') is None)
        self.assertEqual(codec._detectencoding_str('@\x33'), "utf-8")
        self.assert_(codec._detectencoding_str('@\x00') is None)
        self.assertEqual(codec._detectencoding_str('@\x00\x33'), "utf-8")
        self.assert_(codec._detectencoding_str('@\x00\x00') is None)
        self.assertEqual(codec._detectencoding_str('@\x00\x00\x33'), "utf-8")
        self.assertEqual(codec._detectencoding_str('@\x00\x00\x00'), "utf-32-le")
        self.assert_(codec._detectencoding_str('@c') is None)
        self.assert_(codec._detectencoding_str('@ch') is None)
        self.assert_(codec._detectencoding_str('@cha') is None)
        self.assert_(codec._detectencoding_str('@char') is None)
        self.assert_(codec._detectencoding_str('@chars') is None)
        self.assert_(codec._detectencoding_str('@charse') is None)
        self.assert_(codec._detectencoding_str('@charset') is None)
        self.assert_(codec._detectencoding_str('@charset ') is None)
        self.assert_(codec._detectencoding_str('@charset "') is None)
        self.assert_(codec._detectencoding_str('@charset "x') is None)
        self.assertEqual(codec._detectencoding_str('@charset ""'), "")
        self.assertEqual(codec._detectencoding_str('@charset "x"'), "x")
        self.assert_(codec._detectencoding_str("@", False) is None)
        self.assertEqual(codec._detectencoding_str("@", True), "utf-8")
        self.assert_(codec._detectencoding_str("@c", False) is None)
        self.assertEqual(codec._detectencoding_str("@c", True), "utf-8")

    def test_detectencoding_unicode(self):
        # Unicode version (only parses the header)
        self.assert_(codec._detectencoding_unicode(u'@charset "x') is None)
        self.assertEqual(codec._detectencoding_unicode(u'@charset "x', True), "utf-8")
        self.assertEqual(codec._detectencoding_unicode(u'@charset "x"'), "x")

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
            # Check stateless decoder with encoding autodetection
            d = codecs.getdecoder("css")
            self.assertEqual(d(input.encode(encoding))[0], input.replace('"x"', '"%s"' % outputencoding))

            # Check stateless decoder with specified encoding
            self.assertEqual(d(input.encode(encoding), encoding=encoding)[0], input.replace('"x"', '"%s"' % outputencoding))

            # Check incremental decoder with encoding autodetection
            id = codecs.getincrementaldecoder("css")()
            self.assertEqual("".join(id.iterdecode(input.encode(encoding))), input.replace('"x"', '"%s"' % outputencoding))

            # Check incremental decoder with specified encoding
            id = codecs.getincrementaldecoder("css")(encoding=encoding)
            self.assertEqual("".join(id.iterdecode(input.encode(encoding))), input.replace('"x"', '"%s"' % outputencoding))

            # Check stream reader with encoding autodetection
            q = Queue()
            sr = codecs.getreader("css")(q)
            result = []
            for c in input.encode(encoding):
                q.write(c)
                result.append(sr.read())
            self.assertEqual("".join(result), input.replace('"x"', '"%s"' % outputencoding))

            # Check stream reader with specified encoding
            q = Queue()
            sr = codecs.getreader("css")(q, encoding=encoding)
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
            outputencoding = encoding
            if outputencoding == "utf-8-sig":
                outputencoding = "utf-8"
            self.assertEqual(d(input.encode(encoding))[0], input)

            # Check stateless decoder with specified encoding
            self.assertEqual(d(input.encode(encoding), encoding=encoding)[0], input)

            # Check incremental decoder with encoding autodetection
            id = codecs.getincrementaldecoder("css")()
            self.assertEqual("".join(id.iterdecode(input.encode(encoding))), input)

            # Check incremental decoder with specified encoding
            id = codecs.getincrementaldecoder("css")(encoding)
            self.assertEqual("".join(id.iterdecode(input.encode(encoding))), input)

            # Check stream writer with encoding autodetection
            q = Queue()
            sw = codecs.getwriter("css")(q)
            for c in input:
                sw.write(c)
            self.assertEqual(q.read().decode(encoding), input.replace('"x"', '"%s"' % outputencoding))

            # Check stream writer with specified encoding
            q = Queue()
            sw = codecs.getwriter("css")(q, encoding=encoding)
            for c in input:
                sw.write(c)
            self.assertEqual(q.read().decode(encoding), input.replace('"x"', '"%s"' % outputencoding))

        # Use correct declaration
        checkdecl("utf-8")
        checkdecl("iso-8859-1", u'@charset "%s";g\xfcrk')
        checkdecl("iso-8859-15")
        checkdecl("cp1252")

        # No recursion
        self.assertRaises(ValueError, '@charset "css";div{}'.decode, "css")

    def test_encoder(self):
        def check(encoding, input=u'@charset "x";g\xfcrk\u20ac{}'):
            outputencoding = encoding
            if outputencoding == "utf-8-sig":
                outputencoding = "utf-8"

            # Check stateless encoder with encoding autodetection
            e = codecs.getencoder("css")
            inputdecl = input.replace('"x"', '"%s"' % encoding)
            outputdecl = input.replace('"x"', '"%s"' % outputencoding)
            self.assertEqual(e(inputdecl)[0].decode(encoding), outputdecl)

            # Check stateless encoder with specified encoding
            self.assertEqual(e(input, encoding=encoding)[0].decode(encoding), outputdecl)

            # Check incremental encoder with encoding autodetection
            ie = codecs.getincrementalencoder("css")()
            self.assertEqual("".join(ie.iterencode(inputdecl)).decode(encoding), outputdecl)

            # Check incremental encoder with specified encoding
            ie = codecs.getincrementalencoder("css")(encoding=encoding)
            self.assertEqual("".join(ie.iterencode(input)).decode(encoding), outputdecl)

        # Autodetectable encodings
        check("utf-8-sig")
        check("utf-16")
        check("utf-16-le")
        check("utf-16-be")
        if haveutf32:
            check("utf-32")
            check("utf-32-le")
            check("utf-32-be")
        check("utf-8")
        check("iso-8859-1", u'@charset "x";g\xfcrk{}')
        check("iso-8859-15")
        check("cp1252")

        # No recursion
        self.assertRaises(ValueError, u'@charset "css";div{}'.encode, "css")


if __name__ == '__main__':
    import unittest
    unittest.main()
