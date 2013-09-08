#!/usr/bin/env python
##############################################################################
#
# batch.py
#
##############################################################################


import os
import shlex
import subprocess


#=============================================================================
class CommandError( Exception ):
    """
    Error from executing commands.
    """


    #=========================================================================
    def __init__( self, output = '', returncode = -1 ):
        """
        Initializes the instance.
        """

        super( CommandError, self ).__init__( 'command execution error' )

        self.output     = output
        self.returncode = returncode



#=============================================================================
def cmd( arguments, show = False ):
    """
    Executes arguments (list or string) as a local command, and returns the
    output as a string.
    @param arguments Command arguments
    @param show Set to True to display the final command using stdout
    @return The output as a string
    @throw CommandError
    """

    # ZIH - here, i'd like to pull the first argument, and check to see if the
    #   host system supports it.  E.g. asking to "del" on a proper shell.
    # We could try to emulate commonly-used things in batch scripts by
    #   either using a simple command mapping, or (preferably) executing the
    #   correct os.* function.

    # check for the need for shell parsing
    if type( arguments ) is str:
        arguments = shlex.split( arguments )

    # see if the user wants to see the command
    if show == True:
        print subprocess.list2cmdline( arguments )

    # attempt to execute the requested command
    try:
        output = subprocess.check_output(
            arguments,
            stderr = subprocess.STDOUT
        )

    # if the commad flops, raise our own error exception
    except subprocess.CalledProcessError as error:
        raise CommandError( error.output, error.returncode )

    # return the output collected from the command
    return output


#=============================================================================
def oscmd( arguments, show = False ):
    """
    Executes arguments (list or string) as a Python OS command (portable).
    This provides a simple string-mapped mechanism for building batches of
    commands.  If the command in question needs a particular type, that type
    must be handled by the user, and set correctly in the arguments list.
    The first string in the arguments list must be an os.* function.
    @param arguments Command arguments
    @param show Set to True to display the final command using stdout
    @return The normal return of the os.* function
    @throw CommandError
    """

    # check for the need for shell parsing
    if type( arguments ) is str:
        arguments = shlex.split( arguments )

    # see if this "command" is available in the os module
    if hasattr( os, arguments[ 0 ] ):
        call = getattr( os, arguments[ 0 ] )
        if callable( call ):

            # call the function, and return its return
            return call( *arguments[ 1 : ] )

    # os module doesn't have this string as a function
    raise CommandError()


#=============================================================================
def _is_executable( path ):
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
def _which( target ):
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
    Executing this module as a script either executes the lines found in the
    files passed on the command line, executes the lines redirected to our
    standard input, or enters into an interactive mode that executes each line
    entered.
    """

    # execute all files on the command line
    if ( sys.__stdin__.isatty() == False ) or ( len( sys.argv ) > 1 ):
        import fileinput
        for line in fileinput.input():
            try:
                print cmd( line, show = True ).strip()
            except CommandError as error:
                print 'CommandError:', error.output
                break

    # enter interactive mode
    else:
        print 'Type "exit" to exit interactive mode.'
        while True:
            line = raw_input( 'cmd> ' )
            if line == 'exit':
                break
            if line[ : 1 ] == '!':
                print oscmd( line[ 1 : ] )
                continue
            try:
                print cmd( line ).strip()
            except CommandError as error:
                print 'CommandError:', error.output


    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
