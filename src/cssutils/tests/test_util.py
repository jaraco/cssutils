# -*- coding: utf-8 -*-
"""Testcases for cssutils.util"""
__version__ = '$Id$'

import cgi
from email import message_from_string, message_from_file
import StringIO
import sys
import urllib2
import xml.dom

try:
    from minimock import mock, restore
except ImportError:
    mock = None 
    print "install minimock with ``easy_install minimock`` to run all tests"

import basetest
import encutils
    
from cssutils.util import Base, ListSeq, _readUrl, _defaultFetcher

class ListSeqTestCase(basetest.BaseTestCase):
    
    def test_all(self):
        "util.ListSeq"
        ls = ListSeq()
        self.assertEqual(0, len(ls))
        # append()
        self.assertRaises(NotImplementedError, ls.append, 1)
        # set
        self.assertRaises(NotImplementedError, ls.__setitem__, 0, 1)

        # hack:
        ls.seq.append(1)
        ls.seq.append(2)
        
        # len
        self.assertEqual(2, len(ls))
        # __contains__
        self.assertEqual(True, 1 in ls)
        # get
        self.assertEqual(1, ls[0])
        self.assertEqual(2, ls[1])
        # del
        del ls[0]
        self.assertEqual(1, len(ls))
        self.assertEqual(False, 1 in ls)
        # for in 
        for x in ls:
            self.assertEqual(2, x)
    

class BaseTestCase(basetest.BaseTestCase):

    def test_normalize(self):
        "Base._normalize()"
        b = Base()
        tests = {u'abcdefg ABCDEFG äöüß€ AÖÜ': u'abcdefg abcdefg äöüß€ aöü',
                 ur'\ga\Ga\\\ ': ur'gaga\ ',
                 ur'0123456789': u'0123456789',
                 # unicode escape seqs should have been done by
                 # the tokenizer...
                 }
        for test, exp in tests.items():
            self.assertEqual(b._normalize(test), exp)
            # static too
            self.assertEqual(Base._normalize(test), exp)

    def test_tokenupto(self):
        "Base._tokensupto2()"

        # tests nested blocks of {} [] or ()
        b = Base()

        tests = [
            ('default', u'a[{1}]({2}) { } NOT', u'a[{1}]({2}) { }', False),
            ('default', u'a[{1}]({2}) { } NOT', u'a[{1}]func({2}) { }', True),
            ('blockstartonly', u'a[{1}]({2}) { NOT', u'a[{1}]({2}) {', False),
            ('blockstartonly', u'a[{1}]({2}) { NOT', u'a[{1}]func({2}) {', True),
            ('propertynameendonly', u'a[(2)1] { }2 : a;', u'a[(2)1] { }2 :', False),
            ('propertynameendonly', u'a[(2)1] { }2 : a;', u'a[func(2)1] { }2 :', True),
            ('propertyvalueendonly', u'a{;{;}[;](;)}[;{;}[;](;)](;{;}[;](;)) 1; NOT',
                u'a{;{;}[;](;)}[;{;}[;](;)](;{;}[;](;)) 1;', False),
            ('propertyvalueendonly', u'a{;{;}[;](;)}[;{;}[;](;)](;{;}[;](;)) 1; NOT',
                u'a{;{;}[;]func(;)}[;{;}[;]func(;)]func(;{;}[;]func(;)) 1;', True),
            ('funcendonly', u'a{[1]}([3])[{[1]}[2]([3])]) NOT',
                u'a{[1]}([3])[{[1]}[2]([3])])', False),
            ('funcendonly', u'a{[1]}([3])[{[1]}[2]([3])]) NOT',
                u'a{[1]}func([3])[{[1]}[2]func([3])])', True),
            ('selectorattendonly', u'[a[()]{()}([()]{()}())] NOT',
                u'[a[()]{()}([()]{()}())]', False),
            ('selectorattendonly', u'[a[()]{()}([()]{()}())] NOT',
                u'[a[func()]{func()}func([func()]{func()}func())]', True)
            ]

        for typ, values, exp, paransasfunc in tests:

            def maketokens(valuelist):
                # returns list of tuples
                return [('TYPE', v, 0, 0) for v in valuelist]

            tokens = maketokens(list(values))
            if paransasfunc:
                for i, t in enumerate(tokens):
                    if u'(' == t[1]:
                        tokens[i] = ('FUNCTION', u'func(', t[2], t[3])

            if 'default' == typ:
                restokens = b._tokensupto2(tokens)
            elif 'blockstartonly' == typ:
                restokens = b._tokensupto2(
                    tokens, blockstartonly=True)
            elif 'propertynameendonly' == typ:
                restokens = b._tokensupto2(
                    tokens, propertynameendonly=True)
            elif 'propertyvalueendonly' == typ:
                restokens = b._tokensupto2(
                    tokens, propertyvalueendonly=True)
            elif 'funcendonly' == typ:
                restokens = b._tokensupto2(
                    tokens, funcendonly=True)
            elif 'selectorattendonly' == typ:
                restokens = b._tokensupto2(
                    tokens, selectorattendonly=True)

            res = u''.join([t[1] for t in restokens])
            self.assertEqual(exp, res)
     
   
class _readUrl_TestCase(basetest.BaseTestCase):
    """needs minimock install with easy_install minimock""" 

    def test_readUrl(self):
        """util._readUrl()"""        
        # for additional tests see test_parse.py
        url = 'http://example.com/test.css'

        def make_fetcher(r):
            # normally r == encoding, content
            def fetcher(url):
                return r
            return fetcher
        
        tests = {
            # defaultFetcher returns: readUrl returns
            None: (None, None),
            (None, ''): (None, u''),
            (None, u'€'.encode('utf-8')): (None, u'€'),
            ('utf-8', u'€'.encode('utf-8')): ('utf-8', u'€'),
            ('ISO-8859-1', u'ä'.encode('iso-8859-1')): ('ISO-8859-1', u'ä'),
            ('ASCII', u'a'.encode('ascii')): ('ASCII', u'a')
        }

        for r, exp in tests.items():              
            self.assertEquals(_readUrl(url, 
                                       fetcher=make_fetcher(r)), exp)

        tests = {
            # (override, defaultFetcher returns): readUrl returns
            ('latin1', None): (None, None),
            ('latin1', (None, '')): ('latin1', u''),
            ('latin1', ('', u'ä'.encode('iso-8859-1'))): 
                ('latin1', u'ä'),
            ('latin1', ('', u'a'.encode('ascii'))): 
                ('latin1', u'a')
        }
        for (override, r), exp in tests.items():              
            self.assertEquals(_readUrl(url, overrideEncoding=override,
                                       fetcher=make_fetcher(r)), exp)

    def test_defaultFetcher(self):
        """util._defaultFetcher"""
        if mock:
            
            class Response(object):
                """urllib2.Reponse mock"""
                def __init__(self, url, 
                             contenttype, content,
                             exception=None, args=None):
                    self.url = url
                    
                    mt, params = cgi.parse_header(contenttype)
                    self.mimetype = mt
                    self.charset = params.get('charset', None)
                    
                    self.text = content
                    
                    self.exception = exception
                    self.args = args

                def geturl(self):
                    return self.url

                def info(self):
                    mimetype, charset = self.mimetype, self.charset 
                    class Info(object):
                        def gettype(self):
                            return mimetype
                        def getparam(self, name):
                            return charset

                    return Info()

                def read(self):
                    # returns fake text or raises fake exception
                    if not self.exception:
                        return self.text
                    else:
                        raise self.exception(*self.args)

            def urlopen(url, 
                        contenttype=None, content=None,
                        exception=None, args=None):
                # return an mock which returns parameterized Response
                def x(*ignored):
                    if exception:
                        raise exception(*args)
                    else:
                        return Response(url,
                                        contenttype, content, 
                                        exception=exception, args=args)
                return x
            
            # positive tests
            tests = {
                # content-type, contentstr: encoding, contentstr
                ('text/css', u'€'.encode('utf-8')): 
                        (None, u'€'.encode('utf-8')),  
                ('text/css;charset=utf-8', u'€'.encode('utf-8')): 
                        ('utf-8', u'€'.encode('utf-8')),  
                ('text/css;charset=ascii', 'a'): 
                        ('ascii', 'a')  
            }
            url = 'http://example.com/test.css'
            for (contenttype, content), exp in tests.items():
                
                mock("urllib2.urlopen", mock_obj=urlopen(url, contenttype, content))

                #print url, exp == _readUrl(url, encoding), exp, _readUrl(url, encoding)
                self.assertEqual(exp, _defaultFetcher(url))

            # wrong mimetype
            mock("urllib2.urlopen", mock_obj=urlopen(url, 'text/html', 'a'))
            self.assertRaises(ValueError, _defaultFetcher, url)

            # calling url results in fake exception
            tests = {
                '1': (ValueError, ['invalid value for url']),
                'e2': (urllib2.HTTPError, ['u', 500, 'server error', {}, None]),
                #_readUrl('http://cthedot.de/__UNKNOWN__.css')
                'e3': (urllib2.HTTPError, ['u', 404, 'not found', {}, None]),
                #_readUrl('mailto:a.css')
                'mailto:e4': (urllib2.URLError, ['urlerror']),
                # cannot resolve x, IOError
                'http://x': (urllib2.URLError, ['ioerror']),
            }
            for url, (exception, args) in tests.items():
                mock("urllib2.urlopen",
                        mock_obj=urlopen(url, exception=exception, args=args))
                self.assertRaises(exception, _defaultFetcher, url)

            restore()
        

if __name__ == '__main__':
    import unittest
    unittest.main()
