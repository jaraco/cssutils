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
        The number of MediaQuery objects in the list.
    mediaText: of type DOMString
        The parsable textual representation of this MediaList
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
        valid = True
        tokenizer = self._tokenize2(mediaText)
        newseq = []

        expected = None
        while True:
            # find all upto and including next ",", EOF or nothing
            mqtokens = self._tokensupto2(tokenizer, listseponly=True)
            if mqtokens:
                if self._tokenvalue(mqtokens[-1]) == ',':
                    expected = mqtokens.pop()
                else:
                    expected = None

                mq = MediaQuery(mqtokens)
                if mq.valid:
                    newseq.append(mq)
                else:
                    valid = False
                    self._log.error(u'MediaList: Invalid MediaQuery: %s' %
                                    self._valuestr(tokens))
            else:
                break

        # post condition
        if expected:
            valid = False
            self._log.error(u'MediaList: Cannot end with ",".')

        if valid:
            del self[:]
            for mq in newseq:
                self.appendMedium(mq)

    mediaText = property(_getMediaText, _setMediaText,
        doc="""(DOM) The parsable textual representation of the media list.
            This is a comma-separated list of media.""")

    def appendMedium(self, newMedium):
        """
        (DOM)
        Adds the medium newMedium to the end of the list. If the newMedium
        is already used, it is first removed.

        newMedium
            a string or a MediaQuery object

        returns if newMedium is valid

        DOMException

        - INVALID_CHARACTER_ERR: (self)
          If the medium contains characters that are invalid in the
          underlying style language.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this list is readonly.
        """
        self._checkReadonly()

        if not isinstance(newMedium, MediaQuery):
            newMedium = MediaQuery(newMedium)

        if newMedium.valid:

            mts = [self._normalize(mq.mediaType) for mq in self]
            newmt = self._normalize(newMedium.mediaType)

            if newmt in mts:
                self.deleteMedium(newmt)
                self.append(newMedium)
            elif u'all' == newmt:
                # remove all except handheld (Opera)
                h = None
                for mq in self:
                    if mq.mediaType == u'handheld':
                        h = mq
                del self[:]
                self.append(newMedium)
                if h:
                    self.append(h)
            elif u'all' in mts:
                if u'handheld' == newmt:
                    self.append(newMedium)
            else:
                self.append(newMedium)

            return True

        else:
            return False

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
        oldMedium = self._normalize(oldMedium)

        for i, mq in enumerate(self):
            if self._normalize(mq.mediaType) == oldMedium:
                del self[i]
                break
        else:
            raise xml.dom.NotFoundErr(
                u'"%s" not in this MediaList' % oldMedium)

    def item(self, index):
        """
        (DOM)
        Returns the mediaType of the index'th element in the list.
        If index is greater than or equal to the number of media in the
        list, returns None.
        """
        try:
            return self[index].mediaType
        except IndexError:
            return None

    def __repr__(self):
        return "cssutils.stylesheets.%s(mediaText=%r)" % (
                self.__class__.__name__, self.mediaText)

    def __str__(self):
        return "<cssutils.stylesheets.%s object mediaText=%r at 0x%x>" % (
                self.__class__.__name__, self.mediaText, id(self))
