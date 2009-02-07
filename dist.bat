python -V

@echo off
set DISTUTILS_DEBUG='1'

rem NEEDS MANIFEST.in !
rem del MANIFEST

echo
echo "set __version__ in setup.py"
echo
pause

nosetests -v -w src\tests --with-doctest 
pause
nosetests -v -w examples --with-doctest 
pause

python examples\testutil.py
pause

rem python epydoc -o doc --name cssutils --url http://cthedot.de/cssutils/ src/cssutils --show-imports
rem pause

rem python setup.py sdist bdist_egg
python setup.py register sdist bdist_egg bdist_wininst
rem bdist_rpm upload

@echo on
