#!/usr/bin/env python

"""
Python codec for CSS.
"""

__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-09-01 15:55:42 +0200 (Sa, 01 Sep 2007) $'
__version__ = '$LastChangedRevision: 300 $'

import codecs


# We're using bits to store all possible candidate encodings (or variants, i.e.
# we have two bits for the variants of UTF-16 and two for the
# variants of UTF-32).
#
# Prefixes for various CSS encodings
# UTF-8-SIG   xEF  xBB  xBF
# UTF-16 (LE) xFF  xFE ~x00|~x00
# UTF-16 (BE) xFE  xFF
# UTF-16-LE    @   x00   @   x00
# UTF-16-BE   x00   @
# UTF-32 (LE) xFF  xFE  x00  x00
# UTF-32 (BE) x00  x00  xFE  xFF
# UTF-32-LE    @   x00  x00  x00
# UTF-32-BE   x00  x00  x00   @
# CHARSET      @    c    h    a  ...



def _detectencoding_str(input, final=False):
    CANDIDATE_UTF_8_SIG    =   1
    CANDIDATE_UTF_16_AS_LE =   2
    CANDIDATE_UTF_16_AS_BE =   4
    CANDIDATE_UTF_16_LE    =   8
    CANDIDATE_UTF_16_BE    =  16
    CANDIDATE_UTF_32_AS_LE =  32
    CANDIDATE_UTF_32_AS_BE =  64
    CANDIDATE_UTF_32_LE    = 128
    CANDIDATE_UTF_32_BE    = 256
    CANDIDATE_CHARSET      = 512
    candidates = 1023

    li = len(input)
    if li>=1:
        # Check first byte
        c = input[0]
        if c != "\xef":
            candidates &= ~CANDIDATE_UTF_8_SIG
        if c != "\xff":
            candidates &= ~(CANDIDATE_UTF_32_AS_LE|CANDIDATE_UTF_16_AS_LE)
        if c != "\xfe":
            candidates &= ~CANDIDATE_UTF_16_AS_BE
        if c != "@":
            candidates &= ~(CANDIDATE_UTF_32_LE|CANDIDATE_UTF_16_LE|CANDIDATE_CHARSET)
        if c != "\x00":
            candidates &= ~(CANDIDATE_UTF_32_AS_BE|CANDIDATE_UTF_32_BE|CANDIDATE_UTF_16_BE)
        if li>=2:
            # Check second byte
            c = input[1]
            if c != "\xbb":
                candidates &= ~CANDIDATE_UTF_8_SIG
            if c != "\xfe":
                candidates &= ~(CANDIDATE_UTF_16_AS_LE|CANDIDATE_UTF_32_AS_LE)
            if c != "\xff":
                candidates &= ~CANDIDATE_UTF_16_AS_BE
            if c != "\x00":
                candidates &= ~(CANDIDATE_UTF_16_LE|CANDIDATE_UTF_32_AS_BE|CANDIDATE_UTF_32_LE|CANDIDATE_UTF_32_BE)
            if c != "@":
                candidates &= ~CANDIDATE_UTF_16_BE
            if c != "c":
                candidates &= ~CANDIDATE_CHARSET
            if li>=3:
                # Check third byte
                c = input[2]
                if c != "\xbf":
                    candidates &= ~CANDIDATE_UTF_8_SIG
                if c != "c":
                    candidates &= ~CANDIDATE_UTF_16_LE
                if c != "\x00":
                    candidates &= ~(CANDIDATE_UTF_32_AS_LE|CANDIDATE_UTF_32_LE|CANDIDATE_UTF_32_BE)
                if c != "\xfe":
                    candidates &= ~CANDIDATE_UTF_32_AS_BE
                if c != "h":
                    candidates &= ~CANDIDATE_CHARSET
                if li>=4:
                    # Check fourth byte
                    c = input[3]
                    if input[2:4] == "\x00\x00":
                        candidates &= ~CANDIDATE_UTF_16_AS_LE
                    if c != "\x00":
                        candidates &= ~(CANDIDATE_UTF_16_LE|CANDIDATE_UTF_32_AS_LE|CANDIDATE_UTF_32_LE)
                    if c != "\xff":
                        candidates &= ~CANDIDATE_UTF_32_AS_BE
                    if c != "@":
                        candidates &= ~CANDIDATE_UTF_32_BE
                    if c != "a":
                        candidates &= ~CANDIDATE_CHARSET
    if candidates == 0:
        return "utf-8"
    if not (candidates & (candidates-1)): # only one candidate remaining
        if candidates == CANDIDATE_UTF_8_SIG and li >= 3:
            return "utf-8-sig"
        elif candidates == CANDIDATE_UTF_16_AS_LE and li >= 2:
            return "utf-16"
        elif candidates == CANDIDATE_UTF_16_AS_BE and li >= 2:
            return "utf-16"
        elif candidates == CANDIDATE_UTF_16_LE and li >= 4:
            return "utf-16-le"
        elif candidates == CANDIDATE_UTF_16_BE and li >= 2:
            return "utf-16-be"
        elif candidates == CANDIDATE_UTF_32_AS_LE and li >= 4:
            return "utf-32"
        elif candidates == CANDIDATE_UTF_32_AS_BE and li >= 4:
            return "utf-32"
        elif candidates == CANDIDATE_UTF_32_LE and li >= 4:
            return "utf-32-le"
        elif candidates == CANDIDATE_UTF_32_BE and li >= 4:
            return "utf-32-be"
        elif candidates == CANDIDATE_CHARSET and li >= 4:
            prefix = '@charset "'
            if input.startswith(prefix):
                pos = input.find('"', len(prefix))
                if pos >= 0:
                    return input[len(prefix):pos]
    # if this is the last call, and we haven't determined an encoding yet,
    # we default to UTF-8
    if final:
        return "utf-8"
    return None # dont' know yet


def _detectencoding_unicode(input, final=False):
    prefix = u'@charset "'
    if input.startswith(prefix):
        pos = input.find(u'"', len(prefix))
        if pos >= 0:
            return input[len(prefix):pos]
    # if this is the last call, and we haven't determined an encoding yet,
    # we default to UTF-8
    if final:
        return "utf-8"
    return None # dont' know yet


def _fixencoding(input, encoding, final=False):
    prefix = u'@charset "'
    if len(input) > len(prefix):
        if input.startswith(prefix):
            pos = input.find(u'"', len(prefix))
            if pos >= 0:
                if encoding.replace("_", "-").lower() == "utf-8-sig":
                    encoding = u"utf-8"
                return prefix + encoding + input[pos:]
            # we haven't seen the end of the encoding name yet => fall through
        else:
            return input # doesn't start with prefix, so nothing to fix
    elif not prefix.startswith(input) or final:
        # can't turn out to be a @charset rule later (or there is no "later")
        return input
    if final:
        return input
    return None # don't know yet


def decode(input, errors="strict", encoding=None):
    if encoding is None:
        encoding = _detectencoding_str(input, True)
    if encoding == "css":
        raise ValueError("css not allowed as encoding name")
    (input, consumed) = codecs.getdecoder(encoding)(input, errors)
    return (_fixencoding(input, unicode(encoding), True), consumed)


def encode(input, errors="strict", encoding=None):
    consumed = len(input)
    if encoding is None:
        encoding = _detectencoding_unicode(input, True)
        if encoding.replace("_", "-").lower() == "utf-8-sig":
            input = _fixencoding(input, u"utf-8", True)
    else:
        input = _fixencoding(input, unicode(encoding), True)
    if encoding == "css":
        raise ValueError("css not allowed as encoding name")
    info = codecs.lookup(encoding)
    return (info.encode(input, errors)[0], consumed)


class IncrementalDecoder(codecs.IncrementalDecoder):
    def __init__(self, errors="strict", encoding=None):
        self.decoder = None
        self.encoding = encoding
        codecs.IncrementalDecoder.__init__(self, errors)
        # Store ``errors`` somewhere else,
        # because we have to hide it in a property
        self._errors = errors
        self.buffer = ""
        self.headerfixed = False

    def iterdecode(self, input):
        for part in input:
            result = self.decode(part, False)
            if result:
                yield result
        result = self.decode("", True)
        if result:
            yield result

    def decode(self, input, final=False):
        # We're doing basically the same as a ``BufferedIncrementalDecoder``,
        # but since the buffer is only relevant until the encoding has been
        # detected (in which case the buffer of the underlying codec might
        # kick in), we're implementing buffering ourselves to avoid some
        # overhead.
        if self.decoder is None:
            input = self.buffer + input
            self.encoding = _detectencoding_str(input, final)
            if self.encoding is None:
                self.buffer = input # retry the complete input on the next call
                return u"" # no encoding determined yet, so no output
            if self.encoding == "css":
                raise ValueError("css not allowed as encoding name")
            self.buffer = "" # drop buffer, as the decoder might keep its own
            decoder = codecs.getincrementaldecoder(self.encoding)
            self.decoder = decoder(self._errors)
        if self.headerfixed:
            return self.decoder.decode(input, final)
        # If we haven't fixed the header yet,
        # the content of ``self.buffer`` is a ``unicode`` object
        output = self.buffer + self.decoder.decode(input, final)
        newoutput = _fixencoding(output, unicode(self.encoding), final)
        if newoutput is None:
            # retry fixing the @charset rule (but keep the decoded stuff)
            self.buffer = output
            return u""
        self.headerfixed = True
        return newoutput

    def reset(self):
        codecs.IncrementalDecoder.reset(self)
        self.decoder = None
        self.buffer = ""
        self.headerfixed = False

    def _geterrors(self):
        return self._errors

    def _seterrors(self, errors):
        # Setting ``errors`` must be done on the real decoder too
        if self.decoder is not None:
            self.decoder.errors = errors
        self._errors = errors
    errors = property(_geterrors, _seterrors)


class IncrementalEncoder(codecs.IncrementalEncoder):
    def __init__(self, errors="strict", encoding=None):
        self.encoder = None
        self.encoding = encoding
        codecs.IncrementalEncoder.__init__(self, errors)
        # Store ``errors`` somewhere else,
        # because we have to hide it in a property
        self._errors = errors
        self.buffer = u""

    def iterencode(self, input):
        for part in input:
            result = self.encode(part, False)
            if result:
                yield result
        result = self.encode(u"", True)
        if result:
            yield result

    def encode(self, input, final=False):
        if self.encoder is None:
            input = self.buffer + input
            if self.encoding is not None:
                # Replace encoding in the @charset rule with the specified one
                encoding = self.encoding
                if encoding.replace("_", "-").lower() == "utf-8-sig":
                    encoding = "utf-8"
                newinput = _fixencoding(input, unicode(encoding), final)
                if newinput is None: # @charset rule incomplete => Retry next time
                    self.buffer = input
                    return ""
                input = newinput
            else:
                # Use encoding from the @charset declaration
                self.encoding = _detectencoding_unicode(input, final)
            if self.encoding is not None:
                if self.encoding == "css":
                    raise ValueError("css not allowed as encoding name")
                info = codecs.lookup(self.encoding)
                encoding = self.encoding
                if self.encoding.replace("_", "-").lower() == "utf-8-sig":
                    input = _fixencoding(input, u"utf-8", True)
                self.encoder = info.incrementalencoder(self._errors)
                self.buffer = u""
            else:
                self.buffer = input
                return ""
        return self.encoder.encode(input, final)

    def reset(self):
        codecs.IncrementalEncoder.reset(self)
        self.encoder = None
        self.buffer = u""

    def _geterrors(self):
        return self._errors

    def _seterrors(self, errors):
        # Setting ``errors ``must be done on the real encoder too
        if self.encoder is not None:
            self.encoder.errors = errors
        self._errors = errors
    errors = property(_geterrors, _seterrors)


class StreamWriter(codecs.StreamWriter):
    def __init__(self, stream, errors="strict", encoding="utf-8", header=False):
        codecs.StreamWriter.__init__(self, stream, errors)
        self.encoder = IncrementalEncoder(errors)
        self._errors = errors

    def encode(self, input, errors='strict'):
        return (self.encoder.encode(input, False), len(input))

    def _geterrors(self):
        return self._errors

    def _seterrors(self, errors):
        # Setting ``errors`` must be done on the encoder too
        if self.encoder is not None:
            self.encoder.errors = errors
        self._errors = errors
    errors = property(_geterrors, _seterrors)


class StreamReader(codecs.StreamReader):
    def __init__(self, stream, errors="strict"):
        codecs.StreamReader.__init__(self, stream, errors)
        self.decoder = IncrementalDecoder(errors)
        self._errors = errors

    def decode(self, input, errors='strict'):
        return (self.decoder.decode(input, False), len(input))

    def _geterrors(self):
        return self._errors

    def _seterrors(self, errors):
        # Setting ``errors`` must be done on the decoder too
        if self.decoder is not None:
            self.decoder.errors = errors
        self._errors = errors
    errors = property(_geterrors, _seterrors)


def search_function(name):
    if name == "css":
        return codecs.CodecInfo(
            name="css",
            encode=encode,
            decode=decode,
            incrementalencoder=IncrementalEncoder,
            incrementaldecoder=IncrementalDecoder,
            streamwriter=StreamWriter,
            streamreader=StreamReader,
        )


codecs.register(search_function)
