#!/usr/bin/env python


"""
Code and Configuration Comments Parsing and Stripping

This module is designed to make it easy to remove or retrieve comments from a
source file.  This is accomplished in a single pass using a relatively complex
regular expression.  The module provides two interface functions: `get()`
and `strip()`.

If the pattern itself is of interest, it is a visible property of the module:
`pattern`.
"""


import re


__version__ = '0.0.0'


#=============================================================================
# Language Comment Documentation

# list of single-line comment markers in various languages
single_line_comments = [
    '#', '//', ';', "'", '"', '--', 'REM', 'Rem', '::', '!', '%', '\\'
]
single_line_map = [
    ( 'shell', 'Perl', 'PHP', 'Python', 'conf', 'Apache', 'Ruby', 'Make',
      'Bash', 'Bourne Shell', 'C Shell', 'Tcl' ),
    ( 'C', 'C++', 'Java', 'PHP', 'JavaScript', 'ActionScript', 'ECMAScript' ),
    ( 'ini', 'Lisp', 'assembly' ),
    ( 'Visual Basic', 'VBScript' ),
    ( 'Vimscript' ),
    ( 'SQL', 'Haskell', 'Ada', 'Lua', 'VHDL', 'SGML' ),
    ( 'batch' ),
    ( 'batch', 'Visual Basic', 'VBScript' ),
    ( 'batch' ),
    ( 'Fortran 90' ),
    ( 'MATLAB' ),
    ( 'Forth' )
]

# list of multi-line comment markers in various languages
multi_line_comments = [
    '/*~*/', '<!-- ~ -->', '{-~-}', '%{\n~\n}%', '(*~*)', '=begin~=end',
    '=begin~=cut', '#|~|#', '--[[~]]', '--[[=[~]=]', '<#~#>'
]
multi_line_map = [
    ( 'C', 'C++', 'Java', 'JavaScript', 'PHP', 'SQL', 'CSS', 'Objective-C',
      'C#', 'ActionScript', 'ECMAScript' ),
    ( 'SGML', 'XML', 'HTML', 'XHTML' ),
    ( 'Haskell' ),
    ( 'MATLAB' ),
    ( 'Pascal', 'OCaml' ),
    ( 'Ruby' ),
    ( 'Perl' ),
    ( 'Lisp' ),
    ( 'Lua' ),
    ( 'Lua' ),
    ( 'Bash', 'Bourne Shell', 'C Shell', 'Tcl' )
]


#=============================================================================
# Utility Pattern Fragments

_quotes = '"\'`'
_whites = ' \t\r\n'
_missme = r'(?:(?!(?P=quote))|[^\\\r\n])'

_patterns = {

    # double-quoted string (with potentially escaped double quotes inside)
    'dqs' : r'"[^"\\\r\n]*(?:\\.[^"\\\r\n]*)*"',

    # single-quoted string (same as above)
    'sqs' : r"'[^'\\\r\n]*(?:\\.[^'\\\r\n]*)*'",

    # backtick-quoted string (same as above)
    'bqs' : r'`[^`\\\r\n]*(?:\\.[^`\\\r\n]*)*`',

    # double-, single-, and backtick-quoted strings
    #'mqs' : r'[{0}][^{0}\\\r\n]*(?:\\.[^{0}\\\r\n]*)*[{0}]'.format( _quotes ),
    'mqs' : r'(?P<quote>[{q}]){m}*(?:\\.{m}*)*(?P=quote)'.format(
        q = _quotes,
        m = _missme
    ),

    # C-style, multiline comments
    'csc' : r'/\*(?:.|[\r\n])*?\*/',

    # C++- and shell-style comments
    'ssc' : r'(?://|#).*$',

    # allow string formatting easy access to these
    'quotes' : _quotes,
    'whites' : _whites
}


#=============================================================================
# The Comment Stripping Pattern
#
# The strategy involves judiciously attempting to match string literals first.
# The two top-level alternatives are to match either a multi-line comment or a
# single-line comment (in that order).  The replacer or consumer of the match
# must then evaluate if the pattern matched a string by checking if the first
# subgroup has been populated.  If not, the (entire) pattern has matched a
# comment.
#
# This strategy allows us to protect the stripping system from nearly all
# conceivable (and valid) permutations of embedding string literals and
# comments.

