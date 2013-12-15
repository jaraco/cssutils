teset PYTHONPATH=src
%PY2PATH%\scripts\nosetests -v -w src\cssutils\tests --with-doctest
%PY2PATH%\scripts\nosetests -v -w examples --with-doctest