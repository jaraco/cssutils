"""productions for cssutils based on a mix of CSS 2.1 and CSS 3 Syntax
productions

- http://www.w3.org/TR/css3-syntax
- http://www.w3.org/TR/css3-syntax/#grammar0

open issues
    - numbers contain "-" if present
    - HASH: #aaa is, #000 is not anymore,
            CSS2.1: 'nmchar': r'[_a-z0-9-]|{nonascii}|{escape}',
            CSS3: 'nmchar': r'[_a-z-]|{nonascii}|{escape}',
"""
__all__ = ['CSSProductions', 'MACROS', 'PRODUCTIONS', 'RE_UNICODE']
__docformat__ = 'restructuredtext'
__author__ = '$LastChangedBy: cthedot $'
__date__ = '$LastChangedDate: 2007-09-01 15:55:42 +0200 (Sa, 01 Sep 2007) $'
__version__ = '$LastChangedRevision: 300 $'

RE_UNICODE = r'\\[0-9a-fA-F]{1,6}[\t|\r|\n|\f|\x20]?'

# a complete list of css3 macros
MACROS = {
    'ident': r'[-]?{nmstart}{nmchar}*',
    'name': r'{nmchar}+',
    'nmstart': r'[_a-zA-Z]|{nonascii}|{escape}',
    'nonascii': r'[^\0-\177]',
    'unicode': r'\\[0-9a-f]{1,6}{wc}?',
    'escape': r'{unicode}|\\[ -~\200-\777]',
    #   'escape': r'{unicode}|\\[ -~\200-\4177777]',
    'nmchar': r'[-_a-zA-Z0-9]|{nonascii}|{escape}',

    'num': r'[0-9]*\.[0-9]+|[0-9]+', #r'[-]?\d+|[-]?\d*\.\d+',
    'string':  r"""\'({stringesc1}|{stringchar}|")*\'""" + "|" + '''\"({stringesc2}|{stringchar}|')*\"''',
    # seems an error in CSS 3 but is allowed in CSS 2.1
    'stringesc1' : r"\\'",
    'stringesc2' : r'\\"',
    
    'stringchar':  r'{urlchar}| |\\{nl}',

    # urlchar  ::= [#x9#x21#x23-#x26#x27-#x7E] | nonascii | escape
    # 0x27 is "'" which should not be in here...
    'urlchar':  r'[\x09\x21\x23-\x26\x28-\x7E]|{nonascii}|{escape}',

    # from CSS2.1
    'invalid': r'{invalid1}|{invalid2}',
    'invalid1': r'\"([^\n\r\f\\"]|\\{nl}|{escape})*',
    'invalid2': r"\'([^\n\r\f\\']|\\{nl}|{escape})*",

    # what if \r\n, \n matches first?
    'nl': r'\n|\r\n|\r|\f',
    'w': r'{wc}*',
    'wc': r'\t|\r|\n|\f|\x20',

    'comment': r'\/\*[^*]*\*+([^/][^*]*\*+)*\/',

    'A': r'A|a|\\0{0,4}(?:41|61)(?:\r\n|[ \t\r\n\f])?',
    'C': r'C|c|\\0{0,4}(?:43|63)(?:\r\n|[ \t\r\n\f])?',
    'D': r'D|d|\\0{0,4}(?:44|64)(?:\r\n|[ \t\r\n\f])?',
    'E': r'E|e|\\0{0,4}(?:45|65)(?:\r\n|[ \t\r\n\f])?',
    'F': r'F|f|\\0{0,4}(?:46|66)(?:\r\n|[ \t\r\n\f])?',
    'G': r'G|g|\\0{0,4}(?:47|67)(?:\r\n|[ \t\r\n\f])?|\\G|\\g',
    'H': r'H|h|\\0{0,4}(?:48|68)(?:\r\n|[ \t\r\n\f])?|\\H|\\h',
    'I': r'I|i|\\0{0,4}(?:49|69)(?:\r\n|[ \t\r\n\f])?|\\I|\\i',
    'K': r'K|k|\\0{0,4}(?:4b|6b)(?:\r\n|[ \t\r\n\f])?|\\K|\\k',
    'L': r'L|l|\\0{0,4}(?:4c|6c)(?:\r\n|[ \t\r\n\f])?|\\L|\\l',
    'M': r'M|m|\\0{0,4}(?:4d|6d)(?:\r\n|[ \t\r\n\f])?|\\M|\\m',
    'N': r'N|n|\\0{0,4}(?:4e|6e)(?:\r\n|[ \t\r\n\f])?|\\N|\\n',
    'O': r'O|o|\\0{0,4}(?:4f|6f)(?:\r\n|[ \t\r\n\f])?|\\O|\\o',
    'P': r'P|p|\\0{0,4}(?:50|70)(?:\r\n|[ \t\r\n\f])?|\\P|\\p',
    'R': r'R|r|\\0{0,4}(?:52|72)(?:\r\n|[ \t\r\n\f])?|\\R|\\r',
    'S': r'S|s|\\0{0,4}(?:53|73)(?:\r\n|[ \t\r\n\f])?|\\S|\\s',
    'T': r'T|t|\\0{0,4}(?:54|74)(?:\r\n|[ \t\r\n\f])?|\\T|\\t',
    'U': r'U|u|\\0{0,4}(?:55|75)(?:\r\n|[ \t\r\n\f])?|\\U|\\u',
    'X': r'X|x|\\0{0,4}(?:58|78)(?:\r\n|[ \t\r\n\f])?|\\X|\\x',
    'Z': r'Z|z|\\0{0,4}(?:5a|7a)(?:\r\n|[ \t\r\n\f])?|\\Z|\\z',
    }

