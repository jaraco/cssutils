"""Testcases for cssutils.css.property._Property."""
__version__ = '$Id: test_property.py 1529 2008-11-30 15:12:01Z cthedot $'

import copy
import xml.dom
import basetest
import cssutils
from cssutils.css.property import Property

debug = False

class PropertiesTestCase(basetest.BaseTestCase):

    def setUp(self):
        "init test values"
        V = {
            'AUTO': 'auto',
            'INHERIT': 'inherit',
            
            '0': ('0', '-0', '+0'),
            'NUMBER': ('0', '-0', '+0', '100.1', '-100.1', '+100.1'),
            'PERCENTAGE': ('0%', '-0%', '+0%', '100.1%', '-100.1%', '+100.1%'),
            
            'EM': '1.2em',
            'EX': '1.2ex',
            'PX': '1.2px',
            'CM': '1.2cm',
            'MM': '1.2mm',
            'IN': '1.2in',
            'PT': '1.2pt',
            'PC': '1.2pc',
    
            'ANGLES': ('1deg', '1rad', '1grad'),
            'TIMES': ('1s', '1ms'),
            'FREQUENCIES': ('1hz', '1khz'),
            'DIMENSION': ('1dimension', '1_dimension', '1dimension2'),
            'STRING': ('"string"', "'STRING'"),
            'URI': ('url(x)', 'URL("x")', "url(')')"),
            'IDENT': ('ident', 'IDENT', '_IDENT', '_2', 'i-2'),
            'ATTR': ('attr(x)'),
            'RECT': ('rect(1,2,3,4)'),
            #?
            'CLIP': ('rect(1,2,3,4)'),
            'FUNCTION': (),
            
            'COLOR': 'red',
            'HEX3': '#123',
            'HEX6': '#123abc',
            'RGB': 'rgb(1,2,3)',
            'RGB100': 'rgb(1%,2%,100%)',
            'RGBA': 'rgb(1,2,3, 1)',
            'RGBA100': 'rgb(1%,2%,100%, 0)',
            'HSL': 'hsl(1,2,3)',
            'HSLA': 'hsl(1,2,3, 1)'            
             }        
        def expanded(*keys):
            r = []
            for k in keys:
                if isinstance(V[k], basestring):
                    r.append(V[k])
                else:
                    r.extend(list(V[k]))
            return r

        # before adding combined
        self.V = V
        self.ALL = list(self._valuesofkeys(V.keys())) 
        
        # combined values, only keys of V may be used!
        self.V['LENGTHS'] = expanded('0', 'EM', 'EX', 'PX', 'CM', 'MM', 'IN', 'PT', 'PC')
        self.V['COLORS'] = expanded('COLOR', 'HEX3', 'HEX6', 'RGB', 'RGB100')
        self.V['COLORS3'] = expanded('RGBA', 'RGBA100', 'HSL', 'HSLA')
        
        

    def _allvalues(self):
        "Return list of **all** possible values as simple list"
        return copy.copy(self.ALL)
            
    def _valuesofkeys(self, keys):
        "Generate all distinct values in given keys of self.V"
        done = []
        for key in keys:
            v = self.V[key]
            if isinstance(v, basestring):
                # single value
                if v not in done: 
                    done.append(v)
                    yield v
            else:
                # a list of values
                for value in v:
                    if value not in done: 
                        done.append(value)
                        yield value
        
    def _check(self, name, keys):
        """
        Check each value in values if for property name p.name==exp.
        """
        notvalid = self._allvalues()

        for value in self._valuesofkeys(keys):
            if debug:
                print '+True?', Property(name, value).valid, value
            self.assertEqual(Property(name, value).valid, True)
            if value in notvalid:
                notvalid.remove(value)
        
        for value in notvalid:
            if debug:
                print '-False?', Property(name, value).valid, value
            self.assertEqual(Property(name, value).valid, False)
                
    def test_properties(self):
        "properties"
        tests = {
            'color': ('COLORS', 'INHERIT'),
            'left': ('LENGTHS', 'PERCENTAGE', 'AUTO', 'INHERIT'),
            'opacity': ('NUMBER', 'INHERIT')
        }
        for name, keys in tests.items():
            # keep track of valid keys
            self._check(name, keys)


if __name__ == '__main__':
    import logging
    import unittest
    cssutils.log.setLevel(logging.FATAL)
    debug = True
    unittest.main()
