REM set PY3 to your Python 3 exe
REM set PY3PATH to your Python 3 install dir
REM (tested with py3.2 64)

xcopy /e src src3
REM  -f idioms
%PY3% %PY3PATH%\tools\scripts\2to3.py --no-diffs -nw src3