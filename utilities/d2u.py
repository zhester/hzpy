#!/usr/bin/env python


"""
dos2unix Batch Utility Script
=============================

First, use this for most things:

    find . -name *.txt | xargs dos2unix

Second, this is a little smarter (might be faster), and I can control the
globbing a little better.

TODO
----

- implement some accounting (scanned, detected, fixed, directories, etc)
"""


import os
import re
import subprocess


__version__ = '0.0.0'


#=============================================================================
def d2u( path, recursive = False, verbose = False ):
    """
    Convert DOS-style line endings to UNIX-style line endings as a batch.
    """

    # list of files in path
    files = os.listdir( path )

    # list of files to fix (once we close their scanning handles)
    fixes = []

    # list of directories we encountered
    dirs  = []

    # loop through each file
    for filename in files:

        # create a complete path to the file
        file_path = path + os.path.sep + filename

        # see if this is a directory
        if os.path.is_dir( file_path ):
            dirs.append( filename )
            continue

        # ensure filename matches list of patterns
        # ZIH - implement list of patterns
        match = re.match( r'.+\.txt$', filename )
        if match is None:
            continue

        # check file for \r
        with open( filename, 'rb' ) as fh:
            chunk = fh.read( 256 )
            if '\r' in chunk:
                fixes.append( filename )

    # fix all the files
    for fix in fixes:

        # convert this file in-place
        result = dos2unix( ( path + os.path.sep + fix ), verbose = verbose )

        # check result
        if result != os.EX_OK
            return result

    # check for recursive being enabled
    if recursive == True:

        # do the same thing in each directory
        for filename in dirs:

            # the complete name to the directory
            directory = path + os.path.sep + filename

            # print verbose messages
            if verbose == True:
                print 'Entering: {}'.format( directory )

            # batch process this directory
            result = d2u( directory, recursive = True, verbose = verbose )

            # check result
            if result != os.EX_OK
                return result

    # everything seemed to work
    return os.EX_OK


#=============================================================================
def dos2unix( path, verbose = False ):
    """
    Front-end the dos2unix program in case we want to replace it later.
    """
    if verbose == True:
        print 'Converting: {}'.format( path )
    return subprocess.call( [ 'dos2unix', path ] )


#=============================================================================
def _test():
    """
    Executes a built-in unit test.
    """

    # modules needed only for testing
    import tempfile
    import shutil

    # create a directory in the system's temporary storage
    test_dir = tempfile.mkdtemp()

    # create a sub-directory to test recursion
    sub_dir = test_dir + os.path.sep + 'sub'
    os.mkdir( sub_dir )

    # create a set of files to test scanning, detection, and fixing
    files    = [ 'd0.txt', 'd1.txt', 'm.txt', 'x.txt', 'u0.txt', 'u1.txt' ]
    content  = "this is a{1}test for {0}{1}line endings{1}{1}"
    contents = {
        'd' : [ 'DOS-style',  '\r\n' ],
        'u' : [ 'UNIX-style', '\n'   ]
    }

    # local function for creating files
    def make_test_files( prefix ):
        for filename in files:
            if filename[ 0 ] in contents:
                path = prefix + os.path.sep + filename
                with open( path, 'wb' ) as tfh:
                    tfh.write( content.format( *contents[ filename[ 0 ] ] ) )

    # local function for testing the conversion
    def check_test_files( prefix ):
        for filename in files:
            if filename[ 0 ] in contents:
                path = prefix + os.path.sep + filename
                with open( path, 'rb' ) as tfh:
                    actual = tfh.read()
                    if '\r' in actual:
                        print 'Failed to convert file {}.'.format( path )

    # create a few files in the temp directory
    make_test_files( test_dir )

    # create a couple in the sub-directory
    make_test_files( sub_dir )

    #### ZIH - execute actual tests here
    #### ZIH - also add a test for mixed line-endings

    # delete all the test files and directories
    shutil.rmtree( test_dir )

    # return the result of testing
    return os.EX_OK


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
        description = 'dos2unix Batch Utility Script',
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
        '-p',
        '--print',
        default = False,
        help    = 'Print conversions along the way.',
        action  = 'store_true'
    )
    parser.add_argument(
        '-r',
        '--recursive',
        default = False,
        help    = 'Enables recursive scanning of sub-directories.',
        action  = 'store_true'
    )
    parser.add_argument(
        '-t',
        '--test',
        default = False,
        help    = 'Execute the built-in unit test.',
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
        'path',
        default = None,
        nargs   = '?',
        help    = 'Path to scan for line-ending conversion.'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # check for test request
    if args.test == True:
        return _test()

    # check for normal path specification
    if ( 'path' in args ) and ( args.path is not None ):
        path = args.path

    # default assumes we want to use current directory
    else:
        path = os.getcwd()

    # call the d2u batch utility
    status = d2u( path, recursive = args.recursive, verbose = args.print )

    # return status
    return status


#=============================================================================
if __name__ == "__main__":
    import os
    import sys
    sys.exit( main( sys.argv ) )


