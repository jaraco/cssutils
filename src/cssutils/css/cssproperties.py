"""CSS2Properties implements DOM Level 2 CSS CSS2Properties?

cssvalues uaed as a property validator

This module has an importable object, cssvalues, that contains a 
dictionary of compiled regular expressions.  The keys of this 
dictionary are all of the valid CSS property names.  The values
are compiled regular expressions that can be used to validate
the values for that property.  (Actually, the values are references
to the 'match' method of a compiled regular expression, so that
they are simply called like functions.)

written by Kevin D. Smith, thanks!

TODO: CSS2Properties
##DOMImplementation
##=================
##The interface found within this section are not mandatory. A DOM
##application can use the hasFeature method of the DOMImplementation
##interface to determine whether it is supported or not. The feature
##string for this extended interface listed in this section is "CSS2"
##and the version is "2.0".

# TEST
"""
__all__ = ['cssvalues']
__docformat__ = 'restructuredtext'
__author__ = "$LastChangedBy$"
__date__ = '$Date$'
__version__ = '0.9.2a1, SVN revision $Revision$'

import re

"""
Define some regular expression fragments that will be used as 
macros within the CSS property value regular expressions.

"""
MACROS = {
    'ident': r'[-]?{nmstart}{nmchar}*',
    'name': r'{nmchar}+',
    'nmstart': r'[_a-z]|{nonascii}|{escape}',
    'nonascii': r'[^\0-\177]',
    'unicode': r'\\[0-9a-f]{1,6}(\r\n|[ \n\r\t\f])?',
    'escape': r'{unicode}|\\[ -~\200-\777]',
#   'escape': r'{unicode}|\\[ -~\200-\4177777]',
    'int': r'[-]?\d+',
    'nmchar': r'[\w-]|{nonascii}|{escape}',
    'num': r'[-]?\d+|\d*\.\d+',
    'number': r'{num}',
    'string': r'{string1}|{string2}',
    'string1': r'"(\\\"|[^\"])*"',
    'string2': r"'(\\\'|[^\'])*'",
    'nl': r'\n|\r\n|\r|\f',
    'w': r'\s*',

    'integer': r'{int}',
    'length': r'0|{num}(em|ex|px|in|cm|mm|pt|pc)',
    'angle': r'0|{num}(deg|grad|rad)',
    'time': r'0|{num}m?s',
    'frequency': r'0|{num}k?Hz',
    'color': r'(maroon|red|orange|yellow|olive|purple|fuchsia|white|lime|green|navy|blue|aqua|teal|black|silver|gray|ActiveBorder|ActiveCaption|AppWorkspace|Background|ButtonFace|ButtonHighlight|ButtonShadow|ButtonText|CaptionText|GrayText|Highlight|HighlightText|InactiveBorder|InactiveCaption|InactiveCaptionText|InfoBackground|InfoText|Menu|MenuText|Scrollbar|ThreeDDarkShadow|ThreeDFace|ThreeDHighlight|ThreeDLightShadow|ThreeDShadow|Window|WindowFrame|WindowText)|#[0-9a-f]{3}|#[0-9a-f]{6}|rgb\({w}{int}{w},{w}{int}{w},{w}{int}{w}\)|rgb\({w}{num}%{w},{w}{num}%{w},{w}{num}%{w}\)',
    'uri': r'url\({w}({string}|(\\\)|[^\)])+){w}\)',
    'percentage': r'{num}%',
    'border-style': 'none|hidden|dotted|dashed|solid|double|groove|ridge|inset|outset',
    'border-color': '{color}',
    'border-width': '{length}|thin|medium|thick',

    'background-color': r'{color}|transparent|inherit',
    'background-image': r'{uri}|none|inherit',

    ##'background-position': r'(({percentage}|{length}|left|center|right)(\s*{percentage}|{length}|top|center|bottom)?)|(left|center|right|top|center|bottom)(\s*(left|center|right|top|center|bottom))?|inherit',
    'background-position': r'(({percentage}|{length}|top|center|bottom)\s*({percentage}|{length}|left|center|right)?)|inherit',
    'background-repeat': r'repeat|repeat-x|repeat-y|no-repeat|inherit',
    'background-attachment': r'scroll|fixed|inherit',

    'shape': r'rect\(({w}({length}|auto}){w},){3}{w}({length}|auto){w}\)',
    'counter': r'counter\({w}{identifier}{w}(?:,{w}{list-style-type}{w})?\)',
    'identifier': r'{ident}',
    'family-name': r'{string}|{identifier}',
    'generic-family': r'serif|sans-serif|cursive|fantasy|monospace',
    'absolute-size': r'(x?x-)?(small|large)|medium',
    'relative-size': r'smaller|larger',
    'font-family': r'(({family-name}|{generic-family}){w},{w})*({family-name}|{generic-family})|inherit',
    'font-size': r'{absolute-size}|{relative-size}|{length}|{percentage}|inherit',
    'font-style': r'normal|italic|oblique|inherit',
    'font-variant': r'normal|small-caps|inherit',
    'font-weight': r'normal|bold|bolder|lighter|[1-9]00|inherit',
    'line-height': r'normal|{number}|{length}|{percentage}|inherit',
    'list-style-image': r'{uri}|none|inherit',
    'list-style-position': r'inside|outside|inherit',
    'list-style-type': r'disc|circle|square|decimal|decimal-leading-zero|lower-roman|upper-roman|lower-greek|lower-(latin|alpha)|upper-(latin|alpha)|armenian|georgian|none|inherit',
    'margin-width': r'{length}|{percentage}|auto',
    'outline-color': r'{color}|invert|inherit',
    'outline-style': r'{border-style}|inherit',
    'outline-width': r'{border-width}|inherit',
    'padding-width': r'{length}|{percentage}',
    'specific-voice': r'{identifier}',
    'generic-voice': r'male|female|child',
    'content': r'{string}|{uri}|{counter}|attr\({w}{identifier}{w}\)|open-quote|close-quote|no-open-quote|no-close-quote',
    'border-attrs': r'{border-width}|{border-style}|{border-color}',
    'background-attrs': r'{background-color}|{background-image}|{background-repeat}|{background-attachment}|{background-position}',
    'list-attrs': r'{list-style-type}|{list-style-position}|{list-style-image}',
    'font-attrs': r'{font-style}|{font-variant}|{font-weight}',
    'outline-attrs': r'{outline-color}|{outline-style}|{outline-width}',
    'text-attrs': r'underline|overline|line-through|blink',
}


"""
Define the regular expressions for validation all CSS values
"""
cssvalues = {
    'azimuth': r'{angle}|(behind\s+)?(left-side|far-left|left|center-left|center|center-right|right|far-right|right-side)(\s+behind)?|behind|leftwards|rightwards|inherit',
    'background-attachment': r'{background-attachment}',
    'background-color': r'{background-color}',
    'background-image': r'{background-image}',
    'background-position': r'{background-position}',
    'background-repeat': r'{background-repeat}',

    # Each piece should only be allowed one time
    'background': r'{background-attrs}(\s+{background-attrs})*|inherit',
    'border-collapse': r'collapse|separate|inherit',
    'border-color': r'({border-color}|transparent)(\s+({border-color}|transparent)){0,3}|inherit',
    'border-spacing': r'{length}(\s+{length})?|inherit',
    'border-style': r'{border-style}(\s+{border-style}){0,3}|inherit',
    'border-top': r'{border-attrs}(\s+{border-attrs})*|inherit',
    'border-right': r'{border-attrs}(\s+{border-attrs})*|inherit',
    'border-bottom': r'{border-attrs}(\s+{border-attrs})*|inherit',
    'border-left': r'{border-attrs}(\s+{border-attrs})*|inherit',
    'border-top-color': r'{border-color}|transparent|inherit',
    'border-right-color': r'{border-color}|transparent|inherit',
    'border-bottom-color': r'{border-color}|transparent|inherit',
    'border-left-color': r'{border-color}|transparent|inherit',
    'border-top-style': r'{border-style}|inherit',
    'border-right-style': r'{border-style}|inherit',
    'border-bottom-style': r'{border-style}|inherit',
    'border-left-style': r'{border-style}|inherit',
    'border-top-width': r'{border-width}|inherit',
    'border-right-width': r'{border-width}|inherit',
    'border-bottom-width': r'{border-width}|inherit',
    'border-right-width': r'{border-width}|inherit',
    'border-width': r'{border-width}(\s+{border-width}){0,3}|inherit',
    'border': r'{border-attrs}(\s+{border-attrs})*|inherit',
    'bottom': r'{length}|{percentage}|auto|inherit',
    'caption-side': r'top|bottom|inherit',
    'clear': r'none|left|right|both|inherit',
    'clip': r'{shape}|auto|inherit',
    'color': r'{color}|inherit',
    'content': r'normal|{content}(\s+{content})*|inherit',
    'counter-increment': r'({identifier}(\s+{integer})?)(\s+({identifier}(\s+{integer})))*|none|inherit',
    'counter-reset': r'({identifier}(\s+{integer})?)(\s+({identifier}(\s+{integer})))*|none|inherit',
    'cue-after': r'{uri}|none|inherit',
    'cue-before': r'{uri}|none|inherit',
    'cue': r'({uri}|none|inherit){1,2}|inherit',
    'cursor': r'((({uri}{w},{w})*)?(auto|crosshair|default|pointer|move|(e|ne|nw|n|se|sw|s|w)-resize|text|wait|help|progress))|inherit',
    'direction': r'ltr|rtl|inherit',
    'display': r'inline|block|list-item|run-in|inline-block|table|inline-table|table-row-group|table-header-group|table-footer-group|table-row|table-column-group|table-column|table-cell|table-caption|none|inherit',
    'elevation': r'{angle}|below|level|above|higher|lower|inherit',
    'empty-cells': r'show|hide|inherit',
    'float': r'left|right|none|inherit',
    'font-family': r'{font-family}',
    'font-size': r'{font-size}',
    'font-style': r'{font-style}',
    'font-variant': r'{font-variant}',
    'font-weight': r'{font-weight}',
    'font': r'({font-attrs}\s+)*{font-size}({w}/{w}{line-height})?\s+{font-family}|caption|icon|menu|message-box|small-caption|status-bar|inherit',
    'height': r'{length}|{percentage}|auto|inherit',
    'left': r'{length}|{percentage}|auto|inherit',
    'letter-spacing': r'normal|{length}|inherit',
    'line-height': r'{line-height}',
    'list-style-image': r'{list-style-image}',
    'list-style-position': r'{list-style-position}',
    'list-style-type': r'{list-style-type}',
    'list-style': r'{list-attrs}(\s+{list-attrs})*|inherit',
    'margin-right': r'{margin-width}|inherit',
    'margin-left': r'{margin-width}|inherit',
    'margin-top': r'{margin-width}|inherit',
    'margin-bottom': r'{margin-width}|inherit',
    'margin': r'{margin-width}(\s+{margin-width}){0,3}|inherit',
    'max-height': r'{length}|{percentage}|none|inherit',
    'max-width': r'{length}|{percentage}|none|inherit',
    'min-height': r'{length}|{percentage}|none|inherit',
    'min-width': r'{length}|{percentage}|none|inherit',
    'orphans': r'{integer}|inherit',
    'outline-color': r'{outline-color}',
    'outline-style': r'{outline-style}',
    'outline-width': r'{outline-width}',
    'outline': r'{outline-attrs}(\s+{outline-attrs})*|inherit',
    'overflow': r'visible|hidden|scroll|auto|inherit',
    'padding-top': r'{padding-width}|inherit',
    'padding-right': r'{padding-width}|inherit',
    'padding-bottom': r'{padding-width}|inherit',
    'padding-left': r'{padding-width}|inherit',
    'padding': r'{padding-width}(\s+{padding-width}){0,3}|inherit',
    'page-break-after': r'auto|always|avoid|left|right|inherit',
    'page-break-before': r'auto|always|avoid|left|right|inherit',
    'page-break-inside': r'avoid|auto|inherit',
    'pause-after': r'{time}|{percentage}|inherit',
    'pause-before': r'{time}|{percentage}|inherit',
    'pause': r'({time}|{percentage}){1,2}|inherit',
    'pitch-range': r'{number}|inherit',
    'pitch': r'{frequency}|x-low|low|medium|high|x-high|inherit',
    'play-during': r'{uri}(\s+(mix|repeat))*|auto|none|inherit',
    'position': r'static|relative|absolute|fixed|inherit',
    'quotes': r'({string}\s+{string})(\s+{string}\s+{string})*|none|inherit',
    'richness': r'{number}|inherit',
    'right': r'{length}|{percentage}|auto|inherit',
    'speak-header': r'once|always|inherit',
    'speak-numeral': r'digits|continuous|inherit',
    'speak-punctuation': r'code|none|inherit',
    'speak': r'normal|none|spell-out|inherit',
    'speech-rate': r'{number}|x-slow|slow|medium|fast|x-fast|faster|slower|inherit',
    'stress': r'{number}|inherit',
    'table-layout': r'auto|fixed|inherit',
    'text-align': r'left|right|center|justify|inherit',
    'text-decoration': r'none|{text-attrs}(\s+{text-attrs})*|inherit',
    'text-indent': r'{length}|{percentage}|inherit',
    'text-transform': r'capitalize|uppercase|lowercase|none|inherit',
    'top': r'{length}|{percentage}|auto|inherit',
    'unicode-bidi': r'normal|embed|bidi-override|inherit',
    'vertical-align': r'baseline|sub|super|top|text-top|middle|bottom|text-bottom|{percentage}|{length}|inherit',
    'visibility': r'visible|hidden|collapse|inherit',
    'voice-family': r'({specific-voice}|{generic-voice}{w},{w})*({specific-voice}|{generic-voice})|inherit',
    'volume': r'{number}|{percentage}|silent|x-soft|soft|medium|loud|x-loud|inherit',
    'white-space': r'normal|pre|nowrap|pre-wrap|pre-line|inherit',
    'widows': r'{integer}|inherit',
    'width': r'{length}|{percentage}|auto|inherit',
    'word-spacing': r'normal|{length}|inherit',
    'z-index': r'auto|{integer}|inherit',
}


def expand_macros(tokdict):
    """ Expand macros in token dictionary """
    def macro_value(m):
        return '(?:%s)' % MACROS[m.groupdict()['macro']]
    for key, value in tokdict.items():
        while re.search(r'{[a-z][a-z0-9-]*}', value):
            value = re.sub(r'{(?P<macro>[a-z][a-z0-9-]*)}', 
                           macro_value, value)
        tokdict[key] = value
    return tokdict

def compile_regexes(tokdict):
    """ Compile all regular expressions into callable objects """
    for key, value in tokdict.items():
        tokdict[key] = re.compile('^%s$' % value, re.I).match
    return tokdict


compile_regexes(expand_macros(cssvalues))


class CSS2Properties(object):
    """
    Used by CSSStyleDeclaration to check if a property is a CSS property at
    all.
    Includes (private!) functions to convert a DOMname to a CSSname and
    vice versa.
    """
    __reCSStoDOMname = re.compile('-[a-z]', re.I)
    __reDOMtoCSSname = re.compile('[A-Z]')
    _properties = cssvalues.keys()

    @staticmethod
    def __doCSStoDOMname(m):
        "converts CSS name to DOM name like font-style => fontStyle"
        return m.group(0)[1].capitalize()

    @staticmethod
    def __doDOMtoCSSname(m):
        "converts DOM name to CSS name like fontStyle => font-style"
        return '-' + m.group(0).lower()

    @staticmethod
    def _CSSname(DOMname):
        """
        returns CSSname for given DOMname or None if unknown property name
        e.g. DOMname = 'fontStyle' returns 'font-style'
        """
        CSSname = CSS2Properties.__reDOMtoCSSname.sub(
                   CSS2Properties.__doDOMtoCSSname, DOMname)
        if CSSname in CSS2Properties._properties:
            return CSSname
        else:
            return None


if __name__=='__main__':
    c = CSS2Properties()
    #print type(CSS2Properties.color)
    c.color = 'green'
    #print type(CSS2Properties.color), c.color
    print c.color
    del c.color
    #print type(CSS2Properties.color), c.color
    

