#!/usr/bin/env python
"""
CURRENTLY DISFUNCTIONAL !
"""
__docformat__ = 'restructuredtext'

__version__ = '0.3'

##from cssbuilder import *
##from cssexceptions import *
##
##class CSSNormalizerException(Exception):
##    'exceptions during normalizing, should really already come up in CSSParser'
##
##
##class CSSNormalizer(object):
##    'Normalize a CSS Stylesheet'
##
##    # TODO: order in css modules by external config file!
##    _PAGED_MEDIA_MODULE = []
##    _RUBY_MODULE = []
##    _GENERAL_AND_REPLACED_CONTENT_MODULE = ['quotes', 'content', 'counter-increment', 'counter-reset'] # 'display'
##    _BASIC_UI_MODULE = ['cursor']# ...        
##    _TEXT_MODULE = ['direction', 'text-align', 'text-decoration', 'text-indent', 'text-shadow', 'text-transform', 'unicode-bidi', 
##        'letter-spacing', 'word-spacing', 'white-space'
##        ]
##    _FONT_MODULE = ['font', 'font-style', 'font-variant', 'font-weight', 'font-size', 'font-size-adjust', 'font-family',
##        'font-stretch' 
##        ]
##    _LINE_MODULE = ['line-height', 'vertical-align'] # ... text-height ...
##    _LIST_MODULE = ['list-style', 'list-style-type', 'list-style-image', 'list-style-position']
##    # other properties
##    _PRINT_PROFILE = ['clip', 'position', 'right', 'left', 'top', 'bottom', 'z-index',        
##        'caption-side', 'table-layout', 'empty-cells', 'border-collapse', 'border-spacing']
##    _COLOR_MODULE = ['color', 'opacity'] # ... @color-profile 'color-profile', 'rendering-intent'
##    _BACKGROUNDS_MODULE = ['background', 'background-color', 'background-image', 'background-repeat', 'background-attachment', 'background-position']
##    _BOX_MODEL_MODULE = ['display', 'visibility', 'float', 'clear',
##        'overflow', 'overflow-x', 'overflow-y',
##        'width', 'height', 'max-height', 'max-width', 'min-height', 'min-width',
##        'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
##        'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left'
##        ]
##    _BORDER_MODULE = ['border', 'border-top', 'border-right', 'border-bottom', 'border-left',
##        'border-color', 'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color',
##        'border-style', 'border-top-style', 'border-right-style', 'border-bottom-style', 'border-left-style',
##        'border-width', 'border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width',
##        ]
##    ORDER = []
##    ORDER.extend(_BASIC_UI_MODULE)
##    ORDER.extend(_TEXT_MODULE)
##    ORDER.extend(_FONT_MODULE)
##    ORDER.extend(_LINE_MODULE)
##    ORDER.extend(_LIST_MODULE)
##    ORDER.extend(_PRINT_PROFILE)
##    ORDER.extend(_COLOR_MODULE)
##    ORDER.extend(_BACKGROUNDS_MODULE)
##    ORDER.extend(_BOX_MODEL_MODULE)
##    ORDER.extend(_BORDER_MODULE)
##
##    def normalizeDeclarationOrder(self, stylesheet):
##        '''
##        change order of properties to the one specified in ORDER
##        properties not recognized are appended after the ones found in ORDER
##        properties with a backslash (w\idth) are last in the resulting list, again in the above order
##        '''
##        for rule in stylesheet.getRules():
##            newProperties = {}
##            notRecognizedIndex = len(self.ORDER)
##            for p in rule.getStyleDeclaration().getProperties():
##                name = p.name
##                try:
##                    if '\\' in name:    # properties with backslash hack
##                        index = self.ORDER.index(name.replace('\\', '')) + 1000
##                    else:
##                        index = self.ORDER.index(name)
##                    newProperties[index] = p
##                except ValueError, e:
##                    notRecognizedIndex += 1
##                    if '\\' in name:
##                        newProperties[notRecognizedIndex+1000] = p
##                    else:
##                        newProperties[notRecognizedIndex] = p
##            # ? rule.getStyleDeclaration(None)
##            newStyle = cssbuilder.StyleDeclaration()
##            keys = newProperties.keys()
##            keys.sort()
##            for key in keys:
##                np = newProperties[key]
##                newStyle.addProperty(np.getName(), np.getValue())
##            rule.setStyleDeclaration(newStyle)              
##
##
##if __name__ == '__main__':
##    cssstr='''
##body, a, h1 {
##    TESTP\ROPERTY: X;
##    w\idth: 178px
##    TESTPROPERTY: X;
##    color: red;
##    width: 200px;
##    display: block;
##    border: 1px
##    padding: 5px;
##    }
##    '''  
##    import cssparser
##
##    cp = cssparser.CSSParser()
##    cp.parseString(cssstr)  
##    s = cp.getStyleSheet()   
##    print '--- PARSED' 
##    s.pprint()
##
##    normalizer = CSSNormalizer()
##    try:
##        normalizer.normalizeDeclarationOrder(s)
##    except CSSNormalizerException, e:
##        print e
##    print '--- NORMALIZED'
##    s.pprint()
##    
    