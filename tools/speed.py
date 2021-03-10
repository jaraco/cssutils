import timeit

do = """
import cssutils
css = '''
@font-face {
  font-family: 'WebFont';
  src: url('myfont.eot');  /* IE6-8 */
  src: local('xxx'),
        url('myfont.woff') format('woff'),  /* FF3.6, IE9 */
        url('myfont.ttf') format('truetype');  /* Saf3+,Chrome,FF3.5,Opera10+ */
}
a {
/**//**//**//**//**//**//**//**/
/**//**//**//**//**//**//**//**/
color: red;
display: none;
position: absolute;
left: 1px;
top: 2px;
background: 1px url(x) no-repeat left top;
padding: 1px 1px 2px 5cm;
font: normal 1px/5em Arial, sans-serif;

}    '''
p = cssutils.CSSParser(parseComments=False)
sheet = p.parseString(10*css)
"""
t = timeit.Timer(do)  # outside the try/except
try:
    print(t.timeit(20))  # or t.repeat(...)
except Exception:
    print(t.print_exc())
