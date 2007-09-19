"""
MediaList implements DOM Level 2 Style Sheets MediaList.

TODO:
    delete: maybe if deleting from all, replace *all* with all others?
    is unknown media an exception?
"""
__all__ = ['MediaList']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom
import cssutils
from cssutils.css import csscomment
from mediaquery import MediaQuery

class MediaList(cssutils.util.Base, list):
    """
    Provides the abstraction of an ordered collection of media,
    without defining or constraining how this collection is
    implemented.

    A media is always an instance of MediaQuery.

    An empty list is the same as a list that contains the medium "all".

    Properties
    ==========
    length:
        The number of media in the list.
    mediaText: of type DOMString
        The parsable textual representation of this medialist
    self: a list (cssutils)
        All MediaQueries in this MediaList
    valid:
        if this list is valid

    Format
    ======
    ::

        medium [ COMMA S* medium ]*

    New::

        <media_query> [, <media_query> ]*
    """
    def __init__(self, mediaText=None, readonly=False):
        """
        mediaText
            unicodestring of parsable comma separared media
            or a list of media
        """
        super(MediaList, self).__init__()

        self.valid = True
        #self.seq = []

        if isinstance(mediaText, list):
            mediaText = u','.join(mediaText)

        if mediaText:
            self.mediaText = mediaText

        self._readonly = readonly

    def _getLength(self):
        """
        returns count of media in this list which is not the same as
        len(MediaListInstance) which also contains CSSComments
        """
        return len(self)

    length = property(_getLength,
        doc="(DOM readonly) The number of media in the list.")

    def _getMediaText(self):
        """
        returns serialized property mediaText
        """
        return cssutils.ser.do_stylesheets_medialist(self)

    def _setMediaText(self, mediaText):
        """
        mediaText
            simple value or comma-separated list of media

        DOMException

        - SYNTAX_ERR: (MediaQuery)
          Raised if the specified string value has a syntax error and is
          unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this media list is readonly.
        """
        self._checkReadonly()
        tokenizer = self._tokenize2(mediaText)

        newseq = []
        while True:
            # find all upto but excluding next ","
            mqtokens = self._tokensupto2(
                tokenizer, listseponly=True, keepEnd=False)
            if mqtokens:
                newseq.append(MediaQuery(mqtokens))
            else:
                break

        del self[:]
        for mq in newseq:
            self.append(mq)

    mediaText = property(_getMediaText, _setMediaText,
        doc="""(DOM) The parsable textual representation of the media list.
            This is a comma-separated list of media.""")

    def appendMedium(self, newMedium):
        """
        (DOM)
        Adds the medium newMedium to the end of the list. If the newMedium
        is already used, it is first removed.

        returns if newMedium is valid

        DOMException

        - INVALID_CHARACTER_ERR: (self)
          If the medium contains characters that are invalid in the
          underlying style language.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this list is readonly.
        """
        self._checkReadonly()

        newmq = MediaQuery(newMedium)
        if not newmq.valid:
            return False

        mts = [mq.mediaType for mq in self]
        newmt = newmq.mediaType

        if newmt in mts:
            self.deleteMedium(newmt)
            self.append(newmq)
        elif u'all' == newmt:
            # remove all except handheld (Opera)
            h = None
            for mq in self:
                if mq.mediaType == u'handheld':
                    h = mq
            del self[:]
            self.append(newmq)
            if h:
                self.append(h)
        elif u'all' in mts:
            if u'handheld' == newmt:
                self.append(newmq)
        else:
            self.append(newmq)

        return True


    def deleteMedium(self, oldMedium):
        """
        (DOM)
        Deletes the medium indicated by oldMedium from the list.

        DOMException

        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this list is readonly.
        - NOT_FOUND_ERR: (self)
          Raised if oldMedium is not in the list.
        """
        self._checkReadonly()
        oldMedium = oldMedium.lower()

        for i, mq in enumerate(self):
            if mq.mediaType == oldMedium:
                del self[i]
                break
        else:
            raise xml.dom.NotFoundErr(
                u'"%s" not in this MediaList' % oldMedium)

    def item(self, index):
        """
        (DOM)
        Returns the index'th element in the list. If index is greater than
        or equal to the number of media in the list, this returns None.
        """
        try:
            return self[index]
        except IndexError:
            return None

    def __repr__(self):
        return "cssutils.stylesheets.%s(mediaText=%r)" % (
                self.__class__.__name__, self.mediaText)

    def __str__(self):
        return "<cssutils.stylesheets.%s object mediaText=%r at 0x%x>" % (
                self.__class__.__name__, self.mediaText, id(self))


if __name__ == '__main__':
    m = MediaList()
    m.mediaText = u'all; @x'
    print m.mediaText
