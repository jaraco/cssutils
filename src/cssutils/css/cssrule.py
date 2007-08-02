"""CSSRule implements DOM Level 2 CSS CSSRule."""
__all__ = ['CSSRule']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2a1, $LastChangedRevision$'

import xml.dom

import cssutils


class CSSRule(cssutils.util.Base):
    """
    Abstract base interface for any type of CSS statement. This includes
    both rule sets and at-rules. An implementation is expected to preserve
    all rules specified in a CSS style sheet, even if the rule is not
    recognized by the parser. Unrecognized rules are represented using the
    CSSUnknownRule interface.

    Properties
    ==========
    cssText: of type DOMString
        The parsable textual representation of the rule. This reflects the
        current state of the rule and not its initial value.
    parentRule: of type CSSRule, readonly
        If this rule is contained inside another rule (e.g. a style rule
        inside an @media block), this is the containing rule. If this rule
        is not nested inside any other rules, this returns None.
    parentStyleSheet: of type CSSStyleSheet, readonly
        The style sheet that contains this rule.
    type: of type unsigned short, readonly
        The type of the rule, as defined above. The expectation is that
        binding-specific casting methods can be used to cast down from an
        instance of the CSSRule interface to the specific derived interface
        implied by the type.

    cssutils only
    -------------
    seq:
        contains sequence of parts of the rule including comments but
        excluding @KEYWORD and braces
    valid:
        if this rule is valid

    """

    """
    CSSRule type constants.
    An integer indicating which type of rule this is.
    """
    COMMENT = -1
    "cssutils only"
    UNKNOWN_RULE = 0
    STYLE_RULE = 1
    CHARSET_RULE = 2
    IMPORT_RULE = 3
    MEDIA_RULE = 4
    FONT_FACE_RULE = 5
    "Not in CSS 2.1 specification and not implemented"
    PAGE_RULE = 6
    NAMESPACE_RULE = 7
    "TODO: WD, may be different later"

    type = UNKNOWN_RULE
    """
    The type of this rule, as defined by a CSSRule type constant.
    Overwritten in derived classes.

    The expectation is that binding-specific casting methods can be used to
    cast down from an instance of the CSSRule interface to the specific
    derived interface implied by the type.
    (Casting not for this Python implementation I guess...)
    """

    def __init__(self, readonly=False):
        super(CSSRule, self).__init__()

        self.parentRule = None
        self.parentStyleSheet = None

        self.seq = []
        self.valid = True

        # must be set after initialization of #inheriting rule
        self._readonly = False


    def _getCssText(self):
        return u''

    def _setCssText(self, cssText):
        """
        DOMException on setting

        - SYNTAX_ERR:
          Raised if the specified CSS string value has a syntax error and
          is unparsable.
        - INVALID_MODIFICATION_ERR:
          Raised if the specified CSS string value represents a different
          type of rule than the current one.
        - HIERARCHY_REQUEST_ERR:
          Raised if the rule cannot be inserted at this point in the
          style sheet.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if the rule is readonly.
        """
        self._checkReadonly()

    cssText = property(fget=_getCssText, fset=_setCssText,
        doc="""(DOM) The parsable textual representation of the rule. This
        reflects the current state of the rule and not its initial value.
        The initial value is saved, but this may be removed in a future
        version!
        MUST BE OVERWRITTEN IN SUBCLASS TO WORK!""")
