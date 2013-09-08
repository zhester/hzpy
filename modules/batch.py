#!/usr/bin/env python
##############################################################################
#
# batch.py
#
##############################################################################


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

    # see if the user wants to see the command
    if show == True:
        if type( arguments ) is str:
            print arguments
        else:
            print subprocess.list2cmdline( arguments )

    # check for the need for shell parsing
    if type( arguments ) is str:
        use_shell = True
    else:
        use_shell = False

    # attempt to execute the requested command
    try:
        output = subprocess.check_output(
            arguments,
            stderr = subprocess.STDOUT,
            shell  = use_shell
        )

    # if the commad flops, raise our own error exception
    except subprocess.CalledProcessError as error:
        raise CommandError( error.output, error.returncode )

    # return the output collected from the command
    return output


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
