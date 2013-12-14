@echo off
rem set PYTHONPATH=E:\dev-a3\cssutils\src3
%PY3% -V
echo **run 2to3, tests files in src3!** 
@echo on

%PY3% setup3.py test
