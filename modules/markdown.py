#!/usr/bin/env python


"""
Markdown Parser Module
"""


__version__ = '0.0.0'



#=============================================================================
def convert_files( target, source, target_format = None ):
    """
    Converts a Markdown file into another format.  The target format is
    determined by the target file name's extension, or if it is explicitly
    given in the optional argument.  The target format is specified by file
    name extension string (e.g. `html`).

    Current list of supported target formats:
    - html
    """
    pass


#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv         Arguments passed to the script
    @return             Exit code (0 = success)
    """

    # imports when using this as a script
    import argparse

    # create and configure an argument parser
    parser = argparse.ArgumentParser(
        description = 'Markdown Parser Module',
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
        '-t',
        '--test',
        default = False,
        help    = 'Run all internal unit tests.',
        action  = 'store_true'
    )
    parser.add_argument(
        '-v',
        '--version',
        default = False,
        help    = 'Display script version and exit.',
        action  = 'version',
        version = __version__
    )
    parser.add_argument(
        'source',
        default = None,
        nargs   = '?',
        help    = 'Markdown document to convert.'
    )
    parser.add_argument(
        'target',
        default = None,
        nargs   = '?',
        help    = 'Conversion output document.'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # check for running the built-in unit tests
    if ( 'test' in args ) and ( args.test == True ):
        test_result = _test( argv[ 2 : ] )
        return os.EX_OK if test_result == True else os.EX_SOFTWARE

    # assume we are using the module to convert a document
    result = convert_files( args.target, args.source )

    # return result of convertion
    if result == True:
        return os.EX_OK
    return os.EX_SOFTWARE


#=============================================================================
if __name__ == "__main__":
    import os
    import sys
    sys.exit( main( sys.argv ) )


