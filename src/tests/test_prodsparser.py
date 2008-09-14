"""Testcases for cssutils.css.CSSCharsetRule"""
__version__ = '$Id: test_csscharsetrule.py 1356 2008-07-13 17:29:09Z cthedot $'

import basetest
from cssutils.prodsparser import *
from cssutils.prodsparser import ParseError, Exhausted # not in __all__

class ProdTestCase(basetest.BaseTestCase):

    def setUp(self):
        pass

    def test_init(self):
        "Prod.__init__(...)"
        p = Prod('min', lambda t, v: t == 1 and v == 2)
        
        self.assertEqual(p.name, 'min')
        self.assertEqual(p.toStore, None)
        self.assertEqual(p.optional, False)
        
        p = Prod('optional', lambda t, v: True, 
                  optional=True)
        self.assertEqual(p.optional, True)

    def test_initMatch(self):
        "Prod.__init__(...match=...)"
        p = Prod('min', lambda t, v: t == 1 and v == 2)
        self.assertEqual(p.match(1, 2), True)
        self.assertEqual(p.match(2, 2), False)
        self.assertEqual(p.match(1, 1), False)

    def test_initToSeq(self):
        "Prod.__init__(...toSeq=...)"
        # simply saves
        p = Prod('all', lambda t, v: True,
                 toSeq=None)
        self.assertEqual(p.toSeq(1), 1) # simply saves
        self.assertEqual(p.toSeq('same'), 'same') # simply saves

        # saves callback(val)
        p = Prod('all', lambda t, v: True, 
                  toSeq=lambda val: 1 == val)        
        self.assertEqual(p.toSeq(1), True)
        self.assertEqual(p.toSeq(2), False)

    def test_initToStore(self):
        "Prod.__init__(...toStore=...)"
        p = Prod('all', lambda t, v: True, 
                  toStore='key')

        # save as key
        s = {}
        p.toStore(s, 1)
        self.assertEqual(s['key'], 1)

        # append to key
        s = {'key': []}
        p.toStore(s, 1)
        p.toStore(s, 2)
        self.assertEqual(s['key'], [1, 2])

        # callback
        def doubleToStore(key):
            def toStore(store, item):
                    store[key] = item * 2
            return toStore
        
        p = Prod('all', lambda t, v: True, 
                  toStore=doubleToStore('key'))
        s = {'key': []}
        p.toStore(s, 1)
        self.assertEqual(s['key'], 2)

    def test_matches(self):
        "Prod.matches(token)"
        p1 = Prod('norm', lambda t, v: t == 1 and v == 2)
        p2 = Prod('opt', lambda t, v: t == 1 and v == 2, optional=True)
        self.assertEqual(p1.matches([1, 2, 0, 0]), True)
        self.assertEqual(p2.matches([1, 2, 0, 0]), True)
        self.assertRaisesMsg(ParseError, 
                             u'Expected norm, wrong type or value', 
                             p1.matches, [0, 0, 0,0 ])
        # optional!
        self.assertEqual(p2.matches([0, 0, 0, 0]), False)

class SequenceTestCase(basetest.BaseTestCase):
    
    def test_init(self):
        "Sequence.__init__()"
        p1 = Prod('p1', lambda t, v: t == 1)      
        p2 = Prod('p2', lambda t, v: t == 2)
        prods = [p1, p2]  
            
        seq = Sequence(prods)
        
        self.assertEqual(1, seq._min)
        self.assertEqual(1, seq._max)

    def test_initminmax(self):
        "Sequence.__init__(...minmax=...)"
        p1 = Prod('p1', lambda t, v: t == 1)      
        p2 = Prod('p2', lambda t, v: t == 2)
        prods = [p1, p2]  
            
        seq = Sequence(prods, minmax=lambda: (2, 3))
        
        self.assertEqual(2, seq._min)
        self.assertEqual(3, seq._max)

    def test_first(self):
        "Sequence.first()"
        p1 = Prod('p1', lambda t, v: t == 1)      
        p2 = Prod('p2', lambda t, v: t == 2, optional=True)
            
        seq = Sequence([p1, p2])
        self.assertEqual(p1, seq.first())
        
        seq = Sequence([p2, p1])
        self.assertEqual(p1, seq.first())

    def test_nextProd(self):
        "Sequence.nextProd()"
        p1 = Prod('p1', lambda t, v: t == 1, optional=True)      
        p2 = Prod('p2', lambda t, v: t == 2)
        t1 = (1, 0, 0, 0)
        t2 = (2, 0, 0, 0)
                  
        tests = {
            # seq: list of list of (token, prod or error msg)
            (p1, ): ([(t1, p1)],
                     [(t2, 'Extra token')], # as p1 optional
                     [(t1, p1), (t1, u'Extra token')],
                     [(t1, p1), (t2, u'Extra token')]
                    ),
            (p2, ): ([(t2, p2)],
                     [(t1, 'Expected p2, wrong type or value')],
                     [(t2, p2), (t2, u'Extra token')],
                     [(t2, p2), (t1, u'Extra token')]
                    ),
            (p1, p2): ([(t1, p1), (t2, p2)],
                       [(t1, p1), (t1, u'Expected p2, wrong type or value')]
                       )
            }
        for seqitems, results in tests.items():
            for result in results: 
                seq = Sequence(seqitems)
                for t, p in result:
                    if isinstance(p, basestring):
                        self.assertRaisesMsg(ParseError, p, seq.nextProd, t)
                    else:
                        self.assertEqual(p, seq.nextProd(t))

        tests = {
            # seq: list of list of (token, prod or error msg)
            # as p1 optional!
            (p1, p1): ([(t1, p1)],
                       [(t1, p1), (t1, p1)],
                       [(t1, p1), (t1, p1)],
                       [(t1, p1), (t1, p1), (t1, p1)],
                       [(t1, p1), (t1, p1), (t1, p1), (t1, p1)],
                       [(t1, p1), (t1, p1), (t1, p1), (t1, p1), (t1, u'Extra token')],
                     ),
            (p1, ): ([(t1, p1)],
                     [(t2, 'Extra token')], 
                     [(t1, p1), (t1, p1)],
                     [(t1, p1), (t2, 'Extra token')],
                     [(t1, p1), (t1, p1), (t1, u'Extra token')],
                     [(t1, p1), (t1, p1), (t2, u'Extra token')]
                    ),
            # as p2 NOT optional
            (p2, ): ([(t2, p2)],
                     [(t1, 'Expected p2, wrong type or value')],
                     [(t2, p2), (t2, p2)],
                     [(t2, p2), (t1, u'Expected p2, wrong type or value')],
                     [(t2, p2), (t2, p2), (t2, u'Extra token')],
                     [(t2, p2), (t2, p2), (t1, u'Extra token')]
                    ),
            (p1, p2): ([(t1, p1), (t1, u'Expected p2, wrong type or value')],
                       [(t2, p2), (t2, p2)],
                       [(t2, p2), (t1, p1), (t2, p2)],
                       [(t1, p1), (t2, p2), (t2, p2)],
                       [(t1, p1), (t2, p2), (t1, p1), (t2, p2)],
                       [(t2, p2), (t2, p2), (t2, u'Extra token')],
                       [(t2, p2), (t1, p1), (t2, p2), (t1, 'Extra token')],
                       [(t2, p2), (t1, p1), (t2, p2), (t2, 'Extra token')],
                       [(t1, p1), (t2, p2), (t2, p2), (t1, 'Extra token')],
                       [(t1, p1), (t2, p2), (t2, p2), (t2, 'Extra token')],
                       [(t1, p1), (t2, p2), (t1, p1), (t2, p2), (t1, 'Extra token')],
                       [(t1, p1), (t2, p2), (t1, p1), (t2, p2), (t2, 'Extra token')],
                       )
            }
        for seqitems, results in tests.items():
            for result in results: 
                seq = Sequence(seqitems, minmax = lambda: (1,2))
                for t, p in result:
                    if isinstance(p, basestring):
                        self.assertRaisesMsg(ParseError, p, seq.nextProd, t)
                    else:
                        self.assertEqual(p, seq.nextProd(t))
                                
        
