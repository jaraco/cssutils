"""Base class for all tests"""

import logging
import re
import sys
import pytest

if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources

import cssutils


def get_sheet_filename(sheet_name):
    """Get the filename for the given sheet."""
    return resources.files('cssutils') / 'tests' / 'sheets' / sheet_name


class BaseTestCase:
    def setup(self):
        # a raising parser!!!
        cssutils.log.raiseExceptions = True
        cssutils.log.setLevel(logging.FATAL)
        self.p = cssutils.CSSParser(raiseExceptions=True)

    def assertRaisesEx(
        self, exception, callable, *args, exc_args=None, exc_pattern=None, **kwargs
    ):
        assert exc_args is None
        with pytest.raises(exception, match=exc_pattern):
            callable(*args, **kwargs)

    def assertRaisesMsg(self, excClass, msg, callableObj, *args, **kwargs):
        with pytest.raises(excClass, match=re.escape(msg)):
            callableObj(*args, **kwargs)

    def do_equal_p(self, tests, att='cssText', debug=False, raising=True):
        """
        if raising self.p is used for parsing, else self.pf
        """
        p = cssutils.CSSParser(raiseExceptions=raising)
        # parses with self.p and checks att of result
        for test, expected in list(tests.items()):
            if debug:
                print('"%s"' % test)
            s = p.parseString(test)
            if expected is None:
                expected = test
            assert str(s.__getattribute__(att), 'utf-8') == expected

    def do_raise_p(self, tests, debug=False, raising=True):
        # parses with self.p and expects raise
        p = cssutils.CSSParser(raiseExceptions=raising)
        for test, expected in list(tests.items()):
            if debug:
                print('"%s"' % test)
            with pytest.raises(expected):
                p.parseString(test)

    def do_equal_r(self, tests, att='cssText', debug=False):
        # sets attribute att of self.r and asserts Equal
        for test, expected in list(tests.items()):
            if debug:
                print('"%s"' % test)
            self.r.__setattr__(att, test)
            if expected is None:
                expected = test
            assert self.r.__getattribute__(att) == expected

    def do_raise_r(self, tests, att='_setCssText', debug=False):
        # sets self.r and asserts raise
        for test, expected in list(tests.items()):
            if debug:
                print('"%s"' % test)
            with pytest.raises(expected):
                self.r.__getattribute__(att)(test)

    def do_raise_r_list(self, tests, err, att='_setCssText', debug=False):
        # sets self.r and asserts raise
        for test in tests:
            if debug:
                print('"%s"' % test)
            with pytest.raises(err):
                self.r.__getattribute__(att)(test)


class GenerateTests(type):
    """Metaclass to handle a parametrized test.

    This works by generating many test methods from a single method.

    To generate the methods, you need the base method with the prefix
    "gen_test_", which takes the parameters. Then you define the attribute
    "cases" on this method with a list of cases. Each case is a tuple, which is
    unpacked when the test is called.

    Example::

        def gen_test_length(self, string, expected):
            self.assertEquals(len(string), expected)
        gen_test_length.cases = [
            ("a", 1),
            ("aa", 2),
        ]
    """

    def __new__(cls, name, bases, attrs):
        new_attrs = {}
        for aname, aobj in list(attrs.items()):
            if not aname.startswith("gen_test_"):
                new_attrs[aname] = aobj
                continue

            # Strip off the gen_
            test_name = aname[4:]
            cases = aobj.cases
            for case_num, case in enumerate(cases):
                stringed_case = cls.make_case_repr(case)
                case_name = "%s_%s_%s" % (test_name, case_num, stringed_case)

                # Force the closure binding
                def make_wrapper(case=case, aobj=aobj):
                    def wrapper(self):
                        aobj(self, *case)

                    return wrapper

                wrapper = make_wrapper()
                wrapper.__name__ = case_name
                wrapper.__doc__ = "%s(%s)" % (test_name, ", ".join(map(repr, case)))
                if aobj.__doc__ is not None:
                    wrapper.__doc__ += "\n\n" + aobj.__doc__
                new_attrs[case_name] = wrapper
        return type(name, bases, new_attrs)

    @classmethod
    def make_case_repr(cls, case):
        if isinstance(case, str):
            value = case
        else:
            try:
                iter(case)
            except TypeError:
                value = repr(case)
            else:
                value = '_'.join(cls.make_case_repr(x) for x in case)
        value = re.sub('[^A-Za-z_]', '_', value)
        value = re.sub('_{2,}', '_', value)
        return value
