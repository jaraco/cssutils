#!/usr/bin/env python
"""CSS Tokenizer
"""
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '0.9.2b2 $LastChangedRevision$'

import string
import xml.dom

from token import Token, Tokenre
import cssutils


tokenregex = Tokenre()
tokentype = Token


class Tokenizer(object):
    """
    generates a list of Token objects
    """
    WS = ' \t\r\n\f'
    ttypes = tokentype

    _typelist = [
        (lambda t: t == u';', tokentype.SEMICOLON),
        (lambda t: t == u'{', tokentype.LBRACE),
        (lambda t: t == u'}', tokentype.RBRACE),
        (lambda t: t == u'[', tokentype.LBRACKET),
        (lambda t: t == u']', tokentype.RBRACKET),
        (lambda t: t == u'(', tokentype.LPARANTHESIS),
        (lambda t: t == u')', tokentype.RPARANTHESIS),
        (lambda t: t == u',', tokentype.COMMA),
        (lambda t: t == u'.', tokentype.CLASS),
        (tokenregex.w, tokentype.S),
        (tokenregex.num, tokentype.NUMBER), 
        (tokenregex.atkeyword, tokentype.ATKEYWORD),
        (tokenregex.HASH, tokentype.HASH), 
        (tokenregex.DIMENSION, tokentype.DIMENSION), 
        (tokenregex.ident, tokentype.IDENT), 
        (tokenregex.string, tokentype.STRING)
    ]
    _delimmap = {
        u'*': tokentype.UNIVERSAL,
        u'.': tokentype.CLASS,
        u'>': tokentype.GREATER,
        u'+': tokentype.PLUS,
        u'~': tokentype.TILDE
    }
    _attmap = {
        u'~=': tokentype.INCLUDES,
        u'|=': tokentype.DASHMATCH,
        u'^=': tokentype.PREFIXMATCH,
        u'$=': tokentype.SUFFIXMATCH,
        u'*=': tokentype.SUBSTRINGMATCH
    }
    _atkeywordmap = {
        u'charset': tokentype.CHARSET_SYM,
        u'import': tokentype.IMPORT_SYM,
        u'media': tokentype.MEDIA_SYM,
        u'namespace': tokentype.NAMESPACE_SYM,
        u'page': tokentype.PAGE_SYM
        }

    def __init__(self):
        self.log = cssutils.log
        self._sub1ofcol = False
  
    def getttype(self, t):
        """
        check type of tokentype in t which may be string or list
        returns ttype
        """
        if isinstance(t, list): t = u''.join(t)
        
        for check, result in Tokenizer._typelist:
            if check(t): return result
         
        return tokentype.DELIM

            
    def addtoken(self, value, ttype=None):
        """
        adds a new Token to self.tokens
        """
        # convert list of tokens to string
        if isinstance(value, list): value = u''.join(value)
        if not value: return

        if not ttype: ttype = self.getttype(value)        
        
        # last two tokens, if none simple use empty Token
        if len(self.tokens) > 0: last = self.tokens[-1]
        else: last = Token()
        if len(self.tokens) > 1: last2 = self.tokens[-2]
        else: last2 = Token()

        # marker if token already added
        todo = False

        # WS, simply add later
        if ttype == tokentype.S:
            todo = True
            
        # ATKEYWORD: standard, need to adjust type
        elif ttype == tokentype.ATKEYWORD:
            normkeyword  = value[1:].lower().replace(u'\\', u'')
            ttype = Tokenizer._atkeywordmap.get(
                normkeyword, tokentype.ATKEYWORD)
            todo = True

        # ATKEYWORD: replace last token if @xxx 
        elif u'@' == last.value and ttype == tokentype.IDENT:
            keyword = value.lower()
            normkeyword = keyword.replace(u'\\', u'')
            last.type = Tokenizer._atkeywordmap.get(
                normkeyword, tokentype.ATKEYWORD)
            last.value = u'@%s' % keyword # replace @

        # @-ATKEYWORD: replace last2 if @-xxx and remove last
        # probably vendor specific
        elif u'@' == last2.value and u'-' == last.value and \
           ttype == tokentype.IDENT:
            keyword = value.lower()
            normkeyword = keyword.replace(u'\\', u'')
            last2.type = Tokenizer._atkeywordmap.get(
                normkeyword, tokentype.ATKEYWORD)
            last2.value = u'@-%s' % keyword # replace @
            self.tokens.pop(-1) # remove -

        # IDENT, NUMBER or DIMENSION with -, replace last token
        # -IDENT probably vendor specific
        elif u'-' == last.value and (ttype in (
           tokentype.IDENT, tokentype.NUMBER, tokentype.DIMENSION)):
            last.type = ttype
            last.value = u'-%s' % value.lower()        
      
        # DIMENSION: replace last token with num + ident
        elif last.type == tokentype.NUMBER and\
             ttype == tokentype.IDENT:
            last.type = tokentype.DIMENSION
            last.value = u'%s%s' % (last.value, value.lower())
            ## check if before was a -?

        # HASH: replace last token with # + name
        elif self.getttype(last.value + value) == tokentype.HASH:
            last.type = tokentype.HASH
            last.value += value # last value starts with # anyway

        # FUNCTION: replace last token with last.value(
        elif last.type == tokentype.IDENT and u'(' == value:
            last.type = tokentype.FUNCTION
            last.value = u'%s(' % last.value.lower()

        # PERCENTAGE: replace last token with NUMBER%
        elif last.type == tokentype.NUMBER and u'%' == value:
            last.type = tokentype.PERCENTAGE
            last.value = u'%s%%' % last.value

        # IMPORTANT_SYM: combine with preceding "!" if only WS in between
        # No comments in between!
        elif u'important' == value.lower().replace(u'\\', u''):
            for i in range(len(self.tokens), 0, -1):
                _t = self.tokens[i - 1]
                # check if preceding was "!" => !important and delete nexts
                if u'!' == _t.value:
                    _t.type = tokentype.IMPORTANT_SYM
                    _t.value = u'!%s' % value.lower() # keep im\portant?
                    del self.tokens[i:]
                    break
                # other than S means no !important => add
                elif _t.type != tokentype.S:
                    self.tokens.append(
                        Token(self.line, self.col, ttype, value))
                    break

        # URI: possible combine if closed URI or EOF
        elif u')' == value or ttype == tokentype.EOF:
            # find opening {ident}(
            _uriindex = -1
            for i in range(len(self.tokens), 0, -1):
                _t = self.tokens[i-1]
                if tokentype.FUNCTION == _t.type and u'url(' == _t.value:
                    _uriindex = i - 1
                    break
                elif tokentype.FUNCTION == _t.type:
                    # no url( found but other so stop searching
                    todo = True # add )
                    break

            if _uriindex > -1:
                # check content between "url(" and ")"
                _uricontent = u''
                for i in range(_uriindex+1, len(self.tokens)):
                    _t = self.tokens[i]
                    if _t.type == tokentype.S and\
                     ((i == _uriindex+1) or (i == len(self.tokens)-1)):
                        # 1st or last WS ok
                        continue
                    else:
                        # found other content
                        _uricontent += _t.value
                if _uricontent:
                  # check if valid URI and save if yes
                  _uri = u'url(%s)' % _uricontent
                  if tokenregex.URI(_uri):
                      _urit = self.tokens[_uriindex]
                      _urit.type = tokentype.URI
                      _urit.value = _uri
                      del self.tokens[_uriindex + 1:]
                  else:
                      todo = True # add )
            else:
                todo = True # add )
                      
        else:
            todo = True

        # add if not two WS nodes after another
        if todo or ttype == tokentype.EOF:
            self.tokens.append(Token(self.line, self.col, ttype, value))

        # adjust x,y position
        cols = len(value)
        if self._sub1ofcol: 
            # added a "0" to ".1" -> "0.1" so PLUS 1
            cols -= 1
            self._sub1ofcol = False
        if value.find('\n') != -1: 
            # end of a line, start anew but count present chars
            self.col = 1
            cols = len(value[value.rfind('\n')+1:])

        self.line += value.count('\n')
        self.col += cols


    def getescape(self):
        """
        http://www.w3.org/TR/2004/CR-CSS21-20040225/syndata.html#q6

        Third, backslash escapes allow authors to refer to characters
        they can't easily put in a document. In this case, the
        backslash is followed by at most six hexadecimal digits
        (0..9A..F), which stand for the ISO 10646 ([ISO10646])
        character with that number, which must not be zero. If a
        character in the range [0-9a-fA-F] follows the hexadecimal
        number, the end of the number needs to be made clear. There
        are two ways to do that:

        1. with a space (or other whitespace character): "\26 B"
         ("&B"). In this case, user agents should treat a "CR/LF"
         pair (U+000D/U+000A) as a single whitespace character.
        2. by providing exactly 6 hexadecimal digits: "\000026B"
         ("&B")

        In fact, these two methods may be combined. Only one
        whitespace character is ignored after a hexadecimal escape.
        Note that this means that a "real" space after the escape
        sequence must itself either be escaped or doubled. 
        """
        escape = u'\\'
        MAX = 6
        i = 0
        actual = 0
        while self.text and i < MAX:
            i += 1
            c, c2, c3 = self.text[0], u''.join(self.text[:1]),\
                      u''.join(self.text[1:2])
            if c in string.hexdigits:
                escape += c
                del self.text[0]
            else:
                actual = i
                i = MAX # end while and goto else (break would not work)
        else:
            if int(escape[1:], 16) <= 0:
                self.log.error(
                 u'Tokenizer: Syntax Error, ESCAPE SEQUENCE with value 0.')
                escape = ''
            elif actual < MAX + 1 and c2 in self.WS:
                # remove separating WS
                del self.text[0]
                if u'\r' == c2 and u'\n' == c3:
                # remove combined WS \r\n as one WS
                    del self.text[0]

                # add explicit SPACE to end ESCAPE needed as not MAX len!
                escape += u' '

        return escape


    def dostrorcomment(self, t=[], end=None, ttype=None, _fullSheet=False):
        """
        handles
          strings: "..." or '...'
          comment: /*...*/
        
        t
            initial token to start result with
        end
            string at which to end 
        ttype
            str description of token to be found
        _fullSheet
            if no more tokens complete found tokens
        """
        if ttype == tokentype.STRING:
            isstring = True
            kind = 'string'
        else:
            isstring = False
            kind = 'comment'
            
        while self.text:
            # c is removed from self.text, c2 may be removed too later here
            c, c2 = self.text.pop(0), u''.join(self.text[:1])

            if (isstring and c == end) or\
               (not isstring and c + c2 == end):
                # check if end and add
                t.append(end)
                self.addtoken(t, ttype)
                if not isstring:
                    del self.text[0] # remove ending / (c2)
                break
            
            elif isstring and u'\\' == c and c2 in u'\n\r\f':
                # in STRING ignore and remove a combi of \ + nl
                if u'\r' == c2 and \
                   len(self.text) > 2 and u'\n' == self.text[1]:
                    #\r\n!
                    del self.text[0] # remove c2 = \r
                    del self.text[0] # remove "c3" = \n
                else:
                    del self.text[0] #remove c2 \r or \n or \f
                            
            elif isstring and c in '\n\r\f':
                # nl in String makes it invalid
                t.append(c)
                self.addtoken(t, tokentype.INVALID)
                break

            elif not isstring and u'\\' == c:
                # escape in comment does not work
                # simply keep
                t.append(c)

            elif u'\\' == c and c2 and c2 not in string.hexdigits:
                # simple escape
                t.append(c)
                t.append(c2)
                del self.text[0] # remove c2

            elif u'\\' == c and c2:
                # character escape sequence
                # sequence end character/s will be stripped!
                escape = self.getescape()
                t.append(escape)

            else:
                # save
                t.append(c)

        else:
            # EOF but complete string or comment
            if _fullSheet:
                t.append(end)
                self.addtoken(t, ttype)
            else:
                # not complete:
                value = ''.join(t)
                lines = value.count('\n')
                cols = len(value)
                if value.endswith('\n'):
                    cols = -self.col + 1;
                token = Token(self.line, self.col, None, value)
                self.line += lines
                self.col += cols
                self.log.error(
                    u'Tokenizer: Syntax Error, incomplete %s.' % kind,
                    token, xml.dom.SyntaxErr)
                

    def tokenize(self, text, _fullSheet=False):
        """
        tokenizes text and returns tokens     
        """
        if not text:
          return []
        
        self.text = list(text)
        self.tokens = []
        self.line = 1
        self.col = 1

        def addifnewtoken(t, c):
            """
            checks if c starts a new token and adds last t as token
            """
            if len(t) == 0:
                return [c] # new t
            
            tt, ct = self.getttype(t), self.getttype(c)            
##            print '"%s": (%s)\t %s: (%s)' % (c, ct, t, tt),
            
            if tt in (tokentype.ATKEYWORD, tokentype.IDENT)\
               or (t and t[-1] == u'-')\
               and ct in (tokentype.IDENT, tokentype.NUMBER):
                # @keyword or a number starting with -
                # wait for new token "x1..."
                t.append(c)

            # . is always followed by number here as calling function
            # checks this!
            elif (t[-1] == u'.' or tt == tokentype.NUMBER)\
               and ct == tokentype.NUMBER:
                # start of number which may be 1 OR 1. OR .
                if t[0] == u'.':
                    t[0] = '0.' # add 0 in any case
                    self._sub1ofcol = True
                t.append(c)

            elif tt == tokentype.NUMBER and c == u'.':
                # start of number which may be 1 OR 1. OR .
                t.append(c)

            elif ct == tokentype.DELIM: 
                # escape always alone
                # . not with number always alone
                self.addtoken(t)
                self.addtoken(c)
                t = []
               
            elif tt != ct:
                # finish old and start new token with c
                self.addtoken(t)
                t = [c]

            else: 
                # wait for new token or end
                t.append(c)
                
##            print '"%s": (%s)\t %s: (%s)\n' % (c, ct, t, tt)
##            print '----',self.tokens
            return t

        t = []
        while self.text:
            # next two chars
            c, c2 = self.text.pop(0), u''.join(self.text[:1])
            
            if c in self.WS:
                # WhiteSpace
                self.addtoken(t) # add saved
                t = [c] # initial add WS
                try:
                    while self.text[0] in self.WS:
                        t.append(self.text.pop(0))
                except IndexError: # end of CSS
                    pass
                self.addtoken(t, tokentype.S) # add WS
                t = [] # reset

            elif u'/' == c and u'*' == c2:
                # Comment
                self.addtoken(t) # add saved    
                del self.text[0] # remove *
                self.dostrorcomment(
                    [u'/*'], u'*/', tokentype.COMMENT, _fullSheet)
                t = []

            elif c in '"\'':
                # strings
                self.addtoken(t) # add saved
                self.dostrorcomment(
                    [c], c, tokentype.STRING, _fullSheet)
                t = []
                
            elif c in u';{}[](),':
                # reservedchars, type will be handled above
                self.addtoken(t) # add saved               
                self.addtoken(c)
                t = []

            elif c == u'.' and c2 in tuple(u'0123456789'):
                # possible num
                t = addifnewtoken(t, c)

            elif u'::' == c + c2:
                # CSS3 pseudo
                self.addtoken(t) # add saved
                self.addtoken(u'::', tokentype.PSEUDO_ELEMENT)
                del self.text[0] # remove c2
                t = []

            elif c in u'~|^$*' and u'=' == c2:
                # INCLUDES ~= or DASHMATCH |= + CSS3 Selectors
                self.addtoken(t) # add saved
                _t = c + c2
                self.addtoken(_t, Tokenizer._attmap[_t])
                del self.text[0] # remove c2
                t = []

            elif c == u'<' and u''.join(self.text[:3]) == u'!--':
                # CDO
                self.addtoken(t) # add saved       
                del self.text[:3]
                self.addtoken(u'<!--', tokentype.CDO)
                t = []
            elif c == u'-' and u''.join(self.text[:2]) == u'->':
                # CDC
                self.addtoken(t) # add saved       
                del self.text[:2]
                self.addtoken(u'-->', tokentype.CDC)
                t = []

            elif c in u'.=~|*+>#!%:&$':
                # DELIM reservedchars, possibly combined later
                self.addtoken(t) # add saved               
                self.addtoken(
                    c, Tokenizer._delimmap.get(c, tokentype.DELIM))
                t = []
                
            elif u'\\' == c and c2 not in string.hexdigits:
                # simple escape
                t.append(c)
                t.append(c2)
                del self.text[0]
            elif u'\\' == c and c2:
                # character escape sequence
                escape = self.getescape()
                t = addifnewtoken(t, escape)

            else:
                # save
                t = addifnewtoken(t, c)
        else:
            # add remaining
            self.addtoken(t)

        if _fullSheet:
            # add EOF token if from parse or CSSStyleSheet.cssText
            self.addtoken(u'EOF', tokentype.EOF)

        return self.tokens


if __name__ == '__main__':
    """
    NOT LIKE SPEC:
      between ! and important only WS is allowed, no comments, this should
      be very seldomly used anyway 

    TODO:
      Tokenizer:
        
      parser:
        - filter CDO/CDC
        - lengths: % px pt pc em ex in cm mm

    CSS2 parses a number immediately followed by an identifier as a
    DIMEN token (i.e., an unknown unit), CSS1 parsed it as a number
    and an identifier. That means that in CSS1, the declaration
    'font: 10pt/1.2serif' was correct, as was 'font: 10pt/12pt serif';
    in CSS2, a space is required before "serif". (Some UAs accepted
    the first example, but not the second.)        
    """
    css = u'''5px -5px'''

    tokens = Tokenizer().tokenize(css)
    import pprint
    pprint.pprint(tokens)
    print 40* '-'

    sheet = cssutils.parseString(css)
    print sheet.cssText
    print 40* '-'
