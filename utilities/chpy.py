#*******************************************************************************
# chpy.py
# Zac Hester <zac.hester@gmail.com>
# 2012-08-07
#
# Change the Windows file association for .py to a given Python interpretor.
#
# For usage examples, type:
#   chpy.py help
#
# Windows provides two utilities to manage file type assocations.
# These utilities appear to be built into the command interpretor (e.g.
# "where assoc" fails to find a path).  The subprocess module is used to
# invoke the commands in the current COMSPEC interpretor (usually cmd.exe).
#
#   assoc [.EXT[=[FILETYPE]]]
#   assoc .EXT              ; show file type as .EXT=FILETYPE
#   assoc .EXT=             ; delete file type association
#   assoc .EXT=FILETYPE     ; set .EXT to be a FILETYPE
#
#   ftype [FILETYPE[=[CMDSTR]]]
#   ftype FILETYPE          ; show command as FILETYPE=CMDSTR
#   ftype FILETYPE=         ; delete the command for FILETYPE
#   ftype FILETYPE=CMDSTR   ; set the command for FILETYPE
#
#   CMDSTR is typically:  path\to\prog.exe %1
#       txtfile=%SystemRoot%\system32\NOTEPAD.EXE %1
#       Python.File="C:\Python27\python.exe" "%1" %*
#
#*******************************************************************************

#-------------------------------------------------------------------------------
#                                   IMPORTS
#-------------------------------------------------------------------------------

import  os
import  re
import  subprocess
import  sys

#-------------------------------------------------------------------------------
#                                  VARIABLES
#-------------------------------------------------------------------------------

cmd_assoc = 'assoc'
cmd_ftype = 'ftype'
orig_file = 'chpy_orig.txt'

#-------------------------------------------------------------------------------
#                                   CLASSES
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#                                  FUNCTIONS
#-------------------------------------------------------------------------------


#===============================================================================
def check_compatibility():
    """ check the environment for its compatibility with the script """

    # check for convenience function in subprocess module (new in 2.7)
    try:
        subprocess.check_output
    except AttributeError:
        subprocess.check_output = local_check_output


#===============================================================================
def cmd( cmd, args = [], raw = False, show = False ):
    """ executes a command returning the output as a string """

    # prepend the base command
    args.insert( 0, cmd )

    # check for a raw command (no interpreted arguments)
    if raw == True:
        cmd_args = ' '.join( args )
        if show == True:
            print cmd_args

    # normal command (list of arguments)
    else:
        cmd_args = args
        if show == True:
            print subprocess.list2cmdline( cmd_args )

    # call the command expecting to see string output
    output = subprocess.check_output( cmd_args,
                                      stderr             = subprocess.STDOUT,
                                      shell              = True,
                                      universal_newlines = True )

    # return the output of the command
    return output.strip()


#===============================================================================
def get_ftype():
    """ get the .py file type """

    # get the current file type association for .py files
    assoc = cmd( cmd_assoc, [ '.py' ] )

    # parse the output to get just the file type part
    [ ext, ftype ] = assoc.split( '=', 2 )

    # return the file type
    return ftype


#===============================================================================
def get_pyver( path ):
    """ attempt to get the version of a python executable """

    # try to call the python interpretor from its path
    #   Note: python.exe sends the version string to stderr
    check = cmd( path, [ '--version' ] )

    # attempt to capture the version from the output
    m = re.match( r'^Python (\d{1,2}\.\d{1,2}\.\d{1,2})', check )
    if m == None:
        return None
    return m.group( 1 )


#===============================================================================
def local_check_output( *args, **kwargs ):
    """ a local stand-in for subprocess.check_output """

    # force stdout to be piped into the current process
    kwargs[ 'stdout' ] = subprocess.PIPE

    # open a handle to a new child process
    p = subprocess.Popen( *args, **kwargs )

    # retrieve stdout, and return
    return p.communicate()[ 0 ]


#===============================================================================
def restore_original():
    """ restore the original (or previous) file association """

    # resoration is only possible from a save file
    if os.path.exists( orig_file ):

        # open the file
        f = open( orig_file, 'r' )

        # read the contents for the FILETYPE=CMDSTR argument
        ftype = f.read()

        # close the file
        f.close()

        # delete the file
        os.unlink( orig_file )

        # assign the command string to the file type
        cmd( cmd_ftype, [ ftype ], raw = True, show = True )

    # no save file present
    else:
        print 'Error: Unable to restore without an existing save file.'


#===============================================================================
def save_original():
    """ save the original (or current) file association """

    # do not save over previous settings
    if os.path.exists( orig_file ):
        return

    # open a save file to record the command string
    f = open( orig_file, 'w' )
    if f is not None:

        # write the FILETYPE=CMDSTR to record the setting
        f.write( cmd( cmd_ftype, [ get_ftype() ] ) )

        # close the file
        f.close()


#===============================================================================
def set_from_path( path, report = True ):
    """ set the file assocition to the interpretor from a path """

    # make sure the requested path exists
    if os.path.exists( path ):

        # find out if this really is python
        if get_pyver( path ) == None:
            print 'Specified path (%s) does not appear to be Python.' % path
            return 1

        # attempt to record the original settings for later restoration
        save_original()

        # get the current file type for python scripts
        ftype = get_ftype()

        # construct the ftype arguments
        ft_args = [ '%s="%s"' % ( ftype, path ), '"%1"', '%*' ]

        # set the new command string
        output = cmd( cmd_ftype, ft_args, raw = True, show = True )

        # produce some feedback
        if report == True:
            print output

        # return success
        return 0

    # requested path not found
    print 'Unable to find python interpretor at %s' % path
    return 1


#===============================================================================
def main( argv ):
    """ script execution entry point """

    # run the compatibility check
    check_compatibility()

    # no arguments, attempt to set to current python interpretor
    if len( argv ) == 1:
        return set_from_path( sys.executable )

    # user requests a change to a specified python interpretor
    if len( argv ) == 2:

        # check for the restore request
        if argv[ 1 ] == 'restore':
            restore_original()
            return 0

        # check for the current request
        if argv[ 1 ] == 'current':
            print cmd( cmd_ftype, [ get_ftype() ] )
            return 0

        # check for the help request
        if argv[ 1 ] == 'help':
            print """Usage Examples:
    chpy.py help                      - Display this information.
    chpy.py current                   - Display the current association.
    chpy.py restore                   - Restore the original assocation.
    chpy.py 27                        - Associate a 2.7 installation.
    chpy.py Python27                  - Associate a 2.7 installation.
    chpy.py C:\\Python27\\python.exe    - Specify a complete path to use.
    C:\\Python27\\python.exe chpy.py    - Use the invoking interpretor."""
            return 0

        # check for a number such as "27"
        if re.match( r'^\d{1,3}$', argv[ 1 ] ):
            root = os.path.dirname( os.path.dirname( sys.executable ) )
            return set_from_path( '%sPython%s\\python.exe' \
                                  % ( root, argv[ 1 ] ) )

        # check for a short string such as "Python27"
        if re.match( r'^[A-Za-z0-9 ()_-]+$', argv[ 1 ] ):
            root = os.path.dirname( os.path.dirname( sys.executable ) )
            return set_from_path( '%s%s\\python.exe' \
                                  % ( root, argv[ 1 ] ) )

        # finally, assume the user specified the full path
        return set_from_path( argv[ 1 ] )

    # return success to the shell
    return 0


#---------------------------------------------------------------------
# File executed as a script
#---------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )
