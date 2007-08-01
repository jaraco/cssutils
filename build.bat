set DISTUTILS_DEBUG='1'

rem NEEDS MANIFEST.in !
del MANIFEST

python setup.py build
