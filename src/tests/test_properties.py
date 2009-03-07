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
        self.V['COLORS'] = expanded('HEX3', 'HEX6', 'RGB', 'RGB100')
        self.V['COLORS3'] = expanded('RGBA', 'RGBA100', 'HSL', 'HSLA')
        
    def _allvalues(self):
        "Return list of **all** possible values as simple list"
        return copy.copy(self.ALL)
            
    def _valuesofkeys(self, keys):
        "Generate all distinct values in given keys of self.V"
        done = []
        for key in keys:
            if isinstance(key, list):
                # not a key but a list of values, return directly
                for v in key:
                    yield v
            else:
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
            if debug == name:
                print '+True?', Property(name, value).valid, value
            self.assertEqual(True, Property(name, value).valid)
            if value in notvalid:
                notvalid.remove(value)
        for value in notvalid:
            if name == debug:
                print '-False?', Property(name, value).valid, value
            self.assertEqual(False, Property(name, value).valid)
                
    def test_properties(self):
        "properties"
        tests = {
            # propname: key or [list of values]
            'color': ('COLORS', 'INHERIT', ['red']),
            'left': ('LENGTHS', 'PERCENTAGE', 'AUTO', 'INHERIT'),
            # CSS3 COLOR
            'opacity': ('NUMBER', 'INHERIT'),
            # CSS3 PAGED MEDIA
            'fit': (['fill', 'hidden', 'meet', 'slice'],),
            'fit-position': ('AUTO', 'LENGTHS', 'PERCENTAGE', 
                             ['top left', 
                              '0% 50%',
                              '1cm 5em',
                              'bottom']),
            'image-orientation': ('AUTO', '0', 'ANGLES'),
            'page': ('AUTO', 'IDENT', 'INHERIT'), # inherit is an IDENT?
            'page-break-inside': ('AUTO', 'INHERIT', ['avoid']),
            'size': ('AUTO', 'LENGTHS', ['1em 1em', 
                                         'a4 portrait',
                                         'b4 landscape',
                                         'A5 PORTRAIT']),
            'orphans': ('0', ['1', '99999'], 'INHERIT'),
            'widows': ('0', ['1', '99999'], 'INHERIT')
        }
        for name, keys in tests.items():
            # keep track of valid keys
            self._check(name, keys)

    def test_validate(self):
        "Property.validate() and Property.valid"
        tests = {
            # (default L2, no default, no profile, L2, Color L3)
            'red': (True, True, True, True, True),
            'rgba(1,2,3,1)': (False, True, True, False, True),
            '1': (False, False, False, False, False)
        }
        for v, rs in tests.items():
            p = Property('color', v)
            cssutils.profile.defaultProfiles = \
                cssutils.profile.CSS_LEVEL_2
            self.assertEqual(rs[0], p.valid)
            cssutils.profile.defaultProfiles = None
            self.assertEqual(rs[1], p.valid)

            self.assertEqual(rs[2], p.validate())
            self.assertEqual(rs[3], p.validate(
                profiles=cssutils.profile.CSS_LEVEL_2))
            self.assertEqual(rs[4], p.validate(
                cssutils.profile.CSS3_COLOR))


if __name__ == '__main__':
    debug = 'fit-position'
    import logging
    import unittest
    cssutils.log.setLevel(logging.FATAL)
    #debug = True
    unittest.main()
