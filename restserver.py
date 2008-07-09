"""
ReSTserver
==========
:Author: Christof Hoeke
:Date: 080315
:Description: a simple reStructuredText Server
:Version: 2.1 (not release standalone)
:License: This module has been placed in the public domain. (New license from v2.0)

* reStructuredText (ReST) requests - URLs ending with / or extension RST_EXT (default ``.txt``) - will be served as HTML on the fly
* if no filename is given (URL ``/``) "index." + RST_EXT is tried to prevent a maybe older index.html to be shown (from v1.3)
* the ReST file docroot is in RST_ROOT (default ``rst``)
* .html requests will be checked if RST_EXT file with same name is present, if yes the request will be redirected to the RST_EXT file (and then served as above)
* other requests (CSS, images etc) use default SimpleHTTPServer behaviour
* supports command line options same as those for rst2html.py with a patch from Felix Wiemann
* GET and HEAD are supported
"""
import os
import sys
import traceback
import BaseHTTPServer
import SimpleHTTPServer

# for eggs
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

try:
    import pkg_resources
except ImportError:
    pass
else:
    pkg_resources.require('docutils')


import docutils.core
import docutils.io


# import constants
try:
    from config import *
except ImportError:
    PATH = ''
    PORT = 8082
    RST_EXT = '.txt'
    RST_ROOT = '.'


class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        """
        RST_EXT files will be transformed to XHTML with docutils
        .html request will look for RST_EXT with same name
        """
        p = '/%s%s' % (RST_ROOT, str(self.path))

        if p.endswith('/'): # maybe a .RST_EXT link already
            p = '%sindex%s' % (p, RST_EXT)

        if p.endswith(RST_EXT):
            p = p[1:] # remove starting /
            html = output = ''
            try:
                
                html = docutils.core.publish_string(open(p).read(),
                                                writer_name='html',
                                                settings_overrides={
                                                    'template': os.path.join('lib',
                                                                             'template.txt'),
                                                    'embed_stylesheet': False,
                                                    'xml_declaration': False
                                                    })
            except:
                output = traceback.format_exc()
                print >>sys.stderr, output
                self.send_response(500)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                # following is correct but would conflict with Docutils META element:
                # self.send_header("Content-Type", "application/xhtml+xml; charset=utf-8")
            output += html
            self.send_header("Content-Length", len(output))
            self.end_headers()
            self.wfile.write(output)

        elif p.endswith('.html'):
            # should be generated from RST_EXT?
            temp = p[:-5] + RST_EXT
            if os.path.isfile(temp[1:]):
                self.send_response(302)
                self.send_header("Location", temp)
                self.end_headers()

        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


    def do_HEAD(self):
        """
        RST_EXT files will be transformed to XHTML with docutils
        .html request will look for RST_EXT with same name
        """
        p = '/%s%s' % (RST_ROOT, str(self.path))

        if p.endswith('/'): # maybe a .RST_EXT link already
            p = '%sindex%s' % (p, RST_EXT)

        if p.endswith(RST_EXT):
            p = p[1:] # remove starting /
            if os.path.isfile(p):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
            else:
                self.send_response(404)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()

        elif p.endswith('.html'):
            # should be generated from RST_EXT?
            temp = p[:-5] + RST_EXT
            if os.path.isfile(temp[1:]):
                self.send_response(302)
                self.send_header("Location", temp)
                self.end_headers()

        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_HEAD(self)

def run(server_class=BaseHTTPServer.HTTPServer,
        handler_class=Handler, port=PORT):
    server_address = (PATH, port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
    try:
        port = sys.argv[1]
    except IndexError:
        port = PORT
    print 'serving on (localhost) %s:%s' % (PATH, port)
    print 'stop with CTRL + PAUSE'
    run(port=port)
