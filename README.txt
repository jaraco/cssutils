=============================================
                 cssutils
=============================================
---------------------------------------------
CSS Cascading Style Sheets library for Python
---------------------------------------------
:author: $LastChangedBy$
:date: $LastChangedDate$
:version: trunk, $LastChangedRevision$

Copyright (C) 2004-2007 Christof Hoeke
Published under the LGPL, see http://cthedot.de/cssutils/license.html

A Python package to parse and build CSS Cascading Style Sheets. Partly implements the `DOM Level 2 Style <http://www.w3.org/TR/2000/REC-DOM-Level-2-Style-20001113/>`_ Stylesheets and DOM Level 2 CSS interfaces.

Please visit http://cthedot.de/cssutils/ for full details and updates.


.. contents::

installation
============
From 0.9 cssutils uses EasyInstall. Please find installation instructions and more information about EasyInstall from http://peak.telecommunity.com/DevCenter/EasyInstall#installation-instructions.

After installing EasyInstall simple use::

    > easy_install cssutils

to install the latest version of cssutils.

Alternatively download the provided source distribution. Expand the file and from a command line install with::

    > python setup.py install

Before using EasyInstall the first time or using the sdist please remove any old version which should be installed at PYTHONDIR/Lib/site-packages/cssutils.


known issues
============
- implementation is not after the latest grammar and specification. There will be minor differences but generally nothing too serious (I hope ;).

- CSSStyleDeclaration.getCSSValue and Value Classes are not fully implemented. These are currently in work and may be fully implemented in one of the next releases (0.9.3)

- media queries like ``@media all and (color)`` result in an error and the rules are not parsed or included in the resulting CSSStyleSheet. Media queries will be added in one of the next releases (0.9.3 maybe)

- CSS2Properties not implemented completely (setting a property does not set related properties like setting margin does not set margin-left etc

- @charset not implemented according to spec (plan: 0.9.2)
- unknown @-rules are not handled properly in cases, tests are spotty there too

- Tantek hack (using ``voice-family``) is mangled so does not work after reserializing. This is as property order is changed and the hack needs a specific order. Other CSS hacks do work though (e.g. ``color: red; c\olor: green;``.

- escapes of CSS special characters does not really work but is very uncommon (e.g \@a without being an atkeyword or .\1 being a classname selector)

- Properties are not bound to any CSS Version, so all properties are handled so
  *NOT* as described in http://www.w3.org/TR/CSS21/syndata.html#parsing-errors "Illegal values". (A future version might be customizable to a specific CSS version like 1.0 or 2.1)

- Property.value is only checked for valid CSS2 properties, so will accept more than allowed. In case of an error a WARNING is issued only


changes
=======
- TODO: FEATURE: Implementation of css.CSSValue


HEAD
    - FEATURE: Implemented css.CSSValue, css.CSSPrimitiveValue and css.CSSValueList. 
        
        **THESE ARE NOT FINISHED YET!**

        CURRENTLY IN WORK:
            - css.CSSPrimitiveValue.getStringValue, .setStringValue
            
        TODO:
            - css.CSSPrimitiveValue.getFloatValue, .setFloatValue
            - css.CSSPrimitiveValue.getCounterValue
            - css.CSSPrimitiveValue.getRGBColorValue
            - css.CSSPrimitiveValue.getRectValue
        
        css.CSSValueList
            - the list is iterable so may be used in a for loop
            

        + CSSValue has an init Parameter ``_propertyname`` to set a context property for validation. If none is set the value is always invalid. **THIS MAY CHANGE!**
        + FEATURE: CSSValue has property ``cssValueTypeString`` which is the name of the relevant ``cssValueType``, e.g. "CSS_PRIMITIVE_TYPE". Mainly useful for debugging.
        + FEATURE: CSSPrimitiveValue has property ``primitiveTypeString`` which is the name of the relevant ``primitiveType``, e.g. "CSS_PX". Mainly useful for debugging.
    
    - FEATURE (**experimental**): added ``CSSStyleDeclaration.replaceUrls(replacer)`` which may be used to adjust all "url()" values in a style declaration.

    - FEATURE: CSSRule and sub classes have a property ``typeString`` which is the name of the relevant ``type``, e.g. "STYLE_RULE". Mainly useful for debugging.

    - FEATURE: href and media arguments can now be passed to parse() and parseString() functions and methods. This sets the appropriate attributes on the generated stylesheet objects.
    - FEATURE: The MediaList constructor can now be passed a list of media types.

    - API CHANGE (experimental!): CSSStyleDeclaration.getPropertyCSSValue() for shorthand properties like e.g. ``background`` should return None. cssutils returns a CSSValueList in these cases now. Use with care as this may change later
    - API CHANGE: CSSValue default cssText is now ``u""`` and not ``u"inherit"`` anymore

    - CHANGE: The Selector class is now available from cssutils.css too.
    - CHANGE: Added __repr__ methods to most classes. The module is slightly bended as all classes are imported to cssutils.css but not defined there.
    
        - CSSStyleSheet (showing the title and href),
        - CSSCharsetRule (showing the encoding).
        - CSSImportRule (showing the href).
        - CSSNameSpaceRule (showing the prefix and uri).
        - CSSPageRule (showing the selectorText)
        - CSSMediaRule (showing the media list)
        - CSSStyleRule (showing the selector)
        - CSSStyleDeclaration (showing the number of properties set)
        - CSSValue (showing the value type and value)
        - CSSPrimitiveValue (showing the primitive value type and value)
        
    - BUGFIX (minor): removed debug output in CSSStyleDeclaration

0.9.2b3 070804
    - FEATURE: Script ``cssparse`` handles more than one file at a time now (patch from Issue #6 by Walter D�rwald)

    - BUGFIX: Fixed Issue #7: typo gave AssertionError for selectors like ``tr:nth-child(odd) td{}``
    - BUGFIX: Fixed Issue #5: false warning for certain values for ``background-position`` removed
    - BUGFIX: Report of line/col for any node was not correct if a node contained line breaks itself

    - Quite a few internal optimizations (thanks to Walter D�rwald)
    - Added tests for issues #3 and #4 to tokenizer too

0.9.2b2 070728
    - BUGFIX: Fixed Issue #4, tokenizing of color values like ``#00a`` was buggy (mixture of numbers and characters). Also warnings of invalid property values should be more reliable now (regexes in ``css.cssproperties`` changed).

0.9.2b1 070726
    - BUGFIX: Fixed Issue #3, WS was not handled properly if added to token list by tokenizer

0.9.2a5 070624
    - BUGFIX: Unexpected end of style sheet now handled according to spec for most cases, e.g. incomplete CSSStyleRule, CSSMediaRule, CSSImportRule, CSSNamespaceRule, CSSPageRule.

0.9.2a4 070620
    - BUGFIX (major): no changes to the library, but fixed setup of source dist
0.9.2a3 071018
    - no changes to the library, just optimized setuptools dist

0.9.2a2 070617
    - API CHANGE: removed cssutils.util.normalize function, use static (but private!) method cssutils.util.Base._normalize if absolutely needed which may be change too though
    - API CHANGE (minor): removed ``getFormatted`` and ```pprint`` from various classes which were both DEPRECATED for some time anyway
    - API CHANGE (minor): _Property.value is DEPRECATED, use _Property.cssValue.cssText instead, _Property is defined as private anyway so should not be used directly
    - API CHANGE (minor): removed ``Tokenizer.tokensupto`` which was used internally only

    - CHANGE: Numbers and Dimensions starting with "." like ".1em" in the original stylesheet will be output as "0.1em" with a proceding 0 now.
    - CHANGE: Report of parsing errors have a slightly different syntax now.

    - FEATURE: New ``Preferences.omitLastSemicolon`` option. If ``True`` omits ; after last property of CSSStyleDeclaration

    - BUGFIX: The css validator definition for "num" was wrong, so values like ``-5.5em`` would issue a warning but should be correct
    - BUGFIX: Dimension were not parsed correcly so 1em5 was parsed a "1em" + 5 which should really be one "1em5" were "em5" is an unknown dimension. This had probably no effect on current stylesheets but was a tokenizing error
    - BUGFIX: Parsing of nested blocks like {}, [] or () is improved
    - BUGFIX: Comment were not parsed correctly, now ``/*\*/`` is a valid comment
    - BUGFIX: ``css.Selector`` had a warning which called "warning" which in fact is named "warn". Some other error messages gave token list instead of a more useful string in case of an error, that is fixed as well (CSSComment and CSSValue).

    - IMPROVEMENT: Line number are still not given for all errors reported but for at least some more now
    - IMPROVEMENT: Performance of the tokenizer has been improved, it is now about 20% faster (testing the unittests) which may not hold for all usages but is not too bad as well ;)

0.9.2a1 070610
    - FEATURE: Partly Implemented css.CSS2Properties so you can now use::

        >>> sheet = cssutils.parseString('a { font-style: italic; }')
        >>> style = sheet.cssRules[0].style
        >>> style.fontStyle = 'normal'
        >>> print style.fontStyle
        normal

      Each property can be retrieved from CSSStyleDeclaration object with its name as
      an object property. Names with "-" in it like ``font-style`` need to be called by
      the respective DOM name ``fontStyle``.
      Setting a property value works the same way and even ``del`` which effectively removes a property from a CSSStyleDeclaration works. For details see CSSStyleDeclaration.

      Not implemented are the finer details, see the module documentation of
      cssutils.css.cssproperties.

    - BUGFIX: CSSStyleDeclaration.getPropertyCSSValue returns None for all shorthand properties

    - refactored some parts and added more tests


0.9.1b3 070114
    - **CHANGE** for Serializer preference options:

        new name
        + ``defaultAtKeyword`` instead of ``normalkeyword``
        + ``defaultPropertyName`` instead of ``normalpropertyname``

        camelcase now:
        + ``keepComments`` instead of ``keepComments``
        + ``lineNumbers`` instead of ``linenumbers``

        replaced (see below)
        + ``keepAllProperties`` instead of ``keepsimilarnamedproperties``

    - FEATURE: ``Serializer.prefs.keepAllProperties`` replaces `` ``keepsimilarnamedproperties``:
        if ``True`` all properties given in the parsed CSS are kept.
        This may be useful for cases like::

            background: url(1.gif) fixed;
            background: url(2.gif) scroll;

        Certain UAs may not know fixed and will therefor ignore property 1 but
        an application might simply like to prettyprint the stylesheet without
        loosing any information.

        Defaults to ``False``.

        See examples/serialize.py for an usage example.

    - FEATURE(experimental, might change!):
        ``CSSStyleDeclaration.getSameNamePropertyList(name)``
        Experimental method to retrieve a SameNamePropertyList object which
        holds all Properties with the given ``name``. The object has an
        attribute ``name`` and a list of Property objects each with an actual name,
        value and priority.

        ``CSSStyleDeclaration.setProperty`` has a new positional parameter
        ``overwrite`` which defines if the property which is set overwrites any former
        value (or values, see ``getSameNamePropertyList``) (default behaviour) or the
        given value is appended to any former value (overwrite=False).
        Useful for cases where a property should have different values for different UAs.

        Example 1: CSS hacks::

            width: 100px; /* wrong box model value for IE5-5.5 */
            padding: 5px;
            w\idth: 90px; /* correct box model value for later browsers */

        Example 2: UA capabilities::

            background: url(2.gif) scroll; /* Fallback for UA which do not understand fixed */
            background: url(1.gif) fixed; /* UA which do know fixed */

    - FEATURE: Reimplemented csscapture, which uses the new serializer preference ``keepAllProperties``

    - BUGFIX(major!): Serializer outputs actual property depending on Property priority out now
        see ``examples/serialize.py``

    - BUGFIX(minor): Parameter ``name`` for `CSSStyleDeclaration.XXX(name)``
      is normalized now, so ``color``, ``c\olor`` and ``COLOR`` are all equivalent


0.9.1b2 070111
    - FEATURE: added ``Serializer.prefs.keepsimilarnamedproperties``:
        if ``True`` all properties with the same normalname but different
        actual names are kept, e.g. color, c\olor, co\lor.
        This is mainly useful to keep a stylesheet complete which uses
        xbrowser hacks as above.

        **UPDATE IN 0.9.1b3!**

    - BUGFIX (minor): ``Serializer.prefs.normalpropertyname`` did not work properly if a property was set 2 times in the same declaration, e.g. ``color: red;c\olor: green`` setting the pref to ``False`` results in ``c\olor: green`` now.
    - BUGFIX (minor): Serializing of CSSStyleDeclaration did not work well when CSSComments were mixed with Properties.


0.9.1b1
    - FUTURE CHANGE: ``readonly`` will be removed from most rules. It is not used anyway, may be readded in a future release

    - CHANGE: order of constructor parameters changed in ``CSSImportRule``. Should be no problem as positional parameters are discouraged anyway
    - CHANGE: cssutils needs Python 2.4 from the release on as it uses the buildin ``set``
    - CHANGE: removed ``CSSMediaRule.addRule`` which was deprecated anyway

    - FEATURE: implemented @page CSSRule including testcases
    - FEATURE: implemented @namespace CSSRule according to http://www.w3.org/TR/2006/WD-css3-namespace-20060828/ with the following changes
        * the url() syntax is not implemented as it may (?) be deprecated anyway
        * added namespace parsing to ``Selector``, see http://www.w3.org/TR/css3-selectors/
        * CSSStyleSheet checks if all namespaces in CSSStyleRules have been declared with CSSNamespaceRules. If not the rule's ``valid`` property is set to ``False`` and the serializer omits it (you may change ``Preferences.removeInvalid`` to change this behaviour).
        * CSSStyleSheet and Selector object have a new propery ``namespaces`` which currently contain declared and used namespace prefixes (!), this may change in the future so use with care if at all.
    - FEATURE: implemented ``CSSRule.parentStyleSheet`` for all rules
    - FEATURE: implemented ``CSSRule.parentRule`` for relevant rules (all allowed in @media)

    - BUGFIX: Set ``parentStyleSheet`` and ``parentRule`` as instance vars in ``css.CSSRule`` instead as class vars
    - BUGFIX: CSSComment raised exception if setting cssText with empty string - fixed

    - DOCS: generated docs with epydoc which are then included in src dist. Source documentation is cleaned up a bit.

    - INTERNAL: Refactored some unittests
    - INTERNAL: implementation based on `DOM Level 2 Style Recommendation <http://www.w3.org/TR/2000/REC-DOM-Level-2-Style-20001113/>`_ as opposed to the `Proposed Recommendation <http://www.w3.org/TR/2000/PR-DOM-Level-2-Style-20000927/>`_ now. As there are no main changes I could find this does not make any difference...


0.9.1a1
    - CHANGE, renamed ``Serializer.prefs.srcatkeyword`` to ``Serializer.prefs.normalkeyword``
      which work just the other way round but work as ``Serializer.prefs.normalpropertyname``

    - BUGFIX in css.Selector and added support regarding handling of pseudoclasses (``:x`` or ``:x()``) and pseudoelements ``::x``

    - BUGFIX and refactoring in tokenizer, mostly regarding escape sequences
        * combination of \ and NEWLINE in a string is removed according to spec now

    - added ``Serializer.prefs.normalpropertyname``, if True, property names are normalized if known (``color``), else literal form from CSS src is used (e.g. ``c\olor``). Defaults to ``True``.
    - removed ``Token.literal`` which value is in ``value`` now, normalized value is in ``normalvalue``
    - removed ``Token.ESCAPE``. Escapes are contained in IDENTifiers now.
    - internal change: WS is generally kept by tokenizer now, former normalized value ``u' '`` is hold in ``Token.normalvalue``. Serializer does not use it yet and some classes (like Selector) use normalvalue.

      uses normalized form of @keyword in source CSS if ``True`` (e.g. ``@import``), else literal form in CSS sourcefile (e.g. ``@i\mport``). Defaults to ``True``.



0.9a6
    - NEW ``Serializer.prefs.keepcomments`` removes all comments if ``False``, defaults to ``True``

    - NEW ``Serializer.prefs.srcatkeyword`` UPDATE see 9.91a1

    - fixed tokenizer to handle at least simple escapes like ``c\olor`` which is the same as ``color``. The original value is preserved but not used yet except in CSSComments which preserve the original values. See also Serializer.prefs.srcatkeywords

    - ``CSSMediaRule`` tested and lots of bugfixes
        * constructor has **no** parameters anymore (``mediaText`` is removed!)
        * ``addRule`` is DEPRECATED, use ``insertRule(rule)`` with no index instead.
          Synchronized with ``CSSStyleSheet.insertRule``

    - setting of ``CSSImportRule.media`` removed, use methods of this object directly.
      Synchronized with ``CSSMediaRule.media``

    - ``CSSStyleSheet.insertRule`` raises ``xml.dom.IndexSizeErr`` if an invalid index is given. Index may be ``None`` in which case the rule will be appended.
        Synchronized with ``CSSMediaRule.insertRule``

    - CSSStyleDeclaration bugfixes in parsing invalid tokens
    - stylesheets.MediaList bugfixes in parsing uppercase media values like ``PRINT``
    - added more unittests (CSSMediaRule)
    - various bugfixes


0.9a5 061015
    - reimplemented property validator:
        - for unknown CSS2 Properties a INFO message is logged
        - for invalid CSS2 Property values a WARNING message is issued

    - atrules have a new property ``atkeyword`` which is the keyword used in the CSS provided. Normally something like "@import" but may also be an escaped version like "@im\port" or a custom one used in CSSUnknownRule.

    - tokenizer and css.selector.Selector
        - added CSS3 combinator ``~``
        - added CSS3 attribute selectors ``^=``, ``$=``, ``*=``
        - added CSS3 pseudo selector ``::`` and pseudo-functions like ``:lang(fr)``

    - Token
        - added some new constants mainly replacing DELIM, e.g. UNIVERSAL, GREATER, PLUS, TILDE

        (CSS3 see http://www.w3.org/TR/css3-selectors)

    - Improved parsing of "Unexpected end of string" according to spec
    - fixed serializing of CSSUnknownRule if ``valid == False``

    - Properties may also be set with a numeric value now, before everything had to be a string. Direct use of _Property is discouraged though as it may well be changed again in a future version.

0.9a4 060927
    - CSSStyleSheet:
        - removed init parameter ``type`` which is now set as a static type to "text/css"
        - removed ``addRule`` which emits DeprecationWarning now
          Use ``insertRule`` without parameter ``index``
        - added new methods ``setSerializer(cssserializer)`` and
          ``setSerializerPref(self, pref, value)`` to control output
          of a stylesheet directly.

    - CSSStyleRule:
        - new property ``selectorList`` is an instance of SelectorList
          which contains a list of all Selector elements of the rule
        - removed ``addSelector()`` and ``getSelectors()``,
          use property ``selectorList`` instead
        - removed ``getStyleDeclaration()`` and ``setStyleDeclaration()``,
          use property ``style`` instead

    - CSSStyleDeclaration:
        - new constructor parameter ``cssText``

    - moved ``SelectorList``, ``Selector`` and ``Property`` to own modules.
      Should not be used directly yet anyway.

    - Token: renamed ``IMPORTANT`` to ``IMPORTANT_SYM``

    - unittests:
        - added tests for CSSStyleSheet, CSSStyleRule, SelectorList, Selector
          CSSStyleDeclaration, _Property

0.9a3 - 060909
    - refined EasyInstall (still some issues to be done)
    - CSSCharsetRule serialized and parsed according to spec only as ``@charset "ENCODING";`` so no comments allowed, only one space before encoding string which MUST use ``"`` as delimiter (see http://www.w3.org/TR/CSS21/syndata.html#q23)
        NOT COMPLETE YET, E.G. BOM HANDLING

    - added tests for setting empty cssText for all @rules and CSSStyleRule
    - bugfixes
        - CSSStyleDeclaration: Of two Properties if written directly after another``a:1;b:2`` one was swallowed
    - CSSSerializer:
        added new class cssutils.serialize.Preferences to control output or CSSSerializer

0.9a2 - 060908
    - using setuptools for deployment
        - new script ``cssparse`` which pprints css "filename"

    - subpackages ``css`` and ``stylesheets`` are directly available from ``cssutils`` now
    - renamed module ``cssutils.cssparser`` to ``cssutils.parse`` which should not be used directly anyway. Always use ``cssutils.CSSParser`` or ``cssutils.parse`` (s.b)
    - added utility functions ``parse(cssText)`` and ``parse(filename, encoding='utf-8')`` to cssutils main package which work like the CSSParser functions with the same name and API
    - return value of ``.cssText`` is ``u''`` and not ``None`` if empty now

    - serializing
        - cssutils.Serializer renamed to cssutils.CSSSerializer to improve usage of
           ``from cssutils import *``
        - cssutils has a property "ser" which is used by all classes to serialize themselves
          it is definable with a custom instance of cssutils.Serializer by setting
          cssutils.setCSSSerializer(newserializer)

        - prefs['CSSImportrule.href format'] may be set to
            - 'uri': renders url(...) (default)
            - 'string': renders "..."
            - None: renders as set in CSSImportRule.hreftype

    - css.CSSCharsetRule:
        - improved parsing
        - fixed API handling (setting of encoding did not work)

    - css.CSSImportRule:
        - improved parsing

    - usage of \*.getFormatted emits DeprecationWarning now and returns \*.cssText

    - lots of bugfixes and refactoring of modules, classes
    - extension and refactoring of unittests

0.9a1 - 060905
    - new tokenizer, complete rewrite
        * parses strings and comments
        * parses unicode escape sequences (see following)
        * emits CSS tokens according to spec (update: not all yet (ESCAPE)!)

    - renamed module "comment" to "csscomment" and class "Comment" to "CSSComment"
    - configurable Serializer instead of pprint
    - reimplemented CSSMediaRule

----

0.8a6 - 050827
    - bugfixes in valuevalidator regarding values of "background-position", thanks to Tim Gerla!

0.8a5 - 050824
    - bugfix in css.Comment: if constructor was called with empty or no cssText an exception was raised, reported by Tim Gerla!
    - prepared inline comments run through epydoc and generated API docs

0.8a4 - 050814
    - csscapture.py
        * does download linked, inline and @imported stylesheets now
        * renamed csscapture.Capture to csscapture.CSSCapture
        * added options, use ``csspapture.py -h`` to view all options
    - cssutils.css.CSSStyleSheet defines ``literalCssText`` property if property
      ``cssText`` is set. This is the unparsed cssText and might be different to cssText
      e.g. in case of parser errors.

0.8a3 - 050813
    - custom log for CSSparser should work again
    - calling script cssparser has 2 new options (not using optparse yet...)
        cssparser.py filename.css [encoding[, "debug"]]
        1. encoding of the filename.css to parse
        2. if called with "debug" debugging mode is enabled and default log prints all messages

    - cssutils.css.CSSUnknownRule reintegrated and Tests added
    - cssutils.Comment reintegrated
        implements css.CSSRule, there a new typevalue COMMENT (=-1) is added
    - lexer does handle strings *almost* right now...
    - bugfixes
    - simplified lexer, still lots of simplification todo

0.8a2 - 050731
    - CSSParser may now directly be used from cssutils
      cssutils.cssparser as a standalone script does work too.
    - css.CSSStyleDeclaration.getPropertyCSSValue(name) implemented
    - css.CSSValue updated
    - xml.dom.InvalidModificationErr now raised by CSSRule subclasses instead of xml.dom.SyntaxErr in case a non expected rule has been tried to set
    - test are updated to the new API and work (not complete and exhaustive though but a bit more than for 0.61)
    - bugfixes in some classes due to reanimated tests
    - moved module valuevalidator from cssutils.css to cssutils.
      Should not be used directly anyway
    - split CSSParser in actual CSSParser and utility module used by CSSParser and each css class cssText setting method
    - loghandler.ErrorHandler does raiseExceptions by default now. Only CSSParser does overwrite this behaviour. Some tests still need to be looked into...


0.8a1 - 050730
    bugfix medialist
        medium "projection" was spelled wrong (ended with a space)

    docs
        new examples and new structure on the website

    NEW API **INCOMPATIBLE API CHANGES**
        * new package cssutils.css which contains CSS interface implementations (css.CSSStyleSheet, css.CSSRuleList etc)
        * new package cssutils.stylesheets which contains Stylesheets interface implementations are in (stylesheets.StyleSheet, stylesheets.MediaList etc)
        * module cssutils.cssbuilder has therefor been removed and is replaced by packages cssutils.css and cssutils.stylesheets.
          (You may like to define your own cssbuilder module which imports all new classes with their old name if you do not want to change all your code at this time. Usage of the new names is recommended however and there are more subtle changes.)
        * CSS interfaces use W3 DOM names normally starting with CSS... now (e.g. CSSStyleSheet)
        * CSSStyleSheet now uses superclass stylesheets.StyleSheet
        * CSSImportRule is changed to comply to its specification (MediaList is after the URI and not before)
        * CSSFontfaceRule (cssutils FontfaceRule) is removed as CSS 2.1 removed this @ rule completely
        * CSSProperties is removed. Properties are useful in CSSStyleDeclaration only anyway and are used through that class now.
        * some parameters have been renamed to their respective DOM names (e.g. selector is selectorText now in CSSStyleRule constructor
        * the API has been cleaned up a bit. Some redundant methods have been removed.
            - cssmediarule: removed  getRules(), use cssRules property instead

        * Comment as a rule is removed currently, might be reintegrated in a future version.
        * some classes which have not been implemented fully anyway are not available until they are finished. This is mainly CSSMediaRule (will follow shortly), CSSUnknownRule, CSSValue and other value classes.

----

0.61 - 050604
    bugfix reported and fixed thanks to Matt Harrison:
        'border-left-width' property was missing from cssvalues.py

0.60b
    tiny internal changes

0.60a
    added modules to validate Properties and Values
    thanks to Kevin D. Smith

    MediaList renamed media type "speech" to "aural"

0.55_52 - 040517 bugfix bugfix release
    should do test first ;)
    added unittest and fix for fix

0.55_51 - 040517 bugfix release
    cssstylesheet.StyleSheet _pprint was renamed to _getCssText but
    the call in pprint was not changed...

0.55_5 - 040509
    API CHANGES

    StyleDeclaration
        addProperty made/named private
        DEPRECATED anyway, use setProperty

        parentRule raises NotImplementedError

    RGBColor Implemented
    PrimitiveValue uses RGBColor

    CSSParser uses setProperty instead of addProperty now
    StyleDeclaration, Value, ValueList, PrimitiveValue, RGBcolor
    done comparing spec and module docstrings

    made list of TODOs

0.55_4 - 040502
    implement \*Rule.cssText setting (UnknownRule not complete)

    lexer has no log anymore, simply "logs" everything to the
    resulting tokenlist

    cssstylesheet simplified

    bugfixes

0.55_3 not released
    cssnormalizer renamed, does not work anyway at the moment

    implemented StyleRule.cssText setting

    cssproperties.Property has new init param raiseExceptions
    similar to the one of CSSParser. does not log yet
    and functionality might change as well
    * what will not change is that you can specify not
    officially specified properties (like moz-opacity etc)

    some cleanup in various classes

0.55_2 not released
    tests only

0.55_1 not released
    API CHANGES
        CSSFontFaceRule and CSSPageRule
        style is readonly now

    NEW
        CSSRule
        implementation cssText setting
        improved docstrings

    CSSCharsetRule, CSSFontFaceRule, CSSFontFaceRule, CSSImportRule, CSSSMediaRule, CSSPageRule, CSSStyleRule, CSSUnknownRule
        use CSSRule implementation
    CSSCharsetRule
        uses codecs module to check if valid encoding given
    CSSImportRule
        new property styleSheet, always None for now

    simplified and cleaned up sources
    some bugfixes

    added tests
        test_cssrule
        test_csscharsetrule, test_cssfontfacerule, test_cssimportrule,

        test_mediarule, test_stylesheetrule, test_unknownrule
            subclass test_cssrule now
    improved unittests
        test_cssstylesheet import problem removed

0.55b not released
    start implementation StyleRule.cssText setting

0.54 not released
    API CHANGES
        Comment.cssText contains comment delimiter
        attribute text of Comment private now, renamed to _text
        ALPHA new StyleSheet.cssText property (not in W3C DOM)

    BUG FIXES
        Commentable checked only for str, not unicode. now both
        Parser did not raises all errors, might still not do (s. a.)

    added unittest for __init__ module

0.53 - 040418
    !cssnormalizer does not work in this version - on hold for 1.0

    new cssunknownrule.UnknownRule (moved out of module cssrule)
    parser now creates Unknown At-Rules in the resulting StyleSheet. they
    are no longer just dumped and reported in the parser log.

0.52 - 040414
    !cssnormalizer does not work in this version - on hold for 1.0

    whitespace in comments will be preserved now
        added unittest

0.51 - 040412
    !cssnormalizer does not work in this version - on hold for 1.0

    API CHANGES
    cssrule.SimpleAtRule DEPRECATED and empty
    cssmediarule.MediaRule init param "medias" renamed to "media"
    use subclasses of CSSRule (CharsetRule, ImportRule,
    FontFaceRule or PageRule) instead
    StyleRule constructor can be called with arguments (again...)
    Comment attribute "comment" renamed to "text"

    implemented at least partly almost all DOM Level 2 CSS interfaces now
    so the API should be more stable from now on

    new statemachine and lexer helper classes for parsing
    complete rewrite of CSSParser
    CSSParser and lexer put all error messages in a log now
    you might give your own log for messages
    CSSParser might be configured just to log errors or to raise
    xml.dom.DOMExceptions when finding an error

0.41 - 040328
    !cssnormalizer does not work in this version - on hold for 1.0

    API CHANGES
    StyleSheet.getRules() returns a RuleList now
    class Selector removed, integrated into Rules now

    moved most Classes to own module
        StyleSheet, StyleRule, MediaRule, ...

0.40a - 040321
    !cssnormalizer does not work in this version

    API CHANGES:
    cssbuilder.RuleList subclasses list
    cssbuilder.Selector moved to cssrules
    attribute style of class StyleRule made private (_style)
    removed StyleRule.clearStyleDeclaration
    attribute selectorlist of class Selector renamed to _selectors and made private

    NEW:
    MediaList class

    moved tests to directory test

    made a dist package complete with setup.py


0.31 - 040320
    !cssnormalizer does not work in this version

    API CHANGES:
    StyleDeclaration.addProperty is now DEPRECATED
    use StyleDeclaration.setProperty instead

    removed CSSParser.pprint(). use CSSParser.getStyleSheet().pprint() instead
        (a StyleSheet object had a pprint method anyway)

    replaced cssutils own exceptions with standard xml.dom.DOMException
        and subclasses
        !catch these exceptions instead of CSSException or CSSParserException

    moved internal lists (e.g. StyleSheet.nodes list) to private vars
        StyleSheet._nodes
        !please use methods instead of implementation details


    removed cssexception module
    removed csscomment module, classes now directly in cssutils

    more unittests, start with python cssutils/_test.py

    more docs

    integrated patches by Cory Dodt for SGML comments and Declaration additions
    added some w3c DOM methods


0.30b - 040216
    severe API changes
    renamed some classes to (almost) DOM names, the CSS prefix of DOM names is ommited though

    renamed are
        - Stylesheet TO StyleSheet
        - Rule TO StyleRule
        - AtMediaRule TO MediaRule
        - Declaration TO StyleDeclaration

    the according methods are renamed as well

    class hierarchy is changed as well, please see the example

    classes are organized in new modules


0.24_1 - 040214
    legal stuff: added licensing information
    no files released

0.24 - 040111
    split classes in modules, has to be cleaned up again

0.24b - 040106
    cleaned up cssbuilder
        - Comment now may only contain text
            and no comment end delimiter.
            (before it had to be a complete css
            comment including delimiters)
        - AtMediaRule revised completely
            validates given media types
            new method: addMediaType(media_type)

    cssparser updated to new cssbuilder interface and logic
    started unittests (v0.0.0.1..., not included yet)


0.23 - 031228
    new CSSNormalizer.normalizeDeclarationOrder(stylesheet)

    cssbuilder: added methods needed by CSSNormalizer

    CSSParser.parse bugfix


0.22 - 031226
    CSSParser:
            added \n for a declaration ending in addition to ; and }
    cssbuilder:
        docstrings added for @import and @charset
        support build of a selector list in a rule


0.21 - 031226
    cleaned up docstrings and added version information

0.20 - 031224
    complete rewrite with combination of parser and builder classes

0.10 - 031221
    first version to try if i can bring it to work at all
    only a prettyprinter included, no builder

