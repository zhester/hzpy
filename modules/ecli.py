#!/usr/bin/env python


"""
Extensible Command-line Interface
=================================

Implements a relatively sophisticated CLI using the `readline` module.  This
means the CLI support session-based history and command completion.  It also
allows users to customize their interaction via the relatively standard
`.inputrc` configuration.

The intent is for applications to extend the `Interpereter` class.  However,
the `Interpreter` class is fully functional on its own.  It also provides
examples on how to populate commands, and easily map them to functions and/or
methods.

See the `start_demo()` function for an example of using the base class as-is.
"""


import os
import re
import readline
import shlex
import sys


__version__ = '0.0.0'


#=============================================================================
class Interpreter( object ):
    """
    Implements an extensible command interpreter.
    """

    #=========================================================================
    def __init__( self, commands = None, output = None ):
        """
        Initializes an Interpreter object.

        @param commands A dictionary of commands.  Each key is the name of the
                        command (entered by the user).  The value for each key
                        is either a static string (send to the user as-is), a
                        function reference (called when the command is
                        invoked), or a name of one of the host class' methods
                        prefixed with an underscore (`_`).  If no commands are
                        given, the `Interpretor` just provides a startup
                        message and a way to exit the CLI.
        @param output   The stream to which all output is sent.  `stdout` is
                        the default stream if none is specified.
        """
        super( Interpreter, self ).__init__()
        if commands is None:
            commands = {
                '_startup' : 'Entering interactive mode. Type "exit" to exit.',
                'exit'     : '_exit'
            }
        self._commands = commands
        self._out      = output if output is not None else sys.stdout
        self._done     = False


    #=========================================================================
    def complete( self, text, state ):
        """
        Completer function for readline.

        @param text  The text entered by the user
        @param state The current readline completion state (0, 1, 2, etc.)
        @return      A list of potential commands that match the current input
                     state.  If no commands match, this returns `None` to
                     indicate no change in the CLI.
        """

        # initial completion state
        if state == 0:

            # the user has entered something for completion
            if text:

                # filter list of commands by their prefix
                self._matches = [
                    m for m in self._commands.keys()
                    if ( m[ 0 ] != '_' ) and ( m.startswith( text ) )
                ]

            # there is no text entered yet
            else:

                # show entire list of valid commands
                self._matches = [
                    m for m in self._commands.keys()
                    if m[ 0 ] != '_'
                ]

            # sort the new list of potential matches
            self._matches.sort()

        # see if the state is still valid for our list of potential matches
        if state < len( self._matches ):

            # return the best match
            return self._matches[ state ]

        # nothing matches, the CLI does nothing in response
        return None


    #=========================================================================
    def exit( self, args ):
        """
        Call to exit the interactive loop.

        @param args The command-line argument list
        """
        self._done = True


    #=========================================================================
    def get_prompt( self ):
        """
        Retrieves the current input prompt.

        @return A string to present to the user, prompting for input
        """
        return '> '


    #=========================================================================
    def help( self, args ):
        """
        Handles requests for usage information.

        @param args The command-line argument list
        @return     Auto-generated help documentation
        """

        # find all exit commands
        exit_cmds = []

        # build a dictionary of command documentation
        help_doc  = {}

        # scan through all known commands
        for k, v in self._commands.items():

            # ignore internal commands
            if k[ 0 ] == '_':
                continue

            # commands specified by string
            if isinstance( v, str ):
                if v == '_exit':
                    exit_cmds.append( k )
                elif v == '_help':
                    help_doc[ k ] = 'Displays list of commands.'

            # other commands, look for docstring
            elif hasattr( v, '__doc__' ) and ( v.__doc__ is not None ):
                help_doc[ k ] = v.__doc__.strip()

            # everything else
            else:
                help_doc[ k ] = '(help not available)'

        # list of sorted commands
        keys = help_doc.keys()
        keys.sort()

        # help documentation
        fmt = '  {0} :\n    {1}'
        doc = '\n'.join( fmt.format( k, help_doc[ k ] ) for k in keys )

        # look for known exit commads
        if len( exit_cmds ) > 0:
            doc += '\n  Type "{}" to exit.'.format(
                '" or "'.join( exit_cmds )
            )

        # return the documentation
        return doc + '\n'


    #=========================================================================
    def handle_args( self, line, args ):
        """
        Handles command input after it has been parsed into individual
        arguments.

        @param line The line as entered by the user
        @param args The command-line arguments list
        """

        # ensure there are arguments to be handled
        if len( args ) > 0:

            # list of commands
            commands = self._commands.keys()

            # make sure we can handle it
            if args[ 0 ] not in commands:
                self._unknown( args[ 0 ] )
                return

            # get the command handler
            handler = self._commands[ args[ 0 ] ]

            # detect and run the appropriate command handler
            self._run_handler( handler, args )


    #=========================================================================
    def handle_line( self, line ):
        """
        Handles command input as soon as it arrives from the user.

        @param The line as entered by the user
        """

        # remove exterior white space
        stripped = line.strip()

        # test for the presence of a command string
        if len( stripped ) > 0:

            # parse the input line
            args = shlex.split( stripped )

            # handle the parsed arguments
            self.handle_args( line, args )


    #=========================================================================
    def mainloop( self ):
        """
        Executes the command loop until the user exits.

        @return The shell-style exit status
        """

        # run the startup procedure for the command-line interface
        self.run_startup()

        # enter the loop until the user exits the interface
        while self._done == False:

            # handle the next line from the user
            self.handle_line( raw_input( self.get_prompt() ) )

        # run the shutdown procedure for the command-line interface
        self.run_shutdown()

        # return shell exit status
        return os.EX_OK


    #=========================================================================
    def put( self, text ):
        """
        Puts text to the output stream.

        @param text The text to send to the user
        """
        self._out.write( text )


    #=========================================================================
    def read_input_config( self ):
        """
        Attempts to read readline's input configuration for the user.

        @return True if a user's configuration was found and read
        """

        # build some basic paths to the readline configurations
        user_conf = os.path.expanduser( '~/.inputrc' )
        host_conf = '/etc/inputrc'

        # the environment variable should take precedence
        if 'INPUTRC' in os.environ:
            init = os.environ[ 'INPUTRC' ]

        # next, check the for a user's custom configuration
        elif os.path.isfile( user_conf ):
            init = user_conf

        # finally, see if the host has a basic configuration
        elif os.path.isfile( host_conf ):
            init = host_conf

        # no configuration found
        else:
            return False

        # read the init file for the user
        readline.read_init_file( init )
        return True


    #=========================================================================
    def run_shutdown( self ):
        """
        Runs the shutdown procedure for the session.
        """

        # send summary text
        if '_shutdown' in self._commands:
            self._run_handler( self._commands[ '_shutdown' ] )


    #=========================================================================
    def run_startup( self ):
        """
        Runs the startup procedure for the session.
        """

        # configure the readline module
        readline.set_completer( self.complete )

        # attempt to read an init file for readline
        result = self.read_input_config()

        # no init file
        if result == False:

            # bind the tab key for completion
            readline.parse_and_bind( 'tab: complete' )

        # send introductory text
        if '_startup' in self._commands:
            self._run_handler( self._commands[ '_startup' ] )


    #=========================================================================
    def _run_handler( self, handler, args = None ):
        """
        Runs any handler, and sends returned data to the output.

        @param handler
        @param args
        """

        # default the argument list
        if args is None:
            args = []

        # look for handlers specified by string
        if isinstance( handler, str ):

            # look for internal handlers
            if ( handler[ 0 ] == '_' ) and ( hasattr( self, handler[ 1 : ] ) ):

                # attempt to resolve this handler
                self._run_handler( getattr( self, handler[ 1 : ] ), args )

            # this handler is a static string
            else:

                # send the string to the output
                self.put( '{}\n'.format( handler ) )

        # look for function handlers
        elif callable( handler ):
            result = handler( args )
            if result is not None:
                self.put( result )

        # nothing seems to work
        else:
            self._unknown( args[ 0 ] )


    #=========================================================================
    def _unknown( self, command ):
        """
        Indicate an unknown command to the user.

        @param command
        """
        self.put( 'Unknown command "{}".\n'.format( command ) )


