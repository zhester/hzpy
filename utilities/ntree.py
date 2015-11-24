#!/usr/bin/env python
##############################################################################
#
# Normalize a Directory Tree Structure
#
##############################################################################

"""
Normalize Tree

This is used to clean up directories that are typically created either by
hand (without knowledge of odd characters in paths), or by automated scripts
that tend to "pack" a lot of information into a file name that may have
unusual formatting.

Call the script using the `--help` argument for usage information.

A simple, complete tree normalization is done with:
    ./ntree.py -fr path/to/odd\ directory\ name

By default, this does *not* attempt to rename files.  Use `-f` to also
normalize file names.

By default, this does *not* attempt to rename the given directory (allowing
you to use it from inside the "current" directory).  Use `-r` to also
normalize the given directory name (may not work if you are "in" that
directory).
"""


import os
import re
import sys


__version__ = '0.0.0'


#=============================================================================
def mktest( path ):
    """
    Builds a test directory structure inside the given path.

    @param path The parent of the new test directory
    """

    # simple tree structure for testing purposes
    tree = {
        'root' : {
            'branch0' : { 'leaf0a.ext' : None, 'leaf0b.ext' : None },
            'branch1' : { 'leaf1a.ext' : None },
            'branch2' : {},
        }
    }

    # messes up a file or directory name, but is still valid
    def mung( name ):
        split = len( name ) // 2
        n0    = name[ : split ]
        n1    = name[ split : ]
        return '__- {}, {} ( 0 ) & 42 '.format( n0, n1 )

    # creates the directory tree under the given prefix
    def mktree( prefix, tree ):
        for k, v in tree.items():
            path = os.path.join( prefix, mung( k ) )
            if v is None:
                open( path, 'w' ).close()
            else:
                try:
                    os.mkdir( path )
                except OSError as ose:
                    if ose.errno != 17:
                        break
                mktree( path, v )

    # creates the new directory tree on the disk
    mktree( path, tree )


#=============================================================================
def nnode( path, name = None, dry = False, verbose = False ):
    """
    Normalize leaf node at the given path.

    TODO:
    - attempt to re-use possible trailing digits on old names

    @param path The path to normalize
    @param name Optional node name to normalize *after* the path
    @param dry  Set to prevent the rename (just announces new names)
    @return     True if the node was renamed, otherwise False
    """

    # check for need to break off the basename
    if name is None:
        npath = path
        name  = os.path.basename( path )
        path  = os.path.dirname( path )
    else:
        npath = os.path.join( path, name )

    # construct a new name for this node
    nslug   = slug( name )
    newname = os.path.join( path, nslug )

    # diagnostic feedback
    if verbose == True:
        print( '  >> normalizing "{}"'.format( npath ) )

    # see if this node already appears normalized
    if npath == newname:
        if verbose == True:
            print( '  >> already normalized'.format( npath ) )
        return False

    # make sure the new name does not conflict with an existing name
    attempt = 0
    while os.path.exists( newname ):
        if verbose == True:
            print( '  >> "{}" conflicts'.format( newname ) )
        newname = os.path.join( path, '{}{:02}'.format( nslug, attempt ) )
        attempt += 1

    # announce the change
    print( 'renaming "{}" to "{}"'.format( npath, newname ) )

    # check for a dry run
    if dry == True:
        return False

    # rename the node to normalize it
    os.rename( npath, newname )
    return True


#=============================================================================
def ntree( path, files = False, root = False, verbose = False ):
    """
    Normalize Directory Tree

    @param path    The path from which to begin normalization
    @param files   Set to enable normalizing file names
    @param root    Set to also normalize root of the given tree
    @param verbose Set to enable more verbose output
    @return      0 on success
    """

    # test to make sure we can begin normalization
    if os.path.exists( path ) == False:
        print( '"{}" does not exist'.format( path ) )
        return 1

    # walk the directory tree starting at the leaves
    for prefix, dirs, leaves in os.walk( path, topdown = False ):

        # see if the user wishes to also rename files
        if files == True:

            # check/rename all files as needed
            for name in leaves:
                nnode( prefix, name, verbose = verbose )

        # check/rename all directories as needed
        for name in dirs:
            nnode( prefix, name, verbose = verbose )

    # check for root normalization
    if root == True:
        nnode( os.path.realpath( path ), verbose = verbose )

    # return success
    return 0


#=============================================================================
def slug( string, flags = 0 ):
    """
    Attempts to convert a string into a safe "slug" string.

    @param string The string to convert into a slug
    @param flags  Optional behavior flags
                    1: lowercase all uppercase letters
                    2: use hyphens (instead of underscores) as separators
                    4: convert periods to separators
    @return       A "slugged" version of the given string
    """

    # check for hyphen substitution
    ssub = '-' if flags & 2 else '_'

    # strip exterior whitespace
    string = string.strip()

    # remove all undesired characters
    string = re.sub( r'[^a-zA-Z0-9 ._-]', '', string )

    # check for period conversion
    if flags & 3:
        string = string.replace( '.', '' )

    # convert spaces to separators
    string = string.replace( ' ', ssub )

    # remove obnoxious results
    string = string.replace( '_-', ssub )
    string = string.replace( '-_', ssub )

    # collapse repeated substitutions
    string = re.sub( ssub + '+', ssub, string )

    # check for lower-casing
    if flags & 1:
        string = string.lower()

    # return the converted string
    return string


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
        description = 'Normalize Tree',
        add_help    = False
    )
    parser.add_argument(
        '-d',
        '--diagnose',
        default = False,
        help    = 'Provides more output for diagnostic purposes.',
        action  = 'store_true'
    )
    parser.add_argument(
        '-f',
        '--files',
        default = False,
        help    = 'Rename files in addition to directories.',
        action  = 'store_true'
    )
    parser.add_argument(
        '-h',
        '--help',
        default = False,
        help    = 'Display this help message and exit.',
        action  = 'help'
    )
    parser.add_argument(
        '-m',
        '--maketest',
        default = False,
        help    = 'Invoke to build a test directory tree.',
        action  = 'store_true'
    )
    parser.add_argument(
        '-r',
        '--root',
        default = False,
        help    = 'Include root of tree in normalization.',
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
        default = '.',
        nargs   = '?',
        help    = 'Path from which to begin normalization.'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # check for test tree generation
    if args.maketest == True:
        mktest( args.path )
        return 0

    # normalize from the given path
    return ntree( args.path, args.files, args.root, args.diagnose )


#=============================================================================
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )


