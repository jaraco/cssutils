"""MarginRule implements DOM Level 2 CSS MarginRule."""
__all__ = ['MarginRule']
__docformat__ = 'restructuredtext'
__version__ = '$Id$'

from cssutils.prodparser import *
from cssstyledeclaration import CSSStyleDeclaration
import cssrule
import cssutils
import xml.dom

class MarginRule(cssrule.CSSRule):
    """
    A margin at-rule consists of an ATKEYWORD that identifies the margin box
    (e.g. '@top-left') and a block of declarations (said to be in the margin
    context).

    Format::

        @top-left {
            content: "Hamlet";
            }
    """
    _keywords = ['@top-left-corner',
                 '@top-left',
                 '@top-right'
                 # ...
                 ]
    
    def __init__(self, cssText=u'', style=None, parentRule=None, 
                 parentStyleSheet=None, readonly=False):
        """
        :param cssText:
            of type string
        :param style:
            CSSStyleDeclaration for this CSSStyleRule
        """
        super(MarginRule, self).__init__(parentRule=parentRule, 
                                         parentStyleSheet=parentStyleSheet)
        self._atkeyword = None
            
        if cssText:
            self.cssText = cssText
        else:
            if style:
                self.style = style
            else:
                self.style = CSSStyleDeclaration(parentRule=self)
            
        self._readonly = readonly

    def _setAtkeyword(self, keyword):
        """Check if new keyword fits the rule it is used for."""
        atkeyword = self._normalize(keyword)
        if not self.atkeyword or (self.atkeyword == atkeyword) and (
           atkeyword in MarginRule._keywords):
            self._atkeyword = atkeyword
            self._keyword = keyword
        else:
            self._log.error(u'%s: Invalid atkeyword for this rule: %r' %
                            (self.atkeyword, keyword),
                            error=xml.dom.InvalidModificationErr)

    atkeyword = property(lambda self: self._atkeyword, _setAtkeyword,
                         doc=u"Normalized  keyword of an @rule (e.g. ``@import``).")

    def __repr__(self):
        return u"cssutils.css.%s(style=%r)" % (self.__class__.__name__, 
                                               self.style.cssText)

    def __str__(self):
        return u"<cssutils.css.%s object keyword=%r style=%r "\
               u"at 0x%x>" % (self.__class__.__name__,
                              self.keyword,
                              self.style.cssText,
                              id(self))

    def _getCssText(self):
        """Return serialized property cssText."""
        return cssutils.ser.do_MarginRule(self)

    def _setCssText(self, cssText):
        """
        :exceptions:
            - :exc:`~xml.dom.SyntaxErr`:
              Raised if the specified CSS string value has a syntax error and
              is unparsable.
            - :exc:`~xml.dom.InvalidModificationErr`:
              Raised if the specified CSS string value represents a different
              type of rule than the current one.
            - :exc:`~xml.dom.HierarchyRequestErr`:
              Raised if the rule cannot be inserted at this point in the
              style sheet.
            - :exc:`~xml.dom.NoModificationAllowedErr`:
              Raised if the rule is readonly.
        """
        super(MarginRule, self)._setCssText(cssText)
        
        prods = Sequence(Prod(name='@', 
                              match=lambda t, v: t == 'ATKEYWORD',
                              toStore='@' 
                              ),
                         PreDef.char('OPEN', u'{'),
                         Sequence(Prod(name='style', 
                                       match=lambda t, v: v != u'}',
                                       toStore='tokens',
                                       storeToken=True # TODO: resolve later
                                       ),
                                  minmax=lambda: (0, None)
                         ),
                         PreDef.char('CLOSE', u'}', stopAndKeep=True)
                )
        # parse
        ok, seq, store, unused = ProdParser().parse(cssText,
                                                    u'MarginRule',
                                                    prods)
        
#        if self._normalize(store['@'].value) not in MarginRule._keywords:
#            ok = False
#            self._log.error(u'MarginRule: Unexpected @keyword %r'
#                            % store['@'].value)
        
#        else:

        newStyle = CSSStyleDeclaration(parentRule=self)
        # SET, may raise:
        newStyle.cssText = store['tokens']
        
        if ok:
            # may raise:
            self.atkeyword = store['@'].value
            
            self.style = newStyle
                
    cssText = property(fget=_getCssText, fset=_setCssText,
                       doc=u"(DOM) The parsable textual representation.")
    
    def _setStyle(self, style):
        """
        :param style: A string or CSSStyleDeclaration which replaces the
            current style object.
        """
        self._checkReadonly()
        if isinstance(style, basestring):
            self._style = CSSStyleDeclaration(cssText=style, parentRule=self)
        else:
            style._parentRule = self
            self._style = style

    style = property(lambda self: self._style, _setStyle,
                     doc=u"(DOM) The declaration-block of this rule set.")
    
    type = property(lambda self: self.MARGIN_RULE, 
                    doc=u"The type of this rule, as defined by a CSSRule "
                        u"type constant.")
    
    wellformed = property(lambda self: bool(self.atkeyword))
    