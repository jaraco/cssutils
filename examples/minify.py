import logging, StringIO

EXPOUT = "@variables{c:#0f0}a{color:var(c)}\na{color:#0f0}\n"
EXPERR = u'Property: Invalid value for "CSS Color Module Level 3/CSS Level 2.1" property: var(c) [6:9: color]\n'

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
    print s.cssText

    cssutils.ser.prefs.resolveVariables = True
    print s.cssText
    
if __name__ == '__main__':
    main()