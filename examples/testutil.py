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
from StringIO import StringIO
import sys

import cssutils

class TestUtil(object):
    def __init__(self):
        "init out and err to catch both"
        self._out = StringIO()
        sys.stdout = self._out
        
        self._err = StringIO()
        hdlr = logging.StreamHandler(self._err)
        cssutils.log._log.addHandler(hdlr)
                
    def end(self, expo, expe):
        "return out, err"
        sys.stdout = sys.__stdout__

        out = self._out.getvalue()
        err = self._err.getvalue()

        ok = (out == expo and err == expe)
        if not ok:
            if out != expo:
                print '### out:\n%r\n### != expout:\n%r\n' % (out, expo)
            else:
                print '### err:\n%r\n### != experr:\n%r\n' % (err, expe)
        return ok

modules = 0
errors = 0

def testmod(module):
    global modules, errors
    modules += 1
    t = TestUtil()
    module.main()
    ok = t.end(module.EXPOUT, module.EXPERR)
    if not ok:
        errors += 1
    print '---', ok, ':', os.path.basename(module.__file__)
          
def main():
    global modules, errors
    
    import build
    testmod(build)
    import cssencodings
    testmod(cssencodings)
    import customlog
    testmod(customlog)
    import parse
    testmod(parse)
    import selectors_tolower
    testmod(selectors_tolower)
    
    print 
    print 70*'-' 
    print 'Ran %i tests (%i errors).' % (modules, errors)  
    
    print 
    # doctests
    import website
    
if __name__ == '__main__':
    main()
