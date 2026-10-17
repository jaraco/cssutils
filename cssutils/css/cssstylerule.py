"""CSSStyleRule implements DOM Level 2 CSS CSSStyleRule."""

__all__ = ['CSSStyleRule']

import xml.dom

import cssutils

from . import cssrule
from .cssstyledeclaration import CSSStyleDeclaration
from .selectorlist import SelectorList


class CSSStyleRule(cssrule.CSSRule):
    """The CSSStyleRule object represents a ruleset specified (if any) in a CSS
    style sheet. It provides access to a declaration block as well as to the
    associated group of selectors.

    Format::

        : selector [ COMMA S* selector ]*
        LBRACE S* declaration [ ';' S* declaration ]* '}' S*
        ;
    """

    def __init__(
        self,
        selectorText=None,
        style=None,
        parentRule=None,
        parentStyleSheet=None,
        readonly=False,
    ):
        """
        :Parameters:
            selectorText
                string parsed into selectorList
            style
                string parsed into CSSStyleDeclaration for this CSSStyleRule
            readonly
                if True allows setting of properties in constructor only
        """
        super().__init__(parentRule=parentRule, parentStyleSheet=parentStyleSheet)

        self.selectorList = SelectorList()
        if selectorText:
            self.selectorText = selectorText

        if style:
            self.style = style
        else:
            self.style = CSSStyleDeclaration()

        self._readonly = readonly

    def __repr__(self):
        if self._namespaces:
            st = (self.selectorText, self._namespaces)
        else:
            st = self.selectorText
        return f"cssutils.css.{self.__class__.__name__}(selectorText={st!r}, style={self.style.cssText!r})"

    def __str__(self):
        return (
            f"<cssutils.css.{self.__class__.__name__} object selectorText={self.selectorText!r} style={self.style.cssText!r} _namespaces={self._namespaces!r} "
            f"at 0x{id(self):x}>"
        )

    def _getCssText(self):
        """Return serialized property cssText."""
        return cssutils.ser.do_CSSStyleRule(self)

    def _setCssText(self, cssText):  # noqa: C901
        """
        :param cssText:
            a parseable string or a tuple of (cssText, dict-of-namespaces)
        :exceptions:
            - :exc:`~xml.dom.NamespaceErr`:
              Raised if the specified selector uses an unknown namespace
              prefix.
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
        super()._setCssText(cssText)

        # might be (cssText, namespaces)
        cssText, namespaces = self._splitNamespacesOff(cssText)
        try:
            # use parent style sheet ones if available
            namespaces = self.parentStyleSheet.namespaces
        except AttributeError:
            pass

        tokenizer = self._tokenize2(cssText)
        selectortokens = self._tokensupto2(tokenizer, blockstartonly=True)
        styletokens = self._tokensupto2(tokenizer, blockendonly=True)
        trail = self._nexttoken(tokenizer)
        if trail:
            self._log.error(
                f'CSSStyleRule: Trailing content: {self._valuestr(cssText)}',
                token=trail,
            )
        elif not selectortokens:
            self._log.error(
                f'CSSStyleRule: No selector found: {self._valuestr(cssText)!r}'
            )
        elif self._tokenvalue(selectortokens[0]).startswith('@'):
            self._log.error(
                f'CSSStyleRule: No style rule: {self._valuestr(cssText)!r}',
                error=xml.dom.InvalidModificationErr,
            )
        else:
            newSelectorList = SelectorList(parentRule=self)
            newStyle = CSSStyleDeclaration(parentRule=self)
            ok = True

            bracetoken = selectortokens.pop()
            if self._tokenvalue(bracetoken) != '{':
                ok = False
                self._log.error(
                    f'CSSStyleRule: No start {{ of style declaration found: {self._valuestr(cssText)!r}',
                    bracetoken,
                )
            elif not selectortokens:
                ok = False
                self._log.error(
                    f'CSSStyleRule: No selector found: {self._valuestr(cssText)!r}.',
                    bracetoken,
                )
            # SET
            newSelectorList.selectorText = (selectortokens, namespaces)

            if not styletokens:
                ok = False
                self._log.error(
                    f'CSSStyleRule: No style declaration or "}}" found: {self._valuestr(cssText)!r}'
                )
            else:
                braceorEOFtoken = styletokens.pop()
                val, typ = (
                    self._tokenvalue(braceorEOFtoken),
                    self._type(braceorEOFtoken),
                )
                if val != '}' and typ != 'EOF':
                    ok = False
                    self._log.error(
                        'CSSStyleRule: No "}" after style '
                        f'declaration found: {self._valuestr(cssText)!r}'
                    )
                else:
                    if 'EOF' == typ:
                        # add again as style needs it
                        styletokens.append(braceorEOFtoken)
                    # SET, may raise:
                    newStyle.cssText = styletokens

            if ok:
                self.selectorList = newSelectorList
                self.style = newStyle

    cssText = property(
        _getCssText,
        _setCssText,
        doc="(DOM) The parsable textual representation of this rule.",
    )

    def __getNamespaces(self):
        """Uses children namespaces if not attached to a sheet, else the sheet's
        ones."""
        try:
            return self.parentStyleSheet.namespaces
        except AttributeError:
            return self.selectorList._namespaces

    _namespaces = property(
        __getNamespaces,
        doc="If this Rule is attached to a CSSStyleSheet "
        "the namespaces of that sheet are mirrored "
        "here. While the Rule is not attached the "
        "namespaces of selectorList are used."
        "",
    )

    def _setSelectorList(self, selectorList):
        """
        :param selectorList: A SelectorList which replaces the current
            selectorList object
        """
        self._checkReadonly()
        selectorList._parentRule = self
        self._selectorList = selectorList

    _selectorList = None
    selectorList = property(
        lambda self: self._selectorList,
        _setSelectorList,
        doc="The SelectorList of this rule.",
    )

    def _setSelectorText(self, selectorText):
        """
        wrapper for cssutils SelectorList object

        :param selectorText:
            of type string, might also be a comma separated list
            of selectors
        :exceptions:
            - :exc:`~xml.dom.NamespaceErr`:
              Raised if the specified selector uses an unknown namespace
              prefix.
            - :exc:`~xml.dom.SyntaxErr`:
              Raised if the specified CSS string value has a syntax error
              and is unparsable.
            - :exc:`~xml.dom.NoModificationAllowedErr`:
              Raised if this rule is readonly.
        """
        self._checkReadonly()

        sl = SelectorList(selectorText=selectorText, parentRule=self)
        if sl.wellformed:
            self._selectorList = sl

    selectorText = property(
        lambda self: self._selectorList.selectorText,
        _setSelectorText,
        doc="(DOM) The textual representation of the selector for the rule set.",
    )

    def _setStyle(self, style):
        """
        :param style: A string or CSSStyleDeclaration which replaces the
            current style object.
        """
        self._checkReadonly()
        if isinstance(style, str):
            self._style = CSSStyleDeclaration(cssText=style, parentRule=self)
        else:
            style._parentRule = self
            self._style = style

    style = property(
        lambda self: self._style,
        _setStyle,
        doc="(DOM) The declaration-block of this rule set.",
    )

    type = property(
        lambda self: self.STYLE_RULE,
        doc="The type of this rule, as defined by a CSSRule type constant.",
    )

    wellformed = property(lambda self: self.selectorList.wellformed)

    def _getValid(self):
        """Return whether the style declaration is valid."""
        return self.style.valid

    valid = property(_getValid, doc='``True`` when the style declaration is true.')
