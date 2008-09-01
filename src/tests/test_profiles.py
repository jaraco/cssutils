"""Testcases for cssutils.css.CSSValue and CSSPrimitiveValue."""
__version__ = '$Id: test_cssvalue.py 1443 2008-08-31 13:54:39Z cthedot $'

import basetest
import cssutils
from cssutils.profiles import profiles, NoSuchProfileException

class ProfilesTestCase(basetest.BaseTestCase):

    def test_addProfile(self):
        "Profiles.addProfile with custom validation function"
        # unknown profile
        self.assertRaises(NoSuchProfileException, 
                          lambda: list(profiles.propertiesByProfile('NOTSET')) )

        # new profile
        test = {
            '-test-x': '{num}', 
            '-test-y': '{ident}|{percentage}',
            # custom validation function 
            '-test-z': lambda(v): int(v) > 0 
            }        
        profiles.addProfile('test', test)
        
        props = test.keys()
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
            if v:
                p = 'test'
            else:
                p = None 
            self.assertEqual(v, profiles.validate(*test))
            self.assertEqual((v, p), profiles.validateWithProfile(*test))
            
        cssutils.log.raiseExceptions = True
        
        # raises:
        self.assertRaisesMsg(Exception, "invalid literal for int() with base 10: 'x'", 
                             profiles.validate, '-test-z', 'x')
        
    def test_propertiesByProfile(self):
        "Profiles.propertiesByProfile"
        self.assertEqual(['color', 'opacity'], 
                         list(profiles.propertiesByProfile(profiles.CSS_COLOR_LEVEL_3)))
        
    def test_csscolorlevel3(self):
        "CSS Color Module Level 3"
        CSS2 = profiles.CSS_LEVEL_2
        CM3 = profiles.CSS_COLOR_LEVEL_3
        
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
            ('color', 'x'): (False, None),
            ('color', 'black'): (True, CSS2),
            # hex
            ('color', '#'): (False, None),
            ('color', '#0'): (False, None),
            ('color', '#00'): (False, None),
            ('color', '#0000'): (False, None),
            ('color', '#00000'): (False, None),
            ('color', '#0000000'): (False, None),
            ('color', '#00j'): (False, None),
            ('color', '#j00000'): (False, None),
            ('color', '#000'): (True, CSS2),
            ('color', '#000000'): (True, CSS2),
            # rgb
            ('color', 'rgb(0,1,1)'): (True, CSS2),
            ('color', 'rgb(-10,555,1)'): (True, CSS2), # should be clipped
            ('color', 'rgb(100%, 1.5%, 0%)'): (True, CSS2),
            ('color', 'rgb(150%, -20%, 0%)'): (True, CSS2), # should be clipped
            ('color', 'rgb(0.0,1,1)'): (False, None), # int!
            ('color', 'rgb(0)'): (False, None),
            ('color', 'rgb(0, 1)'): (False, None),
            ('color', 'rgb(0, 1, 1, 1)'): (False, None),
            ('color', 'rgb(0, 1, 0%)'): (False, None), # mix
            # rgba
            ('color', 'rgba(1,1,1,1)'): (True, CM3),
            ('color', 'rgba(100%, 0%, 0%, 1)'): (True, CM3),
            ('color', 'rgba(0, 1, 1.0, 1)'): (False, None), # int
            ('color', 'rgba(0)'): (False, None),
            ('color', 'rgba(0, 1)'): (False, None),
            ('color', 'rgba(0, 1, 1, 1, 1)'): (False, None),
            ('color', 'rgba(100%, 0%, 0%, 1%)'): (False, None),
            ('color', 'rgba(100%, 0%, 0, 1)'): (False, None), # mix
            # hsl
            ('color', 'hsl(1,1%,1%)'): (True, CM3),
            ('color', 'hsl(-1000,555.5%,-61.5%)'): (True, CM3),
            ('color', 'hsl(1.5,1%,1%)'): (False, None), # int
            ('color', 'hsl(1,1,1%)'): (False, None), # %
            ('color', 'hsl(1,1%,1)'): (False, None), # %
            #hsla
            ('color', 'hsla(1,1%,1%, 1)'): (True, CM3),
            ('color', 'hsla(-1000,555.5%,-61.5%, 0.5)'): (True, CM3),
            ('color', 'hsla(1.5,1%,1%, 1)'): (False, None), # int
            ('color', 'hsla(1,1,1%, 1)'): (False, None), # %
            ('color', 'hsla(1,1%,1, 1)'): (False, None), # %
            ('color', 'hsla(1,1%,1%, 1%)'): (False, None), # %

            # opacity
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
            ('opacity', 'a'): (False, None),
            ('opacity', '#000'): (False, None),
            ('opacity', '+1'): (False, None),
        }
        for test, (v, p) in tests.items():            
            self.assertEqual(v, profiles.validate(*test))
            self.assertEqual((v, p), profiles.validateWithProfile(*test))

        # not css2 but 3
        self.assertEqual((True, CM3), profiles.validateWithProfile('opacity', '0'))

if __name__ == '__main__':
    import unittest
    unittest.main()
