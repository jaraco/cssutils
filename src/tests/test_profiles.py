"""Testcases for cssutils.css.CSSValue and CSSPrimitiveValue."""
__version__ = '$Id: test_cssvalue.py 1443 2008-08-31 13:54:39Z cthedot $'

import sys
import basetest
import cssutils
from cssutils.profiles import profiles, NoSuchProfileException

class ProfilesTestCase(basetest.BaseTestCase):

    P1 = {
        '-test-x': '{num}', 
        '-test-y': '{ident}|{percentage}',
        # custom validation function 
        '-test-z': lambda(v): int(v) > 0 
        }  

    def test_knownnames(self):
        "Profiles.knownnames"
        p = cssutils.profiles.Profiles()
        p.removeProfile(all=True)
        p.addProfile('test', self.P1)
        self.assertEqual(p.knownnames, self.P1.keys())
        p.removeProfile(all=True)
        self.assertEqual(p.knownnames, [])
        
    def test_profiles(self):
        "Profiles.profiles"
        p = cssutils.profiles.Profiles()
        p.removeProfile(all=True)
        p.addProfile('test', self.P1)
        self.assertEqual(p.profiles, ['test'])
        p.removeProfile(all=True)
        self.assertEqual(p.profiles, [])

    def test_addProfile(self):
        "Profiles.addProfile with custom validation function"
        # unknown profile
        self.assertRaises(NoSuchProfileException, 
                          lambda: list(profiles.propertiesByProfile('NOTSET')) )

        # new profile
        profiles.addProfile('test', self.P1)
        
        props = self.P1.keys()
        props.sort()
        self.assertEqual(props, list(profiles.propertiesByProfile('test')))
        
        cssutils.log.raiseExceptions = False
        tests = {
            ('-test-x', '1'): True,     
            ('-test-x', 'a'): False,     
            ('-test-y', 'a'): True,     
            ('-test-y', '0.1%'): True,     
            ('-test-z', '1'): True,     
            ('-test-z', '-1'): False,     
            ('-test-z', 'x'): False     
            }
        for test, v in tests.items():
            self.assertEqual(v, profiles.validate(*test))
            self.assertEqual((v, ['test']), profiles.validateWithProfile(*test))
            
        cssutils.log.raiseExceptions = True
        
        # raises:
        if sys.version_info[0:2] == (2,4):
            # Python 2.4 has a different msg...
            self.assertRaisesMsg(Exception, u"invalid literal for int(): x", 
                                 profiles.validate, u'-test-z', u'x')
        else:
            self.assertRaisesMsg(Exception, u"invalid literal for int() with base 10: 'x'", 
                                 profiles.validate, u'-test-z', u'x')

    def test_removeProfile(self):
        "Profiles.removeProfile()"
        p = cssutils.profiles.Profiles()
        self.assertEqual(3, len(p.profiles))
        p.removeProfile(p.CSS_LEVEL_2)
        self.assertEqual(2, len(p.profiles))
        p.removeProfile(all=True)
        self.assertEqual(0, len(p.profiles))

    def test_validateWithProfile(self):
        "Profiles.validate(), Profiles.validateWithProfile()"
        p = cssutils.profiles.Profiles()
        tests = {
            ('color', 'red', None): (True, [p.CSS_LEVEL_2]),
            ('color', 'red', p.CSS_LEVEL_2): (True, [p.CSS_LEVEL_2]),
            ('color', 'red', p.CSS_COLOR_LEVEL_3): (True, [p.CSS_COLOR_LEVEL_3]),
            ('color', 'rgba(0,0,0,0)', None): (True, [p.CSS_COLOR_LEVEL_3]),
            ('color', 'rgba(0,0,0,0)', p.CSS_LEVEL_2): (True, [p.CSS_COLOR_LEVEL_3]),
            ('color', 'rgba(0,0,0,0)', p.CSS_COLOR_LEVEL_3): (True, [p.CSS_COLOR_LEVEL_3]),
            ('color', '1px', None): (False, [p.CSS_COLOR_LEVEL_3, p.CSS_LEVEL_2]),
            ('color', '1px', p.CSS_LEVEL_2): (False, [p.CSS_COLOR_LEVEL_3, p.CSS_LEVEL_2]),
            ('color', '1px', p.CSS_COLOR_LEVEL_3): (False, [p.CSS_COLOR_LEVEL_3, p.CSS_LEVEL_2]),

            ('opacity', '1', None): (True, [p.CSS_COLOR_LEVEL_3]),
            ('opacity', '1', p.CSS_LEVEL_2): (True, [p.CSS_COLOR_LEVEL_3]),
            ('opacity', '1', p.CSS_COLOR_LEVEL_3): (True, [p.CSS_COLOR_LEVEL_3]),
            ('opacity', '1px', None): (False, [p.CSS_COLOR_LEVEL_3]),
            ('opacity', '1px', p.CSS_LEVEL_2): (False, [p.CSS_COLOR_LEVEL_3]),
            ('opacity', '1px', p.CSS_COLOR_LEVEL_3): (False, [p.CSS_COLOR_LEVEL_3]),

            ('-x', '1', None): (False, []),
            ('-x', '1', p.CSS_LEVEL_2): (False, []),
            ('-x', '1', p.CSS_COLOR_LEVEL_3): (False, []),
        }
        for test, r in tests.items():
            self.assertEqual(p.validate(test[0], test[1]), r[0])
            self.assertEqual(p.validateWithProfile(*test), r)
            
        

    def test_propertiesByProfile(self):
        "Profiles.propertiesByProfile"
        self.assertEqual(['color', 'opacity'], 
                         list(profiles.propertiesByProfile(profiles.CSS_COLOR_LEVEL_3)))
        
    def test_csscolorlevel3(self):
        "CSS Color Module Level 3"
        CSS2 = [profiles.CSS_LEVEL_2]
        CM3 = [profiles.CSS_COLOR_LEVEL_3]
        CSS2_CM3 = [profiles.CSS_COLOR_LEVEL_3, profiles.CSS_LEVEL_2]
        
        # (propname, propvalue): (valid, validprofile)

        namedcolors = '''transparent, orange,
                         aqua, black, blue, fuchsia, gray, green, lime, maroon,
                         navy, olive, purple, red, silver, teal, white, yellow'''
        for color in namedcolors.split(','):
            color = color.strip()            
            self.assertEqual(True, profiles.validate('color', color))
            self.assertEqual((True, CSS2), profiles.validateWithProfile('color', color))

        uicolor = 'ActiveBorder|ActiveCaption|AppWorkspace|Background|ButtonFace|ButtonHighlight|ButtonShadow|ButtonText|CaptionText|GrayText|Highlight|HighlightText|InactiveBorder|InactiveCaption|InactiveCaptionText|InfoBackground|InfoText|Menu|MenuText|Scrollbar|ThreeDDarkShadow|ThreeDFace|ThreeDHighlight|ThreeDLightShadow|ThreeDShadow|Window|WindowFrame|WindowText'
        for color in uicolor.split('|'):
            self.assertEqual(True, profiles.validate('color', color))
            self.assertEqual((True, CSS2), profiles.validateWithProfile('color', color))
        
        tests = {
            ('color', 'inherit'): (True, CSS2),
            ('color', 'currentColor'): (True, CM3),
            ('color', 'currentcolor'): (True, CM3),
            # names
            ('color', 'x'): (False, CSS2_CM3),
            ('color', 'black'): (True, CSS2),
#            # hex
            ('color', '#'): (False, CSS2_CM3),
            ('color', '#0'): (False, CSS2_CM3),
            ('color', '#00'): (False, CSS2_CM3),
            ('color', '#0000'): (False, CSS2_CM3),
            ('color', '#00000'): (False, CSS2_CM3),
            ('color', '#0000000'): (False, CSS2_CM3),
            ('color', '#00j'): (False, CSS2_CM3),
            ('color', '#j00000'): (False, CSS2_CM3),
            ('color', '#000'): (True, CSS2),
            ('color', '#000000'): (True, CSS2),
#            # rgb
            ('color', 'rgb(0,1,1)'): (True, CSS2),
            ('color', 'rgb( 0 , 1 , 1 )'): (True, CSS2),
# TODO?:
#            ('color', 'rgb(/**/ 0 /**/ , /**/ 1 /**/ , /**/ 1 /**/ )'): (True, CSS2),
            ('color', 'rgb(-10,555,1)'): (True, CSS2), # should be clipped
            ('color', 'rgb(100%, 1.5%, 0%)'): (True, CSS2),
            ('color', 'rgb(150%, -20%, 0%)'): (True, CSS2), # should be clipped
            ('color', 'rgb(0.0,1,1)'): (False, CSS2_CM3), # int!
            ('color', 'rgb(0)'): (False, CSS2_CM3),
            ('color', 'rgb(0, 1)'): (False, CSS2_CM3),
            ('color', 'rgb(0, 1, 1, 1)'): (False, CSS2_CM3),
            ('color', 'rgb(0, 1, 0%)'): (False, CSS2_CM3), # mix
#            # rgba
            ('color', 'rgba(1,1,1,1)'): (True, CM3),
            ('color', 'rgba( 1 , 1 , 1 , 1 )'): (True, CM3),
            ('color', 'rgba(100%, 0%, 0%, 1)'): (True, CM3),
            ('color', 'rgba(0, 1, 1.0, 1)'): (False, CSS2_CM3), # int
            ('color', 'rgba(0)'): (False, CSS2_CM3),
            ('color', 'rgba(0, 1)'): (False, CSS2_CM3),
            ('color', 'rgba(0, 1, 1, 1, 1)'): (False, CSS2_CM3),
            ('color', 'rgba(100%, 0%, 0%, 1%)'): (False, CSS2_CM3),
            ('color', 'rgba(100%, 0%, 0, 1)'): (False, CSS2_CM3), # mix
#            # hsl
            ('color', 'hsl(1,1%,1%)'): (True, CM3),
            ('color', 'hsl( 1 , 1% , 1% )'): (True, CM3),
            ('color', 'hsl(-1000,555.5%,-61.5%)'): (True, CM3),
            ('color', 'hsl(1.5,1%,1%)'): (False, CSS2_CM3), # int
            ('color', 'hsl(1,1,1%)'): (False, CSS2_CM3), # %
            ('color', 'hsl(1,1%,1)'): (False, CSS2_CM3), # %
#            #hsla
            ('color', 'hsla(1,1%,1%,1)'): (True, CM3),
            ('color', 'hsla( 1, 1% , 1% , 1 )'): (True, CM3),
            ('color', 'hsla(-1000,555.5%,-61.5%, 0.5)'): (True, CM3),
            ('color', 'hsla(1.5,1%,1%, 1)'): (False, CSS2_CM3), # int
            ('color', 'hsla(1,1,1%, 1)'): (False, CSS2_CM3), # %
            ('color', 'hsla(1,1%,1, 1)'): (False, CSS2_CM3), # %
            ('color', 'hsla(1,1%,1%, 1%)'): (False, CSS2_CM3), # %
#            # opacity
            ('opacity', 'inherit'): (True, CM3),
            ('opacity', '0'): (True, CM3),
            ('opacity', '0.0'): (True, CM3),
            ('opacity', '0.42342'): (True, CM3),
            ('opacity', '1'): (True, CM3),
            ('opacity', '1.0'): (True, CM3),
            # should be clipped but valid
            ('opacity', '-0'): (True, CM3),
            ('opacity', '-0.1'): (True, CM3),
            ('opacity', '-10'): (True, CM3),
            ('opacity', '2'): (True, CM3),
            # invalid
            ('opacity', 'a'): (False, CM3),
            ('opacity', '#000'): (False, CM3),
            ('opacity', '+1'): (False, CM3),
        }
        for test, (v, p) in tests.items():            
            self.assertEqual(v, profiles.validate(*test))
            self.assertEqual((v, p), profiles.validateWithProfile(*test))

        # not css2 but 3
        self.assertEqual((True, CM3), profiles.validateWithProfile('opacity', '0'))

if __name__ == '__main__':
    import unittest
    unittest.main()
