@echo off
set DISTUTILS_DEBUG='1'

rem NEEDS MANIFEST.in !
rem del MANIFEST

echo
echo "set __version__ in setup.py"
echo
pause

python setup.py test
pause

python epydoc -o doc --name cssutils --url http://cthedot.de/cssutils/ src/cssutils --show-imports
pause

rem python setup.py sdist bdist_egg
python setup.py register sdist bdist_egg bdist_wininst
rem upload

@echo on
