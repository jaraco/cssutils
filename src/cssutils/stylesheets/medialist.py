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
__version__ = '0.9.2a2 $LastChangedRevision$'

import xml.dom

from cssutils.css import csscomment
import cssutils


class MediaList(cssutils.util.Base, list):
    """
    Provides the abstraction of an ordered collection of media,
    without defining or constraining how this collection is
    implemented.
    An empty list is the same as a list that contains the medium "all".

    Properties
    ==========
    length:
        The number of media in the list.
    mediaText: of type DOMString
        The parsable textual representation of this medialist
    seq: a list (cssutils)
        All parts of this MediaList including CSSComments
    valid:
        if this list is valid

    Format
    ======
    medium [ COMMA S* medium ]*
    """

    _MEDIA = [u'all', u'aural', u'braille', u'embossed', u'handheld',
        u'print', u'projection', u'screen', u'tty', u'tv']
    "available media types"

    def __init__(self, mediaText=None, readonly=False):
        """
        mediaText
            unicodestring of parsable comma separared media
        """
        super(MediaList, self).__init__()

        self.valid = True

        if mediaText:
            self._seq = []
            self.mediaText = mediaText
        else:
            self.seq = []
        self._readonly = readonly


    def _getLength(self):
        """
        returns count of media in this list which is not the same as
        len(MediaListInstance) which also contains CSSComments
        """
        return len(self)

    length = property(_getLength,
        doc="(DOM readonly) The number of media in the list.")


    def _getSeq(self):
        return self._seq

    def _setSeq(self, seq):
        self._seq = seq

    seq = property(_getSeq, _setSeq,
        doc="All parts of this MediaList including CSSComments")


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

        - SYNTAX_ERR: (self)
          Raised if the specified string value has a syntax error and is
          unparsable.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this media list is readonly.
        """
        self._checkReadonly()
        tokens = self._tokenize(mediaText)

        newseq = []
        del self[:] # reset
        expected = 'medium1'
        valid = True
        for i in range(len(tokens)):
            t = tokens[i]
            if self._ttypes.S == t.type: # ignore
                pass

            elif self._ttypes.COMMENT == t.type: # just add
                newseq.append(csscomment.CSSComment(t))

            elif expected.startswith('medium') and self._ttypes.IDENT == t.type:
                _newmed = t.value.lower()
                self.appendMedium(_newmed)
                newseq.append(_newmed)
                expected = 'comma'

            elif self._ttypes.IDENT == t.type:
                valid = False
                self._log.error(
                    u'MediaList: Syntax Error, expected ",".', t)

            elif 'comma' == expected and self._ttypes.COMMA == t.type:
                newseq.append(t.value)
                expected = 'medium'

            elif self._ttypes.COMMA == t.type:
                valid = False
                self._log.error(u'MediaList: Syntax Error, expected ",".', t)

            else:
                self._log.error(u'MediaList: Syntax Error in "%s".' %
                          self._valuestr(tokens), t)

        if 'medium' == expected:
            valid = False
            self._log.error(
                u'MediaList: Syntax Error, cannot end with ",".')
        self.seq = newseq
        self.valid = valid

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
        tokens = self._tokenize(newMedium)

        valid = True

        # ? should check format only?
        try:
            newMedium = tokens[0].value.lower()
        except (IndexError, AttributeError):
            self._log.error(
                u'MediaList: "%s" is not a valid medium.' % self._valuestr(
                    newMedium), error=xml.dom.InvalidCharacterErr)
            return

        if newMedium not in self._MEDIA:
            valid = False
            self._log.error(
                u'MediaList: "%s" is not a valid medium.' % newMedium,
                tokens[0], xml.dom.InvalidCharacterErr)

        # all contains every other (except handheld!)
        if u'all' in self and newMedium != u'handheld':
            return valid
        if newMedium == u'all':
            if u'handheld' in self:
                addhandheld2seq = True
            else:
                addhandheld2seq = False
            del self[:]
            self.append(u'all')
            self._seq = [u'all']
            if addhandheld2seq:
                #self.append(u'handheld')
                self._seq.append(u',')
                self._seq.append(u'handheld')
        else:
            if newMedium in self:
                self.remove(newMedium)

                # remove medium and possible ,!
                look4comma = False
                newseq = []
                for x in self._seq:
                    if newMedium == x:
                        look4comma = True
                        continue # remove
                    if u',' == x and look4comma:
                        look4comma = False
                        continue
                    else:
                        newseq.append(x)
                self._seq = newseq

            if len(self) > 0: # already 1 there, add "," + medium 2 seq
                self._seq.append(u',')

            self._seq.append(newMedium)
            self.append(newMedium)
        return valid


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
        try:
            self.remove(oldMedium)
            self._seq.remove(oldMedium)
        except ValueError:
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


if __name__ == '__main__':
    m = MediaList()
    m.mediaText = u'all; @x'
    print m.mediaText
