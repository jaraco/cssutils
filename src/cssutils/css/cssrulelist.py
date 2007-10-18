"""
CSSRuleList implements DOM Level 2 CSS CSSRuleList.

Partly also
    * http://dev.w3.org/csswg/cssom/#the-cssrulelist
"""
__all__ = ['CSSRuleList']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

class CSSRuleList(list):
    """
    The CSSRuleList object represents an (ordered) list of statements.

    The items in the CSSRuleList are accessible via an integral index,
    starting from 0.

    Subclasses a standard Python list so all standard list methods are
    available.

    Properties
    ==========
    length: of type unsigned long, readonly
        The number of CSSRules in the list. The range of valid child rule
        indices is 0 to length-1 inclusive.
    """
    def _getLength(self):
        return len(self)

    length = property(_getLength,
        doc="(DOM) The number of CSSRules in the list.")

    def item(self, index):
        """
        (DOM)
        Used to retrieve a CSS rule by ordinal index. The order in this
        collection represents the order of the rules in the CSS style
        sheet. If index is greater than or equal to the number of rules in
        the list, this returns None.

        Returns CSSRule, the style rule at the index position in the
        CSSRuleList, or None if that is not a valid index.
        """
        try:
            return self[index]
        except IndexError:
            return None