class ChoiceTestCase(basetest.BaseTestCase):
    
    def test_init(self):
        "Choice.__init__()"
        p1 = Prod('p1', lambda t, v: t == 1)      
        p2 = Prod('p2', lambda t, v: t == 2)
        t0 = (0,0,0,0)
        t1 = (1,0,0,0)
        t2 = (2,0,0,0)
            
        ch = Choice([p1, p2])
        self.assertRaisesMsg(ParseError, u'No match in choice', ch.nextProd, t0)
        self.assertEqual(p1, ch.nextProd(t1))
        self.assertRaisesMsg(Exhausted, u'Extra token', ch.nextProd, t1)

        ch = Choice([p1, p2])
        self.assertEqual(p2, ch.nextProd(t2))
        self.assertRaisesMsg(Exhausted, u'Extra token', ch.nextProd, t2)

        ch = Choice([p2, p1])
        self.assertRaisesMsg(ParseError, 'No match in choice', ch.nextProd, t0)
        self.assertEqual(p1, ch.nextProd(t1))
        self.assertRaisesMsg(Exhausted, u'Extra token', ch.nextProd, t1)

        ch = Choice([p2, p1])
        self.assertEqual(p2, ch.nextProd(t2))
        self.assertRaisesMsg(Exhausted, u'Extra token', ch.nextProd, t2)

    def test_nested(self):
        "Choice with nested Sequence"
        p1 = Prod('p1', lambda t, v: t == 1)      
        p2 = Prod('p2', lambda t, v: t == 2)
        s1 = Sequence([p1, p1])
        s2 = Sequence([p2, p2])
        t0 = (0,0,0,0)
        t1 = (1,0,0,0)
        t2 = (2,0,0,0)

        ch = Choice([s1, s2])
        self.assertRaisesMsg(ParseError, u'No match in choice', ch.nextProd, t0)
        self.assertEqual(s1, ch.nextProd(t1))
        self.assertRaisesMsg(Exhausted, u'Extra token', ch.nextProd, t1)
            
        ch = Choice([s1, s2])
        self.assertEqual(s2, ch.nextProd(t2))
        self.assertRaisesMsg(Exhausted, u'Extra token', ch.nextProd, t1)


class ProdsParserTestCase(basetest.BaseTestCase):

    def setUp(self):
        pass

    def test_parse(self):
        "ProdsParser.parse()"      
        # text, name, productions, store=None
        #p = ProdsParser(text, name, productions, store=None)

    def test_combi(self):
        "ProdsParser.parse() 2"
        p1 = Prod('p1', lambda t, v: v == '1')      
        p2 = Prod('p2', lambda t, v: v == '2')
        p3 = Prod('p2', lambda t, v: v == '3')
        s1 = Sequence([p1], minmax=lambda: (1,2))
        
        tests = {
                 '1': True,
                 '1 1': True,
                 '2': True,
                 '1 3': True,
                 '1 1 3': True,
                 '2 3': True,
                 }
        for text, exp in tests.items():
            prods = Sequence([Choice([Sequence([p1], minmax=lambda: (1,2)),
                                      p2]),
                              p3])
            wellformed, seq, store, unused = ProdsParser().parse(text, 'T', prods)
            self.assertEqual(wellformed, exp)


if __name__ == '__main__':
    import unittest
    unittest.main()
