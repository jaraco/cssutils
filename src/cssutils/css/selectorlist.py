"""SelectorList is a list of CSS Selector objects.

TODO
    - ??? CSS2 gives a special meaning to the comma (,) in selectors.
        However, since it is not known if the comma may acquire other
        meanings in future versions of CSS, the whole statement should be
        ignored if there is an error anywhere in the selector, even though
        the rest of the selector may look reasonable in CSS2.

        Illegal example(s):

        For example, since the "&" is not a valid token in a CSS2 selector,
        a CSS2 user agent must ignore the whole second line, and not set
        the color of H3 to red:
"""
__all__ = ['SelectorList']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssutils
from selector import Selector

class SelectorList(cssutils.util.Base, list):
    """
    (cssutils) a list of Selectors of a CSSStyleRule

    Properties
    ==========
    length: of type unsigned long, readonly
        The number of Selector elements in the list.
    selectorText: of type DOMString
        The textual representation of the selector for the rule set. The
        implementation may have stripped out insignificant whitespace while
        parsing the selector.
    seq:
        A list of interwoven Selector objects and u','
    """
    def __init__(self, selectorText=None, readonly=False):
        """
        initializes SelectorList with optional selectorText
        """
        super(SelectorList, self).__init__()

        self.seq = []
        if selectorText:
            self.selectorText = selectorText
        self._readonly = readonly

    def appendSelector(self, newSelector):
        """
        append a new Selector made from newSelector
        returns new Selector

        DOMException on setting

        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error
          and is unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this rule is readonly.
        """
        self._checkReadonly()
        tokens = self._tokenize(newSelector)
        newS = Selector(tokens)
        if not newS.selectorText:
            self._log.error(u'SelectorList: Not a valid selector: "%s".' %
                      self._valuestr(newSelector), error=xml.dom.SyntaxErr)
            return
        else:
            if len(self.seq) > 0:
                self.seq.append(u',')
            self.seq.append(newS)
            self.append(newS)

        return newS

    def _getLength(self):
        return len(self)

    length = property(_getLength,
        doc="The number of Selector elements in the list.")

    def _getSelectorText(self):
        """ returns serialized format """
        return cssutils.ser.do_css_SelectorList(self)

    def _setSelectorText(self, selectorText):
        """
        DOMException on setting

        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error
          and is unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this rule is readonly.
        """
        self._checkReadonly()
        tokens = self._tokenize(selectorText)
        if tokens:
            oldseq, self.seq = self.seq, [] # save and empty
            self.seq = []
            selectorparts = []
            found = None
            for i in range(len(tokens)):
                t = tokens[i]
                if self._ttypes.COMMA == t.type: # add new selector
                    found = 'comma'
                    try:
                        done = self.appendSelector(selectorparts)
                    except xml.dom.SyntaxErr, e:
                        self.seq = oldseq
                        self._log.error(e)
                        return
                    selectorparts = []
                else:
                    found = 'selectorpart'
                    selectorparts.append(t)

            if found == 'comma':
                self._log.error(u'SelectorList: Selectorlist ends with ",".')
                self.seq = oldseq
                return
            elif selectorparts: # add new selector
                try:
                    done = self.appendSelector(selectorparts)
                except xml.dom.SyntaxErr, e:
                    self.seq = oldseq
                    self._log.error(e)
                    return

        else:
            self._log.error(u'SelectorList: No selectors found.')

    selectorText = property(_getSelectorText, _setSelectorText,
        doc="""(cssutils) The textual representation of the selector for
            a rule set.""")


if __name__ == '__main__':
    cssutils.css.cssstylerule.Selector = Selector # for main test
    L = SelectorList()
    L.selectorText = 'a'
    print 1, L.selectorText
    try:
        L.selectorText = ','
    except Exception, e:
        print e
    print 2, L.selectorText
