#!/usr/bin/env python


"""
Code and Configuration Comments Regular Expressions
"""


import re


__version__ = '0.0.0'


#=============================================================================
# Utility Pattern Fragments

quotes = '"\'`'
whites = ' \t\r\n'

patterns = {

    # double-quoted string (with potentially escaped double quotes inside)
    'dqs' : r'"[^"\\\r\n]*(?:\\.[^"\\\r\n]*)*"',

    # double-, single-, and backtick-quoted strings
    'mqs' : r'[{0}][^{0}\\\r\n]*(?:\\.[^{0}\\\r\n]*)*[{0}]'.format( quotes ),

    # C-style, multiline comments
    'csc' : r'/\*(?:.|[\r\n])*?\*/',

    # C++- and shell-style comments
    'ssc' : r'(?://|#).*$',

    # allow string formatting easy access to these
    'quotes' : quotes,
    'whites' : whites
}

#=============================================================================
# The Comment Stripping Pattern

_pattern = '({mqs})|[{whites}]?{csc}[{whites}]?|{ssc}'.format( **patterns )


#=============================================================================
# Test Cases : [ input, expected ]

test_cases = [

    # no comments, just multiple lines
    [
        """a string with no
comments, but
multiple lines""",
        """a string with no
comments, but
multiple lines"""
    ],

    # shell comment
    [
        """a string with
# a shell-style comment
and multiple lines""",
        """a string with

and multiple lines"""
    ],

    # all comments on all lines
    [
        """# a string
# that is all
# shell comments""",
        '\n\n'
    ],

    # mixed comments
    [
        """# a string
// with a mixture
/* of comment types */""",
        '\n\n'
    ],

    # mixed comments with nested comment symbols
    [
        """# a string /* with */
/* messed up // comments */
and one real part /* with comments */
and a trailing # comment""",
        """

and one real part 
and a trailing """
    ],

    # valid tokens, artificial/injected separation
    [ 'a/* AB */b', 'a b' ],

    # multiple lines inside comment
    [ 'a /* A\nB */ b', 'a  b' ],

    # asterisk inside comment
    [ 'a /* A*B */ b', 'a  b' ],

    # island tokens between comments
    [ 'a /* AB */ b /* CD */ c', 'a  b  c' ],

    # multiple asterisks
    [ 'a /** A ** B **/ b', 'a  b' ],

    # shell-style comment in a quoted string
    [
        'a "quoted # comment" character',
        'a "quoted # comment" character'
    ],

    # C++-style comment in a quoted string
    [
        'another "inside // quotes"',
        'another "inside // quotes"'
    ],

    # C-style comment in a single-quoted string
    [
        "the 'other /* style */ of' quotes",
        "the 'other /* style */ of' quotes"
    ]

]


#=============================================================================
def _replacer( match ):
    """
    Replacement function for `re.sub()` callbacks.

    @param match The MatchObject instance for the current match
    @return      The string to use in place of the current match
    """

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
    if g0[ 0 ] in whites:
        replace += g0[ 0 ]
    if g0[ -1 ] in whites:
        replace += g0[ -1 ]
    return replace


#=============================================================================
def print_multiline( left, right ):
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
    print bar
    fmt = '|{{:{0}}}|{{:{0}}}|'.format( max_line )
    for left_line, right_line in zip( l_lines, r_lines ):
        print fmt.format( left_line, right_line )
    print bar


#=============================================================================
def run_tests():
    """
    Runs each test case through each test pattern providing feedback on what
    works, and how well.
    """

    # count the number of failures
    failures = 0

    # iterate through each test case
    test_case_offset = 0
    for string, expected in test_cases:

        # strip the comments using the current pattern
        actual = re.sub(
            _pattern,
            _replacer,
            string,
            flags = re.MULTILINE
        )

        # display the results
        print_multiline( string, actual )

        # test the results
        if actual == expected:
            print 'PASSED test case #{}'.format( test_case_offset )
        else:
            print 'FAILED test case #{}'.format( test_case_offset )
            failures += 1

        # increment to next test case
        test_case_offset += 1

    # display complete test result
    if failures == 0:
        print '*** All Tests PASSED ***'
    else:
        print '*** {} Tests FAILED ***'.format( failures )

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
    return run_tests()


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )

