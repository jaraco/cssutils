import codecs
import pathlib

import cssutils


__here__ = pathlib.Path(__file__).parent


def main():
    cases = __here__.parent / 'sheets' / 'cases.css'
    cssText = codecs.open(cases, encoding='css').read()
    sheet = cssutils.parseString(cssText)
    print(sheet)
    print(sheet.cssText)


__name__ == '__main__' and main()
