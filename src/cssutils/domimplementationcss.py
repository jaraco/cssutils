"""not used yet"""

__all__ = ['DOMImplementationCSS']
__docformat__ = 'restructuredtext'
__version__ = '0.9.1b4'

import css

class DOMImplementationCSS(object):
    """
    This interface allows the DOM user to create a CSSStyleSheet
    outside the context of a document. There is no way to associate
    the new CSSStyleSheet with a document in DOM Level 2.
    """
    _features = [
        ('css', '2.0'),
        ('stylesheets', '2.0')
        ]

    def hasFeature(self, feature, version):
        if version == "":
            version = None
        return (feature.lower(), version) in self._features


    def createCSSStyleSheet(title, media):
        """
        Creates a new CSSStyleSheet.

        title of type DOMString
            The advisory title. See also the Style Sheet Interfaces
            section.
        media of type DOMString
            The comma-separated list of media associated with the new style
            sheet. See also the Style Sheet Interfaces section.

        returns
            CSSStyleSheet: A new CSS style sheet.            

        TODO: DOMException 
            SYNTAX_ERR: Raised if the specified media string value has a
            syntax error and is unparsable.
        """
        return css.CSSStyleSheet(title=title, media=media)

    