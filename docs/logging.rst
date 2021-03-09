.. module:: cssutils.errorhandler

.. index::
    single: log, cssutils.log
    object: cssutils.log

logging
=======

A global logger is used throughout the library. You may configure it or even replace it with your own. Customizing the default log should be sufficient for most purposes though.

The default logger is available as ``cssutils.log``. It has the following methods which are basically the same as defined for standard ``logging`` loggers:

* ``log.setLevel(level)`` and ``log.getEffectiveLevel()``, example::

    import logging
    cssutils.log.setLevel(logging.FATAL)

* ``log.addHandler(h)`` and ``log.removeHandler(h)``
* ``log.*(msg)`` where ``*`` is one of ``debug``, ``info``, ``warn``, ``error`` or ``fatal``/``critical``

Additional method: ``cssutils.log.setLog(newlog)``: To replace the default log which sends output to ``stderr``.


See also :meth:`cssutils.css.Property.validate` for details on how properties log.