"""Selector is a single Selector of a CSSStyleRule SelectorList.

Partly implements
    http://www.w3.org/TR/css3-selectors/

TODO
    - .contains(selector)
    - .isSubselector(selector)

    - ??? CSS2 gives a special meaning to the comma (,) in selectors.
        However, since it is not known if the comma may acquire other
        meanings in future versions of CSS, the whole statement should be
        ignored if there is an error anywhere in the selector, even though
        the rest of the selector may look reasonable in CSS2.

        Illegal example(s):

        For example, since the "&" is not a valid token in a CSS2 selector,
        a CSS2 user agent must ignore the whole second line, and not set
        the color of H3 to red:
"""
__all__ = ['Selector']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy$'
__date__ = '$LastChangedDate$'
__version__ = '$LastChangedRevision$'

import xml.dom

import cssutils

class Selector(cssutils.util.Base):
    """
    (cssutils) a single selector in a SelectorList of a CSSStyleRule

    Properties
    ==========
    selectorText
        textual representation of this Selector
    prefixes
        a set which prefixes have been used in this selector
    seq
        sequence of Selector parts including comments

    Format
    ======
    ::

        # implemented in SelectorList
        selectors_group
          : selector [ COMMA S* selector ]*
          ;

        selector
          : simple_selector_sequence [ combinator simple_selector_sequence ]*
          ;

        combinator
          /* combinators can be surrounded by white space */
          : PLUS S* | GREATER S* | TILDE S* | S+
          ;

        simple_selector_sequence
          : [ type_selector | universal ]
            [ HASH | class | attrib | pseudo | negation ]*
          | [ HASH | class | attrib | pseudo | negation ]+
          ;

        type_selector
          : [ namespace_prefix ]? element_name
          ;

        namespace_prefix
          : [ IDENT | '*' ]? '|'
          ;

        element_name
          : IDENT
          ;

        universal
          : [ namespace_prefix ]? '*'
          ;

        class
          : '.' IDENT
          ;

        attrib
          : '[' S* [ namespace_prefix ]? IDENT S*
                [ [ PREFIXMATCH |
                    SUFFIXMATCH |
                    SUBSTRINGMATCH |
                    '=' |
                    INCLUDES |
                    DASHMATCH ] S* [ IDENT | STRING ] S*
                ]? ']'
          ;

        pseudo
          /* '::' starts a pseudo-element, ':' a pseudo-class */
          /* Exceptions: :first-line, :first-letter, :before and :after. */
          /* Note that pseudo-elements are restricted to one per selector and */
          /* occur only in the last simple_selector_sequence. */
          : ':' ':'? [ IDENT | functional_pseudo ]
          ;

        functional_pseudo
          : FUNCTION S* expression ')'
          ;

        expression
          /* In CSS3, the expressions are identifiers, strings, */
          /* or of the form "an+b" */
          : [ [ PLUS | '-' | DIMENSION | NUMBER | STRING | IDENT ] S* ]+
          ;

        negation
          : NOT S* negation_arg S* ')'
          ;

        negation_arg
          : type_selector | universal | HASH | class | attrib | pseudo
          ;

    """
    def __init__(self, selectorText=None, readonly=False):
        """
        selectorText
            initial value of this selector
        readonly
            default to False
        """
        super(Selector, self).__init__()

        self.seq = self._newseq()
        self.prefixes = set()
        if selectorText:
            self.selectorText = selectorText
        self._readonly = readonly


    def _getSelectorText(self):
        """
        returns serialized format
        """
        return cssutils.ser.do_css_Selector(self)

    def _setSelectorText(self, selectorText):
        """
        NEW
        """
        self._checkReadonly()
        tokenizer = self._tokenize2(selectorText)
        if not tokenizer:
            self._log.error(u'Selector: No selectorText given.')
        else:
            # prepare tokenlist!
            # "*" -> type "universal"
            # "*"|IDENT + "|" -> combined to "namespace_prefix"
            # "|" -> type "namespace_prefix"
            # "." + IDENT -> combined to "class"
            tokens = []
            for t in tokenizer:
                typ, val, lin, col = t
                if val == u':' and tokens and self._type(tokens[-1]) == 'pseudo-class' and\
                   self._tokenvalue(tokens[-1]) != u'::':
                    tokens[-1] = ('pseudo-element', u'::', lin, col)
                elif val == u':':
                    tokens.append(('pseudo-class', u':', lin, col))

                elif val == u'*' and tokens and self._type(tokens[-1]) == 'namespace_prefix' and\
                     self._tokenvalue(tokens[-1]).endswith(u'|'):
                    tokens[-1] = ('universal', self._tokenvalue(tokens[-1])+val, lin, col)
                elif val == u'*':
                    tokens.append(('universal', val, lin, col))

                elif typ == 'IDENT' and tokens and self._tokenvalue(tokens[-1]) == u'.':
                    tokens[-1] = ('class', u'.'+val, lin, col)

                elif val == u'|' and tokens and self._type(tokens[-1]) in ('IDENT', 'universal') and\
                     self._tokenvalue(tokens[-1]).find(u'|') == -1:
                    tokens[-1] = ('namespace_prefix', self._tokenvalue(tokens[-1])+u'|', lin, col)
                elif val == u'|':
                    tokens.append(('namespace_prefix', val, lin, col))

                elif typ == u'FUNCTION' and val == u'not(':
                    tokens.append(('negation', val, lin, col))
                else:
                    tokens.append(t)
                #import pprint;pprint.pprint( tokens)

            tokenizer = (t for t in tokens) # TODO: not elegant at all!

            # for closures: must be a mutable
            new = {'valid': True,
                   'prefixes': set(),
                   'lastindex': None
                   }
            # used for equality checks and setting of a space combinator
            S = u' '

            def append(seq, val, typ=None):
                "appends to seq and sets lastindex"
                seq.append(val, typ)
                new['lastindex'] = len(seq) - 1

            def last(seq):
                "returns value of last relevant token, new['lastindex'] needs to be updated!"
                if new['lastindex'] is not None:
                    return seq[new['lastindex']]
                else:
                    return None

            def setlasttype(seq, type):
                "sets type of last relevant token, new['lastindex'] needs to be updated!"
                if new['lastindex'] is not None:
                    seq.types[new['lastindex']] = type

            #expected
            simple_selector_sequence = 'type_selector universal HASH class attrib pseudo negation '
            simple_selector_sequence2 = 'HASH class attrib pseudo negation '

            combinator = ' combinator'
            negation_arg = 'type_selector universal HASH class attrib pseudo'
            colon1 = 'pseudo-element pseudo-class FUNCTION'

            def _universal(expected, seq, token, tokenizer=None):
                # *|* or prefix|*
                val, typ = self._tokenvalue(token), self._type(token)
                if 'universal' in expected:
                    append(seq, val, typ)
                    new['prefixes'].add(val.split(u'|')[0])
                    if negation_arg == expected:
                        return ')'
                    else:
                        return simple_selector_sequence2 + combinator

                else:
                    self._log.error(
                        u'Selector: Unexpected universal.', token=token)
                    return expected

            def _namespace_prefix(expected, seq, token, tokenizer=None):
                # prefix| => element_name
                val, typ = self._tokenvalue(token), self._type(token)
                if 'type_selector' in expected:
                    append(seq, val, typ)
                    new['prefixes'].add(val.split(u'|')[0])
                    return 'element_name'
                else:
                    self._log.error(
                        u'Selector: Unexpected namespace prefix.', token=token)
                    return expected

            def _pseudo(expected, seq, token, tokenizer=None):
                # pseudo-class or pseudo-element
                val, typ = self._tokenvalue(token), self._type(token)
                if 'pseudo' in expected and not expected[0] == 'pseudo':
                    append(seq, val, typ)
                    if negation_arg == expected:
                        return ('pseudo', ')') # two steps expected!
                        #return ('pseudo', negation_arg) # two steps expected!
                    else:
                        return ('pseudo', simple_selector_sequence2 + combinator)
                        #return ('pseudo', simple_selector_sequence + combinator)

                else:
                    self._log.error(
                        u'Selector: Unexpected start of pseudo.', token=token)
                    return expected

            def _func(expected, seq, token, tokenizer=None):
                # not(
                val = self._tokenvalue(token, normalize=True)
                if 'pseudo' == expected[0]:
                    # part of pseudo, will be combined
                    lasttype = seq.types[len(seq)-1]
                    seq[-1] = (seq[-1] + val, lasttype)

                    # TODO: do FUNCTION
                    functokens = self._tokensupto2(tokenizer, funcendonly=True)

                    append(seq, '...)', 'TODO')

                    if lasttype == 'pseudo-element':
                        # pseudo-element (::) must be last of simple_selector_sequence
                        return combinator
                    else:
                        return expected[1]

                else:
                    self._log.error(
                        u'Selector: Unexpected FUNCTION.', token=token)
                    return expected

            def _ident(expected, seq, token, tokenizer=None):
                # identifier
                val, typ = self._tokenvalue(token), self._type(token)
                if 'type_selector' in expected or 'element_name' == expected:
                    # element name after ns or complete type_selector
                    append(seq, val, typ)
                    if negation_arg == expected:
                        return ')'
                    else:
                        return simple_selector_sequence2 + combinator

                elif 'pseudo' == expected[0]:
                    # part of pseudo, will be combined
                    lasttype = seq.types[len(seq)-1]
                    seq[-1] = (seq[-1] + val, lasttype)

                    lastnval = self._normalize(seq[-1])
                    if lasttype == 'pseudo-element' or lastnval in (
                       ':first-line', ':first-letter', ':before', ':after'):
                        # pseudo-element (::)  or :first-line, :first-letter, :before and :after
                        # must be last of simple_selector_sequence
                        return combinator
                    elif expected[1] != negation_arg:
                        return expected[1]
                    else:
                        return u')'

                else:
                    print expected
                    self._log.error(
                        u'Selector: Unexpected IDENT.', token=token)
                    return expected

            def _class(expected, seq, token, tokenizer=None):
                # .IDENT
                val, typ = self._tokenvalue(token), self._type(token)
                if 'class' in expected:
                    append(seq, val, typ)

                    if negation_arg == expected:
                        return ')'
                    else:
                        return simple_selector_sequence2 + combinator

                else:
                    self._log.error(
                        u'Selector: Unexpected class.', token=token)
                    return expected

            def _hash(expected, seq, token, tokenizer=None):
                # #IDENT
                val, typ = self._tokenvalue(token), self._type(token)
                if 'HASH' in expected:
                    append(seq, val, typ)

                    if negation_arg == expected:
                        return ')'
                    else:
                        return simple_selector_sequence2 + combinator

                else:
                    self._log.error(
                        u'Selector: Unexpected HASH.', token=token)
                    return expected

            def _S(expected, seq, token, tokenizer=None):
                # S
                val, typ = self._tokenvalue(token), self._type(token)
                if 'combinator' in expected:
                    append(seq, S, 'combinator')
                    return simple_selector_sequence + combinator
                else:
                    return expected

            def _char(expected, seq, token, tokenizer=None):
                # + > ~ S
                val, typ = self._tokenvalue(token), self._type(token)
                if val in u'+>~' and 'combinator' in expected:
                    # no other combinator except S may be following
                    if seq and S == seq[-1]:
                        seq[-1] = (val, 'combinator')
                    else:
                        append(seq, val, 'combinator')
                    return simple_selector_sequence

                elif u':' == val and 'pseudo' in expected:
                    # ':' ':'? [ IDENT | functional_pseudo ]
                    append(seq, val)
                    if negation_arg == expected:
                        return ') pseudo'
                    elif ') pseudo' == expected:
                        return ')'
                    else:
                        return simple_selector_sequence2 + combinator

                elif u')' == val and u')' in expected:
                    # end of "not( negation_arg"
                    append(seq, val)

                    if type(expected) == tuple:
                        return expected[1]
                    else:
                        return simple_selector_sequence

                elif u'[' == val and 'attrib' in expected:
                    # start of [attrib]
                    attribtokens = self._tokensupto2(tokenizer, starttoken=token,
                                                     selectorattendonly=True)
                    # TODO
                    append(seq, '[...]', 'TODO')
                    if negation_arg == expected:
                        return ')'
                    else:
                        return simple_selector_sequence2 + combinator

                else:
                    self._log.error(
                        u'Selector: Unexpected CHAR.', token=token)
                    return expected


            def _negation(expected, seq, token, tokenizer=None):
                # not(
                val = self._tokenvalue(token, normalize=True)
                if 'negation' in expected:
                    append(seq, val, 'negation')
                    return negation_arg
                else:
                    self._log.error(
                        u'Selector: Unexpected not(.', token=token)
                    return expected

            # expected: only|not or mediatype, mediatype, feature, and
            newseq = self._newseq()
            valid, expected = self._parse(expected=simple_selector_sequence,
                seq=newseq, tokenizer=tokenizer,
                productions={'CHAR': _char,
                             'class': _class,
                             'FUNCTION': _func,
                             'HASH': _hash,
                             'IDENT': _ident,
                             'namespace_prefix': _namespace_prefix,
                             'negation': _negation,
                             'pseudo-class': _pseudo,
                             'pseudo-element': _pseudo,
                             'universal': _universal,
                             'S': _S})
            valid = valid and new['valid']

            if valid:
                self.seq = newseq
                self.prefixes = new['prefixes']





    def OLD_setSelectorText(self, selectorText):
        """
        DOMException on setting

        - INVALID_MODIFICATION_ERR: (self)
          Raised if the specified CSS string value represents a different
          type than the current one, e.g. a SelectorList.
        - NO_MODIFICATION_ALLOWED_ERR: (self)
          Raised if this rule is readonly.
        - SYNTAX_ERR: (self)
          Raised if the specified CSS string value has a syntax error
          and is unparsable.
        """
        def preprocess(tokens):
            """
            remove S at start and end,
            if around a combinator (ignoring comments)
            or in att []
            """
            # remove starting S
            if tokens[0].type == self._ttypes.S:
                del tokens[0]
            COMBINATORS_NO_S = u'+>~'
            r = []
            attlevel = 0
            i = 0

            i, imax = 0, len(tokens) # imax may be changed later!
            while i < imax:
                t = tokens[i]
                if self._ttypes.S == t.type and attlevel > 0:
                    # remove all WS in atts 1st level
                    i += 1
                    continue

                elif t.value in COMBINATORS_NO_S and attlevel == 0:
                    # remove preceding S from found except token!=Comment
                    before = len(r)
                    while before >= 0:
                        before -= 1
                        if r[before].type == self._ttypes.S:
                            del r[before]
                        elif r[before].type != self._ttypes.COMMENT:
                            break
                    # remove following S from tokens except token!=Comment
                    after = i+1
                    while after < imax:
                        if tokens[after].type == self._ttypes.S:
                            del tokens[after]
                            after -= 1 # BECAUSE DELETED ONE!
                            imax = len(tokens) # new imax!
                        elif tokens[after].type != self._ttypes.COMMENT:
                            break
                        after += 1
                elif t.value == u'[':
                    attlevel += 1
                elif t.value == u']':
                    attlevel -= 1
                r.append(t)
                i += 1

            # remove ending S
            if r and r[-1].type == self._ttypes.S:
                del r[-1]
            return r

        def addprefix(seq):
            """
            checks if last item in seq was a namespace prefix
            and if yes adds it to newprefixes
            """
            try:
                # may also be comment...
                if isinstance(seq[-1], dict) and \
                   seq[-1]['type'] in ('type', 'attributename'):
                    newprefixes.add(seq[-1]['value'])
                    seq[-1]['type'] = 'prefix'
                else:
                    newprefixes.add('')
            except IndexError:
                pass

        def getAttrib(atttokens):
            """
            atttokens
                a sequence of tokens without any S which are preprocessed

            returns seq of selector attribute

            Format
            ======
            attrib
              : '[' S* IDENT S* [ [ '=' | INCLUDES | DASHMATCH ] S*
                [ IDENT | STRING ] S* ]? ']' ;

            CSS3 additionally:
                ^= PREFIXMATCH
                $= SUFFIXMATCH
                *= SUBSTRINGMATCH
            """
            attseq = []
            expected = "[" # att, comb or ], value, pipe
            i, imax = 0, len(atttokens)
            while i < imax:
                t = atttokens[i]
                if self._ttypes.COMMENT == t.type: # just add
                    attseq.append(cssutils.css.CSSComment(t))

                # [ start
                elif expected == '[' and t.value == u'[':
                    attseq.append({'type': 'attribute selector', 'value': t.value})
                    expected = 'att'
                elif expected == '[':
                    self._log.error(u'Selector: No Attrib start "[" found.', t)
                    return

                # ] end
                elif expected in ('comb or ]', ']') and t.value == u']':
                    attseq.append({'type': 'attribute selector end', 'value': t.value})
                    assert i == len(atttokens) - 1 # should really be end
                    break
                elif expected == 'pipe' and t.value == u']':
                    self._log.error(u'Selector: No attribute name for namespace start found.', t)
                    return

                # * (must be followed by |)
                elif expected == 'att' and t.type == self._ttypes.UNIVERSAL:
                    attseq.append({'type': 'type', 'value': t.value})
                    expected = 'pipe'

                # | namespace pipe
                elif expected in ('pipe', 'att', 'comb or ]') and \
                     t.value == u'|':
                    addprefix(attseq)
                    attseq.append({'type': 'type', 'value': t.value})
                    expected = 'att'

                elif expected == 'att' and t.type == self._ttypes.IDENT:
                    attseq.append({'type': 'attributename', 'value': t.value})
                    expected = 'comb or ]'
                elif expected == 'att':
                    self._log.error(u'Selector: No Attrib found.', t)
                    return

                # CSS3 selectors added
                elif expected == 'comb or ]' and t.value in (
                     u'=', u'~=', u'|=', u'^=', u'$=', u'*='):
                    attseq.append({'type': 'combinator', 'value': t.value})
                    expected = 'val'
                elif expected == 'comb or ]':
                    self._log.error(u'Selector: No Attrib combinator found.', t)
                    return

                elif expected == 'val' and t.type in (
                     self._ttypes.IDENT, self._ttypes.STRING):
                    attseq.append({'type': 'attributevalue', 'value': t.value})
                    expected = ']'
                elif expected == 'val':
                    self._log.error(u'Selector: No Attrib value found.', t)
                    return

                else:
                    self._log.error(u'Selector: Unknown Attrib syntax.', t)
                    return

                i += 1

            else: # in case of ] not found
                self._log.error(u'Selector: Incomplete Attrib.', t)
                return

            return attseq

        def getFunc(functokens):
            """
            functokens
                a sequence of tokens

            returns seq of selector functional_pseudo

            Format
            ======
            functional_pseudo
              : FUNCTION S* expression ')'
              ;
            """
            funcseq = [{'type': 'function', 'value': functokens[0].value}]
            expected = ")" # expr or )
            i, imax = 1, len(functokens)
            while i < imax:
                t = functokens[i]

                if self._ttypes.COMMENT == t.type: # just add
                    funcseq.append(cssutils.css.CSSComment(t))

                elif t.value == u')':
                    funcseq.append(
                        {'type': 'function end', 'value': t.value})
                    expected = None
                    assert i == len(functokens) - 1 # should really be end
                    break

                else:
                    funcseq.append({'type': 'functionvalue', 'value': t.value})

                i += 1

            if expected:
                self._log.error(
                    u'Selector: Incomplete functional pseudo "%s".' %
                    self._valuestr(functokens))
                return

            return funcseq

        self._checkReadonly()

        tokens = self._tokenize(selectorText)
        if tokens:
            COMBINATORS = u' >+~'
            tokens = preprocess(tokens)

            newseq = []
            newprefixes = set()
            found1 = False
            # simple_selector | combinator: u' >+~' |
            # pseudoclass after : | pseudoelement after ::
            expected = 'simple_selector'
            i, imax = 0, len(tokens)
            while i < imax:
                t = tokens[i]
                ##print t.value, t.type, expected
                # , invalid SelectorList
                if self._ttypes.COMMA == t.type:
                    self._log.error(u'Selector: Possible SelectorList found.', t,
                              error=xml.dom.InvalidModificationErr)
                    return

                # /* comments */
                elif self._ttypes.COMMENT == t.type and expected not in (
                     'classname', 'pseudoclass', 'pseudoelement'):
                    # just add
                    newseq.append(cssutils.css.CSSComment(t))

                # . class
                elif expected.startswith('simple_selector') and \
                     t.type == self._ttypes.CLASS:
                    newseq.append({'value': t.value, 'type': 'class'})
                    found1 = True
                    expected = 'classname'
                elif expected == 'classname' and t.type == self._ttypes.IDENT:
                    newseq.append({'value': t.value, 'type': 'classname'})
                    expected = 'simple_selector or combinator'

                # pseudoclass ":" or pseudoelement "::"
                elif expected.startswith('simple_selector') and \
                     t.value == u':' or t.value == u'::':
                    expected = {
                        ':': 'pseudoclass', '::': 'pseudoelement'}[t.value]
                    newseq.append({'value': t.value, 'type': expected})
                    found1 = True
                elif expected.startswith('pseudo') and \
                     t.type == self._ttypes.IDENT:
                    newseq.append({'value': t.value, 'type': 'pseudoname'})
                    expected = 'simple_selector or combinator'
                elif expected == 'pseudoclass' and \
                     t.type == self._ttypes.FUNCTION:
                    # pseudo "function" like lang(...)
                    functokens, endi = self._tokensupto(
                        tokens[i:], funcendonly=True)
                    i += endi
                    funcseq = getFunc(functokens)
                    if not funcseq:
                        self._log.error(
                            u'Selector: Invalid functional pseudo.', t)
                        return
                    newseq.extend(funcseq)
                    expected = 'simple_selector or combinator'
                elif expected == 'pseudoclass':
                    self._log.error(u'Selector: Pseudoclass name expected.', t)
                    return
                elif expected == 'pseudoelement':
                    self._log.error(u'Selector: Pseudoelement name expected.', t)
                    return

                # #hash
                elif expected.startswith('simple_selector') and \
                     t.type == self._ttypes.HASH:
                    newseq.append({'value': t.value, 'type': 'id'})
                    found1 = True
                    expected = 'simple_selector or combinator'

                # | namespace pipe
                elif expected.startswith('simple_selector') and \
                     t.value == u'|':
                    addprefix(newseq)
                    newseq.append({'type': 'pipe', 'value': t.value})
                    found1 = True
                    expected = 'namespaced element'

                # element, *
                elif (expected.startswith('simple_selector') or
                      expected == 'namespaced element') and \
                     t.type in (self._ttypes.IDENT, self._ttypes.UNIVERSAL):
                    newseq.append({'value': t.value, 'type': 'type'})
                    found1 = True
                    expected = 'simple_selector or combinator'
                # element, *
                elif expected == 'namespaced element' and \
                     t.type not in (self._ttypes.IDENT, self._ttypes.UNIVERSAL):
                    self._log.error(u'Selector: Namespaced element expected.', t)
                    return

                # attribute selector
                elif expected.startswith('simple_selector') and t.value == u'[':
                    atttokens, endi = self._tokensupto(
                        tokens[i:], selectorattendonly=True)
                    i += endi
                    attseq = getAttrib(atttokens)
                    if not attseq:
                        self._log.warn(
                            u'Selector: Empty attribute selector.', t)
                        return
                    newseq.extend(attseq)
                    found1 = True
                    expected = 'simple_selector or combinator'

                # CSS3 combinator ~
                elif expected == 'simple_selector or combinator' and \
                     t.value in COMBINATORS or t.type == self._ttypes.S:
                    if t.type == self._ttypes.S:
                        newseq.append({'value': t.normalvalue, 'type': 'combinator'}) # single u' '
                    else:
                        newseq.append({'value': t.value, 'type': 'combinator'})
                    expected = 'simple_selector' # or [
                elif expected == 'simple_selector or combinator':
                    self._log.error(u'Selector: No combinator found.', t)
                    return

                else:
                    self._log.error(u'Selector: Expected simple selector.', t)
                    return

                i += 1

            if expected == 'classname':
                self._log.error(u'Selector: Class name expected: %s.' %
                          selectorText)
                return
            elif expected == 'namespaced element':
                self._log.error(u'Selector: No element found for namespace start: %s.' %
                          selectorText)
                return
            elif expected == 'pseudoclass':
                self._log.error(u'Selector: Pseudoclass name expected: %s.' %
                          selectorText)
                return
            elif expected == 'pseudoelement':
                self._log.error(u'Selector: Pseudoelement name expected: %s.' %
                          selectorText)
                return
            elif newseq and ((
                    isinstance(newseq[-1], basestring) and \
                    newseq[-1] in COMBINATORS
                    ) or ( # may be a dict
                    isinstance(newseq[-1], dict) and
                    isinstance(newseq[-1]['value'], basestring) and \
                    newseq[-1]['value'] in COMBINATORS)):
                self._log.error(u'Selector: Cannot end with combinator: %s.' %
                    selectorText)
                return

            if found1:
                self.seq = newseq
                self.prefixes = newprefixes
##                import pprint;pprint.pprint(newseq)
##                print self.prefixes
            else:
                self._log.error(
                    u'Selector: No selector found: %s.' % selectorText)
        else:
            self._log.error(u'Selector: Empty selector.')

    selectorText = property(_getSelectorText, _setSelectorText,
        doc="(DOM) The parsable textual representation of the selector.")

    def __repr__(self):
        return "cssutils.css.%s(selectorText=%r)" % (
                self.__class__.__name__, self.selectorText)

    def __str__(self):
        return "<cssutils.css.%s object selectorText=%r at 0x%x>" % (
                self.__class__.__name__, self.selectorText, id(self))


if __name__ == '__main__':
    s = Selector()
    s.selectorText = u'n1|a[n2|x]' #u'::a:b()'
    print s.selectorText
