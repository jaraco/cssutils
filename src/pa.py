# -*- coding: utf-8 -*-
from pprint import pprint as pp
from cssutils.prodsparser import *
import cssutils

# PRODUCTION FOR CSSColor
types = cssutils.cssproductions.CSSProductions

sign = Prod(name='sign +-', match=lambda t, v: v in u'+-',
            optional=True)
value = Prod(name='value', 
             match=lambda t, v: t in (types.NUMBER, types.PERCENTAGE), 
             toSeq=cssutils.css.CSSPrimitiveValue,
             toStore='test'
             )
comma = Prod(name='comma', match=lambda t, v: v == u',')
endfunc = Prod(name='end FUNC ")"', match=lambda t, v: v == u')')

# COLOR PRODUCTION
funccolor = Sequence([
    Prod(name='FUNC', match=lambda t, v: v in ('rgb(', 'rgba(', 'hsl(', 'hsla(') and t == types.FUNCTION, 
         toStore='colorType' ),
    sign, value,
    # more values starting with Comma
    # should use store where colorType is saved to 
    # define min and may, closure?
    Sequence([comma, sign, value], minmax=lambda: (2, 2)), 
    # end of FUNCTION )
    endfunc
 ])
colorprods = Choice([funccolor,
                      Prod(name='HEX color', 
                           match=lambda t, v: t == types.HASH and 
                            len(v) == 4 or len(v) == 7,
                            toSeq=cssutils.css.CSSPrimitiveValue,
                            toStore='colorType'
                           ),
                      Prod(name='named color', match=lambda t, v: t == types.IDENT,
                           toSeq=cssutils.css.CSSPrimitiveValue,
                           toStore='colorType'),
                      ]
    )

# ----

# PRODUCTION FOR Rect
rectvalue = Prod(name='value in rect()', 
                 match=lambda t, v: t == types.DIMENSION or\
                                    str(v) in ('auto', '0'), 
                 toSeq=cssutils.css.CSSPrimitiveValue)
rectprods = Sequence([Prod(name='FUNC rect(', 
                           match=lambda t, v: v == u'rect('),  #normalized!
                           rectvalue,
                           Sequence([comma, rectvalue], minmax=lambda: (3,3)),
                           endfunc 
                           ])

# EXAMPLE
name, productions = u'CSSColor', colorprods
text = 'rgb(1%,   \n2% , -3.0%)' 
# RESULT: colorType filled, in test all values
store = {'test': [] }

wellformed, seq, unusedtokens = ProdsParser().parse(text, name, productions,  
                                                    store=store)

print '- WELLFORMED:', wellformed
print '- STORE:', store
print '- TOKENS:', list(unusedtokens) 
pp(seq)