#=============================================================================
def start_demo( args ):
    """
    Runs the module as its own CLI.
    """

    # define a few command handlers
    def handle_echo( args ):
        """ Echos the given input back to the output. """
        return ' '.join( args[ 1 : ] ) + '\n'
    def handle_caps( args ):
        """ Converts the given input to uppercase letters. """
        return ' '.join( args[ 1 : ] ).upper() + '\n'
    def handle_reverse( args ):
        """ Reverses the letters in the given input. """
        return ' '.join( args[ 1 : ] )[ : : -1 ] + '\n'

    # define a few commands with their handlers
    # note: the special commands and handlers that start with "_"
    commands = {
        'echo'      : handle_echo,
        'caps'      : handle_caps,
        'reverse'   : handle_reverse,
        'help'      : '_help',
        'exit'      : '_exit',
        '_startup'  : 'Entering interactive mode.  Type "exit" to exit.',
        '_shutdown' : 'Goodbye!'
    }

    # create a simple command interpreter
    ecli = Interpreter( commands )

    # execute the command loop until the user exits the CLI
    exit_status = ecli.mainloop()

    # the mainloop returns the typical shell exit status
    return exit_status


#=============================================================================
def _test():
    """
    Executes all module test functions.

    @return True if all tests pass, false if one fails.
    """

    # imports for testing only
    import inspect

    # set up a simple logging facility to capture or print test output
    class TestError( RuntimeError ):
        pass
    class TestLogger( object ):
        def fail( self, message ):
            caller = inspect.getframeinfo( inspect.stack()[ 1 ][ 0 ] )
            output = '## FAILED {}: {} ##'.format( caller.lineno, message )
            self.put( output )
            raise TestError( output )
        def put( self, message ):
            sys.stdout.write( '{}\n'.format( message ) )
    log = TestLogger()

    # list of all module members
    members = globals().copy()
    members.update( locals() )

    # iterate through module members
    for member in members:

        # check members for test functions
        if ( member[ : 6 ] == '_test_' ) and ( callable( members[ member ] ) ):

            # execute the test
            try:
                members[ member ]( log )

            # catch any errors in the test
            except TestError:

                # return failure to the user
                return False

    # if no test fails, send a helpful message
    log.put( '!! PASSED !!' )

    # return success to the user
    return True


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
        description = 'Extensible Command-line Interface',
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
    parser.add_argument(
        '-t',
        '--test',
        default = False,
        help    = 'Execute built-in unit tests.',
        action  = 'store_true'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # user requests built-in unit tests
    if args.test != False:
        result = _test()
        if result == False:
            return os.EX_SOFTWARE
        return os.EX_OK

    # check args.* for script execution here
    else:

        # start the module demo interface
        return start_demo( args )

    # return success
    return os.EX_OK


#=============================================================================
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )

