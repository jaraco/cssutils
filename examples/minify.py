import logging, StringIO

EXPOUT = "@variables{c:#0f0}a{color:var(c)}\na{color:#0f0}\n"
EXPERR = u'Property: Found valid "CSS Level 2.1" value: #0f0 [6:9: color]\n'

def main():
    import cssutils
    import cssutils.script
    
    css = '''
    @variables {
        c: #0f0;
    }
    a {
        color: var(c);
    }
    '''
    s = cssutils.parseString(css)
    
    cssutils.ser.prefs.useMinified()
    cssutils.ser.prefs.resolveVariables = False
    print s.cssText

    # reset
    cssutils.ser.prefs.resolveVariables = True
    print s.cssText

    
if __name__ == '__main__':
    main()