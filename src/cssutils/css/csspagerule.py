"""CSSPageRule implements DOM Level 2 CSS CSSPageRule."""
__all__ = ['CSSPageRule']
__docformat__ = 'restructuredtext'
__version__ = '$Id$'

from cssstyledeclaration import CSSStyleDeclaration
import cssrule
import cssutils
import xml.dom

class CSSPageRule(cssrule.CSSRule):
    """
    The CSSPageRule interface represents a @page rule within a CSS style
    sheet. The @page rule is used to specify the dimensions, orientation,
    margins, etc. of a page box for paged media.

    Format::

        page
          PAGE_SYM S* IDENT? pseudo_page? S* 
            '{' S* declaration [ ';' S* declaration ]* '}' S*
          ;
        pseudo_page
          ':' [ "left" | "right" | "first" ]
          ;
    """
    def __init__(self, selectorText=None, style=None, parentRule=None, 
                 parentStyleSheet=None, readonly=False):
        """
        If readonly allows setting of properties in constructor only.

        :param selectorText:
            type string
        :param style:
            CSSStyleDeclaration for this CSSStyleRule
        """
        super(CSSPageRule, self).__init__(parentRule=parentRule, 
                                          parentStyleSheet=parentStyleSheet)
        self._atkeyword = u'@page'
        
        tempseq = self._tempSeq()

        if selectorText:
            self.selectorText = selectorText
            tempseq.append(self.selectorText, 'selectorText')
        else:
            self._selectorText = self._tempSeq()
        
        if style:
            self.style = style
        else:
            self.style = CSSStyleDeclaration()
        
        tempseq.append(self.style, 'style')

        self._setSeq(tempseq)        
        self._readonly = readonly

    def __repr__(self):
        return u"cssutils.css.%s(selectorText=%r, style=%r)" % (
                self.__class__.__name__, 
                self.selectorText, 
                self.style.cssText)

    def __str__(self):
        return u"<cssutils.css.%s object selectorText=%r style=%r at 0x%x>" % (
                self.__class__.__name__,
                self.selectorText, 
                self.style.cssText,
                id(self))

    def __parseSelectorText(self, selectorText):
        """
        Parse `selectorText` which may also be a list of tokens
        and returns (selectorText, seq).

        see _setSelectorText for details
        """
        # for closures: must be a mutable
        new = {'wellformed': True, 'last-S': False}

        def _char(expected, seq, token, tokenizer=None):
            # pseudo_page, :left, :right or :first
            val = self._tokenvalue(token)
            if not new['last-S'] and expected in ['page', ': or EOF']\
               and u':' == val:
                try:
                    identtoken = tokenizer.next()
                except StopIteration:
                    self._log.error(
                        u'CSSPageRule selectorText: No IDENT found.', token)
                else:
                    ival, ityp = self._tokenvalue(identtoken),\
                                 self._type(identtoken)
                    if self._prods.IDENT != ityp:
                        self._log.error(u'CSSPageRule selectorText: Expected '
                                        u'IDENT but found: %r' % ival, token)
                    else:
                        seq.append(val + ival, 'pseudo')
                        
                        if not ival in (u'first', u'left', u'right'):
                            self._log.warn(u'CSSPageRule: Unknown @page '
                                           u'selector: %r' 
                                           % (u':'+ival,), neverraise=True)

                        return 'EOF'
                return expected
            else:
                new['wellformed'] = False
                self._log.error(u'CSSPageRule selectorText: Unexpected CHAR: %r'
                                % val, token)
                return expected

        def S(expected, seq, token, tokenizer=None):
            "Does not raise if EOF is found."
            if expected == ': or EOF':
                # pseudo must directly follow IDENT if given
                new['last-S'] = True
            return expected

        def IDENT(expected, seq, token, tokenizer=None):
            ""
            val = self._tokenvalue(token)
            if 'page' == expected:
                seq.append(val, 'IDENT')
                return ': or EOF'
            else:
                new['wellformed'] = False
                self._log.error(u'CSSPageRule selectorText: Unexpected IDENT: '
                                u'%r' % val, token)
                return expected

        def COMMENT(expected, seq, token, tokenizer=None):
            "Does not raise if EOF is found."
            seq.append(cssutils.css.CSSComment([token]), 'COMMENT')
            return expected 

        newseq = self._tempSeq()
        wellformed, expected = self._parse(expected='page',
            seq=newseq, tokenizer=self._tokenize2(selectorText),
            productions={'CHAR': _char,
                         'IDENT': IDENT,
                         'COMMENT': COMMENT, 
                         'S': S}, 
            new=new)
        wellformed = wellformed and new['wellformed']
        
        # post conditions
        if expected == 'ident':
            self._log.error(
                u'CSSPageRule selectorText: No valid selector: %r' %
                    self._valuestr(selectorText))
            
        return wellformed, newseq

    def _getCssText(self):
        """Return serialized property cssText."""
        return cssutils.ser.do_CSSPageRule(self)

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
        super(CSSPageRule, self)._setCssText(cssText)
        
        tokenizer = self._tokenize2(cssText)
        if self._type(self._nexttoken(tokenizer)) != self._prods.PAGE_SYM:
            self._log.error(u'CSSPageRule: No CSSPageRule found: %s' %
                            self._valuestr(cssText), 
                            error=xml.dom.InvalidModificationErr)
        else:
            newStyle = CSSStyleDeclaration(parentRule=self)
            ok = True
            
            selectortokens, startbrace = self._tokensupto2(tokenizer, 
                                                           blockstartonly=True,
                                                           separateEnd=True)
            styletokens, braceorEOFtoken = self._tokensupto2(tokenizer, 
                                                        blockendonly=True,
                                                        separateEnd=True)
            nonetoken = self._nexttoken(tokenizer)
            if self._tokenvalue(startbrace) != u'{':
                ok = False
                self._log.error(
                    u'CSSPageRule: No start { of style declaration found: %r' %
                    self._valuestr(cssText), startbrace)
            elif nonetoken:
                ok = False
                self._log.error(
                    u'CSSPageRule: Trailing content found.', token=nonetoken)
                
            selok, newselectorseq = self.__parseSelectorText(selectortokens)
            ok = ok and selok

            val, type_ = self._tokenvalue(braceorEOFtoken),\
                       self._type(braceorEOFtoken)
            if val != u'}' and type_ != 'EOF':
                ok = False
                self._log.error(
                    u'CSSPageRule: No "}" after style declaration found: %r' %
                    self._valuestr(cssText))
            else:
                if 'EOF' == type_:
                    # add again as style needs it
                    styletokens.append(braceorEOFtoken)
                # SET, may raise:
                newStyle.cssText = styletokens

            if ok:
                self._selectorText = newselectorseq
                self.style = newStyle 
                
    cssText = property(_getCssText, _setCssText,
        doc=u"(DOM) The parsable textual representation of this rule.")

    def _getSelectorText(self):
        """Wrapper for cssutils Selector object."""
        return cssutils.ser.do_CSSPageRuleSelector(self._selectorText)

    def _setSelectorText(self, selectorText):
        """Wrapper for cssutils Selector object.

        :param selectorText: 
            DOM String, in CSS 2.1 one of
            
            - :first
            - :left
            - :right
            - empty

        :exceptions:
            - :exc:`~xml.dom.SyntaxErr`:
              Raised if the specified CSS string value has a syntax error
              and is unparsable.
            - :exc:`~xml.dom.NoModificationAllowedErr`:
              Raised if this rule is readonly.
        """
        self._checkReadonly()

        # may raise SYNTAX_ERR
        wellformed, newseq = self.__parseSelectorText(selectorText)
        if wellformed:
            self._selectorText = newseq

    selectorText = property(_getSelectorText, _setSelectorText,
                            doc=u"(DOM) The parsable textual representation of "
                                u"the page selector for the rule.")

    def _setStyle(self, style):
        """
        :param style:
            a CSSStyleDeclaration or string
        """
        self._checkReadonly()
        if isinstance(style, basestring):
            self._style = CSSStyleDeclaration(cssText=style, parentRule=self)
        else:
            style._parentRule = self
            self._style = style
            
    style = property(lambda self: self._style, _setStyle,
                     doc=u"(DOM) The declaration-block of this rule set, "
                         u"a :class:`~cssutils.css.CSSStyleDeclaration`.")

    type = property(lambda self: self.PAGE_RULE, 
                    doc=u"The type of this rule, as defined by a CSSRule "
                        u"type constant.")
    
    # constant but needed:
    wellformed = property(lambda self: True)
