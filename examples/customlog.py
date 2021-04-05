import logging
import io

import cssutils


EXPOUT = ""
EXPERR = """Property: Unknown Property name. [1:5: x]
HTTPError opening url=http://cthedot.de/x: 404 Not Found
CSSImportRule: While processing imported style sheet href=http://cthedot.de/x: IOError('Cannot read Stylesheet.',)
CSSStylesheet: CSSImportRule not allowed here. [1:13: @import]
"""


def main():
    mylog = io.StringIO()
    h = logging.StreamHandler(mylog)
    h.setFormatter(logging.Formatter('%(levelname)s    %(message)s'))
    cssutils.log.setLevel(logging.INFO)

    cssutils.parseString('a { x: 1; } @import "http://cthedot.de/x";')

    cssutils.log.removeHandler(h)


if __name__ == '__main__':
    main()