_pattern = '({mqs})|[{whites}]?{csc}[{whites}]?|{ssc}'.format( **_patterns )


#=============================================================================
# The Compiled Pattern (for external users)

pattern = re.compile( _pattern, flags = re.MULTILINE )


#=============================================================================
# Test Cases : [ key, input, expected ]

_test_cases = [

    # no comments, just a line
    [ 'base-single', 'a b c', 'a b c' ],

    # no comments, just multiple lines
    [ 'base-multi', 'a\nb\nc', 'a\nb\nc' ],

    # multiple lines inside comment
    [ 'multi', 'a /* b\nc */ d', 'a  d' ],

    # shell comment
    [ 'shell', 'a\n# b\nc', 'a\n\nc' ],

    # all shell comments on all lines
    [ 'shell-all', '# a\n# b\n# c', '\n\n' ],

    # mixed comment styles on all lines
    [ 'mixed-all', '# a\n// b\n/* c */', '\n\n' ],

    # mixed comments with nested comment symbols
    [ 'mixed-emb',
      '# a /* b */\n/* c // d */\ne /* f */\ng # h',
      '\n\ne \ng ' ],

    # valid tokens, artificial/injected separation
    [ 'multi-inject', 'a/* b */c', 'a c' ],

    # asterisk inside comment
    [ 'multi-asterisk', 'a /* b*c */ d', 'a  d' ],

    # multiple asterisks
    [ 'multi-astersiks', 'a /** b ** c **/ d', 'a  d' ],

    # island tokens between comments
    [ 'multi-island', 'a /* b */ c /* d */ e', 'a  c  e' ],

    # shell-style comment in a quoted string
    [ 'str-emb-shell', 'a "b # c" d', 'a "b # c" d' ],

    # C++-style comment in a quoted string
    [ 'str-emb-c++', 'a "b // c" d', 'a "b // c" d' ],

    # C-style comment in a single-quoted string
    [ 'str-emb-c', "a 'b /* c */ d' e", "a 'b /* c */ d' e" ],

    # strings with embedded, but valid quotes
    [ 'str-emb-str', 'a "b \'c\' d" e', 'a "b \'c\' d" e' ],

    # strings with embedded comments
    [ 'str-emb-multi', 'a "b \'c\' /* d */ e" f', 'a "b \'c\' /* d */ e" f' ],

    # embedded string with embedded comments
    [ 'str-emb-str-multi',
      'a "b \'c /* d */\' e" f',
      'a "b \'c /* d */\' e" f' ],

    # invalid string delimiter
    [ 'str-invalid', 'a " # b', 'a " ' ],

    # comments with embedded strings
    [ 'shell-emb-str', 'a # b "c" d', 'a ' ],
    [ 'multi-emb-str', 'a /* b "c" */ d', 'a  d' ]

]


#=============================================================================
def get( string ):
    """
    Iteratively yields all comments from the given string.

    @param string A string from which all comments will be retrieved
    @yield        A string containing the current comment
    """

    # perform an iterative search on the subject string
    comments = re.finditer( _pattern, string, flags = re.MULTILINE )

    # iterate through matched patterns
    for comment in comments:

        # retrieve the complete match, and the first subgroup
        g0, g1 = comment.group( 0, 1 )

        # the first subgroup is from string literal matching.  if the subgroup
        # is populated, ignore it, and advance to the next match.  if the
        # subgroup is None, the entire pattern has matched a comment.
        if g1 is None:

            # yield this comment (optionally matched whitespace is removed)
            yield g0.strip()


#=============================================================================
def strip( string ):
    """
    Removes all comments from the given string.

    @param string A string from which all comments will be removed
    @return       A string with no comments
    """

    # run the regular expression against the subject string
    return re.sub( _pattern, _replacer, string, flags = re.MULTILINE )