# The following productions are the complete list of tokens
# used by cssutils, a mix of CSS3 and some CSS2.1 productions.
# The productions are **ordered**:
PRODUCTIONS = [
    ('BOM', r'\xFEFF'),
    ('URI', r'{U}{R}{L}\({w}({string}|{urlchar}*){w}\)'),
    ('FUNCTION', r'{ident}\('),

    # from CSS2.1
    ('IMPORT_SYM', r'@{I}{M}{P}{O}{R}{T}'),#'),
    ('PAGE_SYM', r'@{P}{A}{G}{E}'),
    ('MEDIA_SYM', r'@{M}{E}{D}{I}{A}'),
    ('FONT_FACE_SYM', r'@{F}{O}{N}{T}\\?\-{F}{A}{C}{E}'),
    ('CHARSET_SYM', r'@charset '), # from Errata includes ending space!
    ('NAMESPACE_SYM', r'@{N}{A}{M}{E}{S}{P}{A}{C}{E}'),
    # from CSS3
    ('ATKEYWORD', r'@{ident}'),

    # in CSS2.1: r'\!({w}|{comment})*{I}{M}{P}{O}{R}{T}{A}{N}{T}'),
    ##('IMPORTANT_SYM', r'{I}{M}{P}{O}{R}{T}{A}{N}{T}'),

    ('IDENT', r'{ident}'),
    ('STRING', r'{string}'),
    # from CSS2.1
    ('INVALID', r'{invalid}'),

    ('HASH', r'\#{name}'),
    ('PERCENTAGE', r'{num}\%'),
    ('DIMENSION', r'{num}{ident}'),
    ('NUMBER', r'{num}'),
    #???
    ('UNICODE-RANGE', r'[0-9A-F?]{1,6}(\-[0-9A-F]{1,6})?'),
    ('CDO', r'\<\!\-\-'),
    ('CDC', r'\-\-\>'),
    ('S', r'{wc}+'),
    ('INCLUDES', '\~\='),
    ('DASHMATCH', r'\|\='),
    ('PREFIXMATCH', r'\^\='),
    ('SUFFIXMATCH', r'\$\='),
    ('SUBSTRINGMATCH', r'\*\='),

    # checked specially if fullsheet is parsed
    ('COMMENT', r'{comment}'), #r'\/\*[^*]*\*+([^/][^*]*\*+)*\/'),

    # MUST always be last
    ('CHAR', r'[^"\']')
    ]

class CSSProductions(object):
    """
    most attributes are set later
    """
    EOF = True

for i, t in enumerate(PRODUCTIONS):
    setattr(CSSProductions, t[0].replace('-', '_'), t[0])
