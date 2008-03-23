"""
convert files in txt to html with adjusted links and img/@src (all absolute)
"""
from docutils.core import publish_file
import codecs
import fnmatch
from lxml import etree
import os
import shutil

from config import *

def preparedirs():
    "prepare directories"
    print '* removing old "%s"' % TARGETDIR
    try:
        shutil.rmtree(TARGETDIR)
    except OSError, e:
        print e

def convert2html():
    "convert *.txt to *.html"
    print '* converting rst to html'
    for dir, dirs, files in os.walk(RST_ROOT):
        if '\\.svn' not in dir:
            print '\t*', dir

            try:
                newdir = dir.replace(RST_ROOT, TARGETDIR, 1)
                os.mkdir(newdir)
            except OSError, e:
                print '\t', e

            for f in fnmatch.filter(os.listdir(dir), '*%s' % RST_EXT):
                s = os.path.join(dir, f)
                t = s.replace(RST_ROOT, TARGETDIR, 1)
                t = '%s%s' % (os.path.splitext(t)[0], '.html')
                print '\t\t+ %s -> %s' % (s, t)
                publish_file(source_path=s, destination_path=t, writer_name='html')

def adjusthtml():
    # replace href="*.txt" to href="*.html"
    print '* adjusting HTML paths (@href, @src)'

    def rel(dummy, href, level):
        "xpath extension function: make href relative"
        if href.endswith('/'):
            href += 'index.html'
        if href.startswith('/'):
            href = href[1:]
        if level > 0:
            for i in range(0, int(level)):
                href = '../%s' % href
        return href

    # register xpath extension function
    ns = etree.FunctionNamespace('py')
    ns['rel'] = rel

    # prepare transformer
    transform = etree.XSLT(etree.parse(open('py/resthtml-fixlinks.xsl')))

    for dir, dirs, files in os.walk(TARGETDIR):
        print '\t*', dir
        for filename in fnmatch.filter(os.listdir(dir), '*.html'):
            print '\t\t+', filename

            f = os.path.join(dir, filename)

            x = codecs.open(f, encoding='utf-8').read()
            x = x.replace('&nbsp;', '&#160;')
            xf = codecs.open(f, 'w', encoding='utf-8')
            xf.write(x)
            xf.close()
            try:
                result = transform(etree.parse(open(f)), level='%i' % dir.count('\\'))
            except Exception, e:
                print e, f
                result = x

            # save
            target = open(f, 'w')
            target.write(str(result))
            target.close()

#def copystatic(paths, target=TARGETDIR):
#    """copy all files from path to target path keeping directory layout but filtering ".svn" dirs"""
#    for pathname in paths:
#        print '* copy static files "%s"' % pathname
#        for path, dirnames, filenames in os.walk(pathname):
#            if '\\.svn' not in path:
#                tpath = os.path.join(target, path)
#                try:
#                    os.makedirs(tpath)
#                except OSError, e:
#                    pass
#                for f in filenames:
#                    s, d = os.path.join(path, f), os.path.join(tpath, f)
#                    if s.endswith('.css'):
#                        print "\t* copying %s to %s" % (s,d)
#                        shutil.copy2(s, d)


if __name__ == '__main__':
    preparedirs()
    convert2html()
    adjusthtml()
    shutil.copy2('rst/docs/default.css',
                 '../docs_html/docs/default.css')

    print "\nFINAL HTML docs are complete in ./%s/" % TARGETDIR

