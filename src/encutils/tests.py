"""
tests for encutils.py
"""
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.7a2, SVN revision $LastChangedRevision$'

import httplib
from StringIO import StringIO
import sys
import unittest

try:
    import encutils
except ImportError:
    import cssutils.encutils as encutils


# helper log
log = encutils.buildlog(stream=StringIO())    


class AutoEncodingTestCase(unittest.TestCase):


    def _fakeRes(self, content):
        "build a fake HTTP response"
        class FakeRes:
            def __init__(self, content):
                fp = StringIO(content)
                self._info = httplib.HTTPMessage(fp)
                
            def info(self):
                return self._info
        return FakeRes(content)


    def test_getTextTypeByMediaType(self):
        tests = {
            'application/xml': encutils._XML_APPLICATION_TYPE,
            'application/xml-dtd': encutils._XML_APPLICATION_TYPE,
            'application/xml-external-parsed-entity': encutils._XML_APPLICATION_TYPE,
            'application/xhtml+xml': encutils._XML_APPLICATION_TYPE,
            'text/xml': encutils._XML_TEXT_TYPE,
            'text/xml-external-parsed-entity': encutils._XML_TEXT_TYPE,
            'text/xhtml+xml': encutils._XML_TEXT_TYPE,
            'text/html': encutils._HTML_TEXT_TYPE,
            'text/css': encutils._TEXT_TYPE,
            'text/plain': encutils._TEXT_TYPE,
            'x/x': encutils._OTHER_TYPE,
            'ANYTHING': encutils._OTHER_TYPE 
            }
        for test, exp in tests.items():
            self.assertEqual(
                exp, encutils._getTextTypeByMediaType(test, log=log))


    def test_getTextType(self):
        tests = {
            u'\x00\x00\xFE\xFF<?xml version="1.0"': encutils._XML_APPLICATION_TYPE,
            u'\xFF\xFE\x00\x00<?xml version="1.0"': encutils._XML_APPLICATION_TYPE,
            u'\xFE\xFF<?xml version="1.0"': encutils._XML_APPLICATION_TYPE,
            u'\xFF\xFE<?xml version="1.0"': encutils._XML_APPLICATION_TYPE,
            u'\xef\xbb\xbf<?xml version="1.0"': encutils._XML_APPLICATION_TYPE,
            u'<?xml version="1.0"': encutils._XML_APPLICATION_TYPE,
            u'\x00\x00\xFE\xFFanything': encutils._OTHER_TYPE,
            u'\xFF\xFE\x00\x00anything': encutils._OTHER_TYPE,
            u'\xFE\xFFanything': encutils._OTHER_TYPE,
            u'\xFF\xFEanything': encutils._OTHER_TYPE,
            u'\xef\xbb\xbfanything': encutils._OTHER_TYPE,
            u'x/x': encutils._OTHER_TYPE,
            u'ANYTHING': encutils._OTHER_TYPE 
            }
        for test, exp in tests.items():
            self.assertEqual(
                exp, encutils._getTextType(test, log=log))        


    def test_encodingByMediaType(self):
        tests = {
            'application/xml': 'utf-8',
            'application/xml-dtd': 'utf-8',
            'application/xml-external-parsed-entity': 'utf-8',
            'application/ANYTHING+xml': 'utf-8',
            '  application/xml  ': 'utf-8',
            'text/xml': 'ascii',
            'text/xml-external-parsed-entity': 'ascii',
            'text/ANYTHING+xml': 'ascii',
            'text/html': 'iso-8859-1',
            'text/css': 'iso-8859-1',
            'text/plain': 'iso-8859-1',
            'ANYTHING': None
            }
        for test, exp in tests.items():
            self.assertEqual(exp,
                             encutils.encodingByMediaType(test, log=log))

    
    def test_getMetaInfo(self):
        tests = {
            """<meta tp-equiv='Content-Type' content='text/html; charset=ascii'>""":
                (None, None),
            """<meta http-equiv='ontent-Type' content='text/html; charset=ascii'>""":
                (None, None),

            """<meta http-equiv='Content-Type' content='text/html'>""":
                ('text/html', None),

            """<meta content='text/html' http-equiv='Content-Type'>""":
                ('text/html', None),
            """<meta content='text/html;charset=ascii' http-equiv='Content-Type'>""":
                ('text/html', 'ascii'),

            """<meta http-equiv='Content-Type' content='text/html ;charset=ascii'>""":
                ('text/html', 'ascii'),
            """<meta content='text/html;charset=iso-8859-1' http-equiv='Content-Type'>""":
                ('text/html', 'iso-8859-1'),
            """<meta http-equiv="Content-Type" content="text/html;charset = ascii">""":
                ('text/html', 'ascii'),

            """<meta http-equiv="Content-Type" content="text/html;charset=ascii;x=2">""":
                ('text/html', 'ascii'),
            """<meta http-equiv="Content-Type" content="text/html;x=2;charset=ascii">""":
                ('text/html', 'ascii'),
            """<meta http-equiv="Content-Type" content="text/html;x=2;charset=ascii;y=2">""":
                ('text/html', 'ascii'),

            """<meta http-equiv='Content-Type' content="text/html;charset=ascii">""":
                ('text/html', 'ascii'),
            """<meta http-equiv='Content-Type' content='text/html;charset=ascii'  />""":
                ('text/html', 'ascii'),
            """<meta http-equiv = " Content-Type" content = " text/html;charset=ascii " >""":
                ('text/html', 'ascii'),
            """<meta http-equiv = " \n Content-Type " content = "  \t text/html   ;  charset=ascii " >""":
                ('text/html', 'ascii')
            }
        for test, exp in tests.items():
            self.assertEqual(exp, encutils.getMetaInfo(test, log=log))


    def test_detectXMLEncoding(self):
        tests = {
            # BOM
            ('utf_32_be'): u'\x00\x00\xFE\xFFanything',
            ('utf_32_le'): u'\xFF\xFE\x00\x00anything',
            ('utf_16_be'): u'\xFE\xFFanything',
            ('utf_16_le'): u'\xFF\xFEanything',
            ('utf-8'): u'\xef\xbb\xbfanything',
            # encoding=
            ('ascii'): '<?xml version="1.0" encoding="ascii" ?>', 
            ('ascii'): "<?xml version='1.0' encoding='ascii' ?>", 
            ('iso-8859-1'): "<?xml version='1.0' encoding='iso-8859-1' ?>",
            # default
            ('utf-8'): '<?xml version="1.0" ?>', 
            ('utf-8'): '<?xml version="1.0"?><x encoding="ascii"/>'
            }
        for exp, test in tests.items():
            self.assertEqual(exp, encutils.detectXMLEncoding(test, log=log))        


    def test_tryEncodings(self):
        try:
            import chardet            
            tests = [
                ('ascii', 'abc'),
                ('windows-1252', u'\xf6'),
                ('ascii', u'\u1111')
                ]
        except ImportError:
            tests = [
                ('ascii', 'abc'),
                ('iso-8859-1', u'\xf6'),
                ('utf-8', u'\u1111')
                ]            
        for exp, test in tests:
            self.assertEqual(exp, encutils.tryEncodings(test))        


    # (expectedencoding, expectedmismatch): (httpheader, filecontent)
    fulltests = {
        ('utf-8', False): (
            '''NoContentType''', '''OnlyText'''),
        
        # --- application/xhtml+xml ---
        # default enc
        ('utf-8', False): (
            '''Content-Type: application/xhtml+xml''',
            '''<?xml version="1.0" ?>
                <example>
                    <meta http-equiv="Content-Type"
                        content="application/xhtml+xml"/>
                </example>'''),
        # header enc
        ('iso-h', True): (
            '''Content-Type: application/xhtml+xml;charset=iso-H''',
            '''<?xml version="1.0" ?>
                <example>
                    <meta http-equiv="Content-Type"
                        content="application/xhtml+xml"/>
                </example>'''),
        # mismatch header - meta, meta ignored
        ('iso-h', True): (
            '''Content-Type: application/xhtml+xml;charset=iso-H''',
            '''<?xml version="1.0" ?>
                <example>
                    <meta http-equiv="Content-Type"
                        content="application/xhtml+xml;charset=iso_M"/>
                </example>'''),
        # mismatch XML - meta, meta ignored
        ('iso-x', False): (
            '''Content-Type: application/xhtml+xml''',
            '''<?xml version="1.0" encoding="iso-X" ?>
                <example>
                    <meta http-equiv="Content-Type"
                        content="application/xhtml+xml;charset=iso_M"/>
                </example>'''),
        # mismatch header and XML, header wins
        ('iso-h', True): (
            '''Content-Type: application/xhtml+xml;charset=iso-H''',
            '''<?xml version="1.0" encoding="iso-X" ?>
                <example/>'''),

        # --- text/xml ---
        # default enc
        ('ascii', False): (
            '''Content-Type: text/xml''',
            '''<?xml version="1.0" ?>
                <example>
                    <meta http-equiv="Content-Type"
                        content="text/xml"/>
                </example>'''),
        # header enc
        ('iso-h', True): (
            '''Content-Type: text/xml;charset=iso-H''',
            '''<?xml version="1.0" ?>
                <example>
                    <meta http-equiv="Content-Type"
                        content="text/xml"/>
                </example>'''),
        # mismatch header - meta, meta ignored
        ('iso-h', True): (
            '''Content-Type: text/xml;charset=iso-H''',
            '''<?xml version="1.0" ?>
                <example>
                    <meta http-equiv="Content-Type"
                        content="text/xml;charset=iso_M"/>
                </example>'''),
        # XML - meta, both ignored, use HTTP, meta completely ignored
        ('ascii', False): (
            '''Content-Type: text/xml''',
            '''<?xml version="1.0" encoding="iso-X" ?>
                <example>
                    <meta http-equiv="Content-Type"
                        content="text/xml;charset=iso_M"/>
                </example>'''),
        # mismatch header and XML, XML ignored
        ('iso-h', True): (
            '''Content-Type: text/xml;charset=iso-H''',
            '''<?xml version="1.0" encoding="iso-X" ?>
                <example/>'''),

        # --- text/html ---
        # no default enc
        (None, False): ('Content-Type: text/html;',
            '''<meta http-equiv="Content-Type"
                content="text/html">'''),
        # header enc
        ('iso-h', True): ('Content-Type: text/html;charset=iso-H',
            '''<meta http-equiv="Content-Type"
                content="text/html">'''),   
        # meta enc
        ('iso-m', True): ('Content-Type: text/html',
            '''<meta http-equiv="Content-Type"
                content="text/html;charset=iso-m">'''),
        # mismatch header - meta, header wins
        ('iso-h', True): ('Content-Type: text/html;charset=iso-H',
            '''<meta http-equiv="Content-Type"
                content="text/html;charset=iso-m">'''),

        # no header:
        (None, False): (None,
            '''<meta http-equiv="Content-Type"
                content="text/html;charset=iso-m">'''),
          (None, False): (None, '''text'''),
          ('utf-8', False): (None, '''<?xml version='''),
          ('utf-8', False): (None, '''<?xml version='''),
          ('iso-x', False): (None, '''<?xml version="1.0" encoding="iso-X"?>''')
        }


    def test_getEncodingInfo(self):
        for exp, test in self.fulltests.items():
            header, text = test
            if header:
                res = encutils.getEncodingInfo(self._fakeRes(header), text)
            else:
                res = encutils.getEncodingInfo(text=text)
            res = (res.encoding, res.mismatch)
            self.assertEqual(exp, res)


if __name__ == '__main__':
    unittest.main()
