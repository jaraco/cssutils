#!/usr/bin/env python
"""cssutils ErrorHandler

ErrorHandler
    used as log with usual levels (debug, info, warn, error)

    if instanciated with ``raiseExceptions=True`` raises exeptions instead
    of logging

log
    defaults to instance of ErrorHandler for any kind of log message from
    lexerm, parser etc.

    - raiseExceptions = [False, True]
    - setloglevel(loglevel)
"""
__all__ = ['ErrorHandler']
__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import logging
import xml.dom

class _ErrorHandler(object):
    """
    handles all errors and log messages
    """
    def __init__(self, log,
                 defaultloglevel=logging.DEBUG, raiseExceptions=False):
        """
        inits log if none given

        log
            for parse messages, default logs to sys.stderr
        defaultloglevel
            if none give this is logging.DEBUG
        raiseExceptions
            - True: Errors will be reported to the calling app,
              e.g. during building
            - False: Errors will be written to the log, this is the
              default behaviour when parsing
        """
        if log:
            self._log = log
        else:
            import sys
            self._log = logging.getLogger('CSSUTILS')
            hdlr = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter('%(levelname)s\t%(message)s')
            hdlr.setFormatter(formatter)
            self._log.addHandler(hdlr)
            self._log.setLevel(defaultloglevel)

        self.raiseExceptions = raiseExceptions

    def __getattr__(self, name):
        # here if new log has been set
        _logcalls = {
            u'debug': self._log.debug,
            u'info': self._log.info,
            u'warn': self._log.warn,
            u'critical': self._log.critical,
            u'fatal': self._log.fatal,
            u'error': self._log.error
            }

        if name in _logcalls.keys():
            self._logcall = _logcalls[name]
            return self.__handle
        else:
            raise AttributeError(
                '(errorhandler) No Attribute "%s" found' % name)

    def setlog(self, log):
        """set log of errorhandler's log"""
        self._log = log

    def setloglevel(self, level):
        """set level of errorhandler's log"""
        self._log.setLevel(level)

    def __handle(self, msg=u'', token=None, error=xml.dom.SyntaxErr,
                 neverraise=False):
        """
        handles all calls
        logs or raises exception
        """
        if token:
            if isinstance(token, tuple):
                msg = u'%s [%s:%s: %s]' % (
                    msg, token[2], token[3], token[1])
            else:
                msg = u'%s [%s:%s: %s]' % (
                    msg, token.line, token.col, token.value)

        if error and self.raiseExceptions and not neverraise:
            raise error(msg)
        else:
            self._logcall(msg)


class ErrorHandler(_ErrorHandler):
    "Singleton, see _ErrorHandler"
    instance = None

    def __init__(self,
            log=None, defaultloglevel=logging.INFO, raiseExceptions=True):

        if ErrorHandler.instance is None:
            ErrorHandler.instance = _ErrorHandler(log=log,
                                        defaultloglevel=defaultloglevel,
                                        raiseExceptions=raiseExceptions)
        self.__dict__ = ErrorHandler.instance.__dict__
