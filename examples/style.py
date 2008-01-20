# -*- coding: utf-8 -*-
"""
example renderer

moves infos from external stylesheet "css" to internal @style attributes 
and for debugging also in @title attributes.

adds css as text to html
"""
import codecs
import webbrowser
import cssutils
from lxml import etree
from lxml.builder import E
from lxml.cssselect import CSSSelector

def getDocument(html, css=None):
    """
    returns a DOM of html, if css is given it is appended to html/body as 
    pre.cssutils
    """
    document = etree.HTML(html)
    if css:
        # prepare document (add css for debugging)
        e = etree.Element('pre', {'class': 'cssutils'})
        e.text = css
        document.find('body').append(e)
    return document
    
def styleattribute(element):
    "returns css.CSSStyleDeclaration of inline styles, for html: @style"
    cssText = element.get('style')
    if cssText:
        return cssutils.css.CSSStyleDeclaration(cssText=cssText)
    else:
        return None

def getView(document, css, media='all', name=None, 
            styleCallback=lambda element: None):
    """
    document
        a DOM document, currently an lxml HTML document
    css
        a CSS StyleSheet string
    media: optional
        TODO: view for which media it should be
    name: optional
        TODO: names of sheets only
    styleCallback: optional
        should return css.CSSStyleDeclaration of inline styles, for html
        a style declaration for ``element@style``. Gets one parameter 
        ``element`` which is the relevant DOMElement
    
    returns style view
        a dict of {DOMElement: css.CSSStyleDeclaration} for html
    """
    sheet = cssutils.parseString(css)
    
    view = {}
    specificities = {} # needed temporarily 

    # TODO: filter rules simpler?, add @media
    rules = (rule for rule in sheet if rule.type == rule.STYLE_RULE)    
    for rule in rules:
        for selector in rule.selectorList:
            
            # TODO: make this a callback to be able to use other stuff than lxml
            cssselector = CSSSelector(selector.selectorText)
            matching = cssselector.evaluate(document)
            for element in matching:
                # add styles for all matching DOM elements
                if element not in view:
                    # add initial
                    view[element] = cssutils.css.CSSStyleDeclaration()
                    specificities[element] = {}                    
                    # add inline styles if present
                    inlinestyle = styleCallback(element)
                    if inlinestyle:
                        for p in inlinestyle:
                            # set inline style specificity
                            view[element].setProperty(p)
                            specificities[element][p.name] = (1,0,0,0)
                                                        
                for p in rule.style:
                    # update styles
                    if p not in view[element]:
                        view[element].setProperty(p)
                        specificities[element][p.name] = selector.specificity
                    else:
                        sameprio = (p.priority == 
                                    view[element].getPropertyPriority(p.name))
                        if not sameprio and bool(p.priority) or (
                           sameprio and selector.specificity >= 
                                        specificities[element][p.name]):
                            # later, more specific or higher prio 
                            view[element].setProperty(p)              

    return view                        

def render2style(document, view):
    """
    - add style into @style attribute
    - add style into @title attribute (for debugging)
    """
    for element, style in view.items():
        v = style.getCssText(separator=u'')
        element.set('style', v)
        element.set('title', v)

def render2content(document, view, css):
    """
    - add css as <style> element to be rendered by browser
    - replace elements content with actual style
    
    result is a HTML which the browser renders itself from the original css
    cssutils only writes debugging, useful to compare with render2style
    """
    e = etree.Element('style', {'type': 'text/css'})
    e.text = css
    document.find('head').append(e)
    for element, style in view.items():
        v = style.getCssText(separator=u'')
        element.text = v

def show(text, name, encoding='utf-8'):
    "saves text to file with name and encoding"
    f = codecs.open(name, 'w', encoding=encoding)
    f.write(text)
    f.close()
    webbrowser.open(name)

def main():
    tpl = '''<html><head><title>style test</title></head><body>%s</body></html>'''
    html = tpl % '''
            <h1>Style example 1</h1>
            <p>simple p</p>
            <p style="color: red;">p with inline style: "color: red"</p>
            <p id="x" style="color: red;">p#x with inline style: "color: red"
                but see a#x!</p>
        '''
    css = '''
        body {
            color: blue !important;
            font: normal 100% sans-serif;
        }
        p {
            c\olor: green;
            font-size: 2em;
        }
        p#x {
            color: black !important;
        }
        .cssutils {
            font: 1em "Lucida Console", monospace;
            border: 1px outset;
            padding: 5px;
        }
    '''
    # TODO:
    #defaultsheet = cssutils.parse('sheets/default_html4.css')
    
    # adds style to @style
    document = getDocument(html, css)
    view = getView(document, css, styleCallback=styleattribute)
    render2style(document, view)
    text = etree.tostring(document, pretty_print=True)
    show(text, '__tempinline.html')

    # replaces elements content with style
    document = getDocument(html)
    view = getView(document, css, styleCallback=styleattribute)
    render2content(document, view, css)    
    text = etree.tostring(document, pretty_print=True)
    show(text, '__tempbrowser.html')

    
if __name__ == '__main__':
    import sys
    sys.exit(main())