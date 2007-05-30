"""
CSSValueList implements DOM Level 2 CSS ValueList.
"""
__all__ = ['CSSValueList']
__docformat__ = 'restructuredtext'
__version__ = '0.9a1'


class CSSValueList(list):
    """
    The CSSValueList interface provides the abstraction of an ordered
    collection of CSS values.

    Some properties allow an empty list into their syntax. In that case,
    these properties take the none identifier. So, an empty list means
    that the property has the value none.
    
    The items in the CSSValueList are accessible via an integral index, 
    starting from 0.
    """

    def _getLength(self):
        "same as len(ValueList)"
        return len(self)

    length = property(_getLength,
                doc="(DOM attribute) The number of CSSValues in the list.")

    def item(self, index):
        """
        (DOM method) Used to retrieve a CSSValue by ordinal index. The
        order in this collection represents the order of the values in the
        CSS style property. If index is greater than or equal to the number
        of values in the list, this returns None.
        """
        try:
            return self[index]
        except IndexError:
            return None