#=============================================================================
def _replacer( match ):
    """
    Replacement function for `re.sub()` callbacks.

    @param match The MatchObject instance for the current match
    @return      The string to use in place of the current match
    """

    #print( '## Match:', match.group( 0 ), 'Groups:', match.groups() )

    # get the entire match string and the first subgroup
    g0, g1 = match.group( 0, 1 )

    # string literal was matched, do not remove it from the subject string
    if g1 is not None:
        return g1

    # C-style comments with no surrounding space are replaced with a space
    #   to allow "BEFORE/* ... */AFTER" to become "BEFORE AFTER"
    if g0.startswith( '/*' ) and g0.endswith( '*/' ):
        return ' '

    # restore optionally-matched surrounding whitespace characters
    replace = ''
    if g0[ 0 ] in _whites:
        replace += g0[ 0 ]
    if g0[ -1 ] in _whites:
        replace += g0[ -1 ]
    return replace


#=============================================================================
def _print_multiline( left, right ):
    """
    Prints a pair of multi-line strings side-by-side.

    @param left  The left-hand multi-line string
    @param right The right-hand multi-line string
    """
    l_lines   = left.split( '\n' )
    r_lines   = right.split( '\n' )
    nl_lines  = len( l_lines )
    nr_lines  = len( r_lines )
    num_lines = max( nl_lines, nr_lines )
    if nl_lines < num_lines:
        l_lines.extend( [ '' ] * ( num_lines - nl_lines ) )
    if nr_lines < num_lines:
        r_lines.extend( [ '' ] * ( num_lines - nr_lines ) )
    max_left  = max( len( line ) for line in l_lines )
    max_right = max( len( line ) for line in r_lines )
    max_line  = max( max_left, max_right )
    box_bar   = '-' * max_line
    bar       = '+{0}+{0}+'.format( box_bar )
    print( bar )
    fmt = '|{{:{0}}}|{{:{0}}}|'.format( max_line )
    for left_line, right_line in zip( l_lines, r_lines ):
        print( fmt.format( left_line, right_line ) )
    print( bar )


#=============================================================================
def _run_tests( run ):
    """
    Runs each test case (for a selected test target) through each test pattern
    providing feedback on what works, and how well.

    @param run The test target to execute (strip or get)
    @return    The result of test execution (0 = success)
    """

    # count the number of failures
    failures = 0

    # get testing
    if ( run == 'all' ) or ( run == 'get' ):

        # example of various styles of comments
        case = """a
//b
c
#d
e
f /* g */ h
/*
 * i j
 * k l
 */
m"""

        # this should be the resulting list of comments
        expected = [ '//b', '#d', '/* g */', '/*\n * i j\n * k l\n */' ]

        # fetch the comments all at once (not a typical usage pattern)
        actual = list( get( case ) )

        # check what was retrieved
        if actual == expected:
            print 'PASSED get test "mixed"'
        else:
            print 'FAILED get test "mixed"'
            print 'Expected:', expected
            print 'Actual  :', actual
            failures += 1

    # strip testing
    if ( run == 'all' ) or ( run == 'strip' ):

        # iterate through each test case
        for key, string, expected in _test_cases:

            # strip the comments
            actual = strip( string )

            # test the results
            if actual == expected:
                print( 'PASSED strip test "{}"'.format( key ) )
            else:
                print( 'FAILED strip test "{}"'.format( key ) )
                _print_multiline( string, actual )
                failures += 1

    # display complete test result
    if failures == 0:
        print( '*** All Tests PASSED ***' )
    else:
        print( '*** {} Tests FAILED ***'.format( failures ) )

    # return test status
    return 0 if failures == 0 else 1


#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv List of arguments passed to the script
    @return     Shell exit code (0 = success)
    """

    # imports when using this as a script
    import argparse

    # create and configure an argument parser
    parser = argparse.ArgumentParser(
        description = 'Code and Configuration Comments Regular Expressions',
        add_help    = False
    )
    parser.add_argument(
        '-h',
        '--help',
        default = False,
        help    = 'Display this help message and exit.',
        action  = 'help'
    )
    parser.add_argument(
        '-r',
        '--run',
        default = 'all',
        help    = 'Specify the test to execute (all, get, or strip).',
        nargs   = '?'
    )
    parser.add_argument(
        '-v',
        '--version',
        default = False,
        help    = 'Display script version and exit.',
        action  = 'version',
        version = __version__
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # run all the tests, and return status to shell
    return _run_tests( args.run )


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )

