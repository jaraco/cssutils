import codecs
import pathlib

import cssutils

__here__ = pathlib.Path(__file__).parent


def main():
    cases = __here__.parent / 'sheets' / 'cases.css'
    with codecs.open(cases, encoding='css') as f:
        cssText = f.read()
    sheet = cssutils.parseString(cssText)
    print(sheet)
    print(sheet.cssText)


__name__ == '__main__' and main()
