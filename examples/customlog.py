import logging, StringIO

EXPOUT = '''INFO    Property: No CSS2 Property: u'a'. [1:5: a]

'''
EXPERR = u"Property: No CSS2 Property: u'a'. [1:5: a]\n"

def main():
    import cssutils
    
    st = StringIO.StringIO()
    h = logging.StreamHandler(st)
    h.setFormatter(logging.Formatter('%(levelname)s    %(message)s'))
    cssutils.log.addHandler(h) 
    ##cssutils.log.setLevel(logging.DEBUG)
     
    sheet = cssutils.parseString('a { a: 1; }')
    print st.getvalue()


# OUTPUTS:
#--- customlog content  ---
#INFO:mylog:Property: No CSS2 Property: "x".
#INFO:mylog:CSSValue: Unable to validate as no or unknown property context set for
# this value: u'1'
#ERROR:mylog:CSSStylesheet: CSSImportRule not allowed here. [1:13: @import]


if __name__ == '__main__':
    main()