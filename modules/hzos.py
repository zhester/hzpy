#!/usr/bin/env python


"""
Additional OS Functionality
"""


import os
import sys


#=============================================================================
def is_executable( path ):
    """
    Tests a path to determine if it is a valid executable.
    """
    if os.path.isfile( path ) == True:
        return os.access( path, os.X_OK )
    path += '.exe'
    if os.path.isfile( path ) == True:
        return os.access( path, os.X_OK )
    return False


#=============================================================================
def mkdir( path, mode = 0777 ):
    """
    User-friendly os.mkdir() front-end.

    @param path The path to the directory to create.
    @param mode The numeric permission mode of the new directory.
                The mode is masked out by the current umask value.
                The default mode is 0777.
    """

    # directory exists, no need to continue
    if os.path.isdir( path ):
        return

    # a file exists with the same name, throw an exception
    if os.path.isfile( path ):
        raise OSError( 'Unable to make directory: file exists at %s' % path )

    # see if recursive directory creation is necessary
    elif ( '/' in path ) or ( '\\' in path ):
        os.makedirs( path, mode )

    # create the directory
    else:
        os.mkdir( path, mode )


#=============================================================================
def which( target ):
    """
    which utility emulation function.

    See Also:
    http://code.google.com/p/which/source/browse/trunk/which.py
    """

    # attempt to split the target's dirname and basename
    dirname, basename = os.path.split( target )

    # target came with a dirname component
    if dirname:

        # if the target is executable...
        if _is_executable( target ):

            # return the given path
            return target

    # target has no dirname component
    else:

        # iterate through each search path
        for path in os.environ[ 'PATH' ].split( os.pathsep ):

            # some environments will quote the path
            path = path.strip( '"\'' )

            # construct a complete path to the program
            target_path = os.path.join( path, target )

            # if the target is executable...
            if _is_executable( target_path ):

                # return the complete path to the program
                return target_path

    # failed to find target in all search paths
    return None



#=============================================================================
def main( argv ):
    """
    """


    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )

