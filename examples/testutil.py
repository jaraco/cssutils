# -*- coding: utf-8 -*-
"""test utils for tests of examples

A module to test must have:

- main(): a method
- EXPOUT: string which contains expected output
- EXPERR: string which contains expected error output
"""
__all__ = ['TestUtil']

import logging
import os
import StringIO
import sys

import cssutils

PY2x = sys.version_info < (3,0)

class OutReplacement(object):
    "io.StringIO does not work somehow?!"
    def __init__(self):
        self.t = ''
        
    def write(self, t):
        if not PY2x:
            # py3 hack
            if t.startswith('b') and t.endswith("'"):
                t = t[2:-1]
                
        self.t += t
        
    def getvalue(self):
        if not PY2x:
            # py3 hack
            self.t = self.t.replace('\\n', '\n')
            self.t = self.t.replace('\\\\', '\\')
            
        return self.t
    

class TestUtil(object):
    def __init__(self):
        "init out and err to catch both"
        self._out = OutReplacement()#StringIO()
        sys.stdout = self._out
        
        self._err = StringIO.StringIO()
        hdlr = logging.StreamHandler(self._err)
        cssutils.log._log.addHandler(hdlr)
                
    def end(self, expo, expe):
        "return out, err"
        sys.stdout = sys.__stdout__

        out = self._out.getvalue()
        err = self._err.getvalue()

        ok = (out == expo and err == expe)
        if not ok:
            print
            if out != expo:
                print '### out:\n%r\n### != expout:\n%r\n' % (out, expo)
            else:
                print '### err:\n%r\n### != experr:\n%r\n' % (err, expe)
        return ok

modules = 0
errors = 0

def mod(module):
    global modules, errors
    modules += 1
    t = TestUtil()
    module.main()
    ok = t.end(module.EXPOUT, module.EXPERR)
    if not ok:
        errors += 1
    print '---', ok, ':', os.path.basename(module.__file__)
    print 
          
def main():
    if PY2x:
        print "DOCTESTS:::::::::::::"
        # doctests
        import website
        import doctest
        doctest.testmod(website)
        print 
        print 80*'-' 
        print 
        print 

    global modules, errors
    
    import build
    mod(build)
    import customlog
    mod(customlog)
    import imports
    mod(imports) 
    import parse
    mod(parse)
    import selectors_tolower
    mod(selectors_tolower)

    import cssencodings
    mod(cssencodings)
    
    import minify
    mod(minify)
    
    print 
    print 80*'-' 
    print 'Ran %i tests (%i errors).' % (modules, errors)
    if PY2x:
        print '**Check doctest results above!**'
    else:
        print 'doctests do not work in Python 3 (yet?)!'
          
    
if __name__ == '__main__':
    main()
