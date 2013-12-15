set PYTHONPATH=src
%PY2% -V

@echo off
set DISTUTILS_DEBUG='1'

rem NEEDS MANIFEST.in !
rem del MANIFEST

echo
echo "set __version__ in setup.py"
echo
pause

%PY2PATH%\scripts\nosetests -v -w src\cssutils\tests --with-doctest
pause
%PY2PATH%\scripts\nosetests -v -w examples --with-doctest
pause

%PY2% examples\testutil.py
pause

rem sphinx
rem pause

rem python setup.py sdist bdist_egg
%PY2% setup.py register sdist bdist_egg bdist_wininst
rem bdist_rpm upload

@echo on
