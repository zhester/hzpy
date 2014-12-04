#!/usr/bin/env python


"""
User Configuration Deployment
=============================

This script is intended to provide a simplified way to configure a new user on
any UNIX-like system (FreeBSD, cygwin, Debian, Raspbian, etc).  I now have
normal and root user accounts spread between many physical systems, SBCs,
virtual machines, and jailed environments.  I have the steps to get them all
looking/behaving correctly pretty-well memorized, but let's put this in a
script, get it versioned-controlled, and stop typing so much!

Assumptions
-----------

1. We're in a POSIX-like environment with a functioning shell and Internet
   connection.
2. We have access to an HTTP downloader of some sort (fetch, wget, or curl).
    Note: If we're behind a proxy, the HTTP client already knows how to punch
    through (e.g. with the proper environment variables).
3. There is a functioning Python installation.

Installation
------------

This script provides a bootstrap for the user's environment.  The actual setup
is pulled from a version-controlled repository, and runs a designated
executeable, and/or loads a configuration file that provides dependency and
installation instructions.  The intent is that the repository contains all the
necessary configuration files, so only one trip to the VCS is needed.

Host this script somewhere on the local network, or on a web site, or just
pull it from its original repository, and run it with the URL to the target
configuration repository.

    wget http://example.com/path/to/user.py
    python user.py http://example.com/path/to/configs.git

Configuration
-------------

The easiest way to set this up is to create a repository that can be retrieved
locally (by HTTP, git, or subversion) and has a `dotfiles` directory.  If you
have that in place, this script will download the repository, find the
`dotfiles` directory, backup your local copies of every currently-existing
version of those files, and symbolically link the new copies of each
configuration file into the user environment.

The other option is to create a file called `user.json` in the root of the
repository.  This is a configuration file that indicates where you keep your
dot-files, and which ones you want to backup and link.  The format is as such:

    {
        "files" : {
            "path" : "some/path/to/configs",
            "blacklist" : [ ".special", ".do_not_use", ".testing_only" ]
        }
    }

Alternatively, you can give it a `whitelist` key, and only install those
configurations.  If both are present, only the whitelist is used.

Specifying absolute paths (`/*`) in either of the lists ignores the `path`
setting.  This allows configurations to be handled outside of your home
directory.  You'll still need to have write access to these locations.

Note: The `path` setting is relative to the configuration repository's root.
By default, this setting is set to `"dotfiles"`.

The repository is always cloned/checked-out/etc to a directory called
`.user/configs`.

The backups are copied to a directory called `.user/backups` in the user's
home directory.

### Environment Overrides

The configuration takes environment-specific queues, and can be tweaked for
different environments, host machines, and/or users.

    {
        "environment" : {
            "OSTYPE" : {
                "FreeBSD" : {
                    "files"  : { "blacklist" : [ ".linux_stuff" ] }
                }
            },
            "HOST" : {
                "my-desktop" : {
                    "files" : { "blacklist" : [ ".server_user_config" ] }
                }
            },
            "USER" : {
                "root" : {
                    "files" : { "blacklist" : [ ".non_root_config" ] }
                }
            }
        }
    }

Note: The entire config tree can be overridden within each section.  I've only
provided examples using the `dotfiles.blacklist` settings.

Note: The environment keys are taken directly from the user's environment
variables.  Anything can be specified here.  The keys under eatch "matched"
environment variables can be glob patterns (according Python's `glob` module).
For example, you can do something like this:

    { "environment" : { "OSTYPE" : { "Linux*" : { ... } } } }

This would match anything sticking the word "Linux" at the beginning of the
`$OSTYPE` environment variable.

If you really like regular expressions (and trying to properly encode them in
a JSON string), the keys can be evaluated using Python's `re.match()`.  If you
want to give this a shot, there is a global config item you can use:

    {
        "config" : {
            "regexp-match" : true
        },
        "environment" : {
            "HOST" : { "^cluster-node-\\d{3}" : { ... } }
        }
    }

Note: This will disable glob matching for the entire configuration.  You can
re-enable it using any of the `environment` settings, though.

### Automatic Execution

Let's say you need a script executed as soon as the repository has been
downloaded (check for applications that need to be installed, perform some
kind of standard cleanup activities, whatever).  This can be done one of two
ways:

#### user-install-pre

Create a script in the root named `user-install-pre`, and it will be
automatically `chmod`'d to `744` and executed.  If you name it with an
extension (e.g. `user-install-pre.py`), instead of `chmod`-ing it, the script
will just be passed directly to the interpretor (python, sh, csh, bash, etc).

This script should return to the shell with a valid system exit status in
order for the installer to proceed (e.g. return `0` if you want the installer
to keep going).  Otherwise, the installer will assume your script had a
problem, and will stop installation.

#### user-install-post

Once the automatic portions of the installer have executed, you can specify a
script named `user-install-post`.  This script is just like the `-pre` script,
except that it is run once the environment is set up.

#### user.json

You can also specify scripts or programs to be executed in the configuration
file.

    {
        "auto-exec" : {
            "pre"  : [ "./pre-installer.py", "./something_else.sh argument" ],
            "post" : [ "./post-installer.py", "./path/to/post-install.py" ]
        }
    }

Each script is run in order.  Specify arguments like you would on the shell
(keeping in mind the JSON parser is un-escaping things as it parses the
strings).

### Restoring the Backup

To test your configuration a few times, it might be desired to restore your
backups, nuke anything the installer downloaded, and maybe re-run the
installer.

#### Restoration

Pass the `--restore` argument to restore your environment to its pristine
state (as if this script was never run).

#### Reset

If you want to delete everything _and_ start over again, pass the `--reset`
argument.  This uses a backed-up URL for the configuration repository's URL.
Therefore, it can't be run if there was no backup.

#### Updating the Environment

Once you've got a really sweet setup going, you can update your environment
using this script.  The most likely case is you just updated one of your
configurations.  If that's the case, you can, of course, just re-run the
checkout/pull/fetch/etc command for your configuration repository.  Or, you
can run this script with the `--update` argument.

This argument also provides the nifty feature of running extra commands
specified in the configuration.  Here's what mine does:

    {
        "auto-exec" : {
            "update" : [ "vim +PluginUpdate +qall" ]
        }
    }

### Authorizing SSH Hosts

It's tedious making sure you have all your public keys sorted out between all
these hosts, so this script will automatically sort out your public keys for
you.  You will need to create the list of public keys in the config file.
Once that's done, the installer will check each key for its specified source
host name, and if you're installing/updating on a host that doesn't match a
particular key's host, and it's not already in your `authorized_keys` list, it
will be appended to the list.

Here's how you specify the list:

    {
        "ssh-keys" : {
            "my-desktop" : "ssh-dss blahblahblah user@my-desktop",
            "my-laptop"  : "ssh-dss blahblahblah user@my-laptop"
        }
    }

Note: I don't see why you can't leave your public keys out on a public
repository hosting service (e.g. github).  The worst that can happen is other
people start allowing you to access their stuff without any challenge.  The
big thing to remember is to keep your _private_ keys locked away--preferably,
right next to your super-duper-triple-secret feelings journal.

Note: This never synchronizes keys for any account named "root" or "toor".
Additional user-name based overrides can be given just like any other
override:

    { "environment" : { "USER" : { "service_user" : "ssh-keys" : null } } }


I'll probably write a key importer at some point.  It'd be pretty trivial, and
could be run as a part of the post-installation sequence (complete with
checking-in the change if it was pulled with `git` or `svn`).

"""


import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys


__version__ = '0.0.0'


#-----------------------------------------------------------------------------
# Module-wide Configuration
#-----------------------------------------------------------------------------

target_directory = '.user'              # destination for cloning/checkouts


#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------

#=============================================================================
class Configuration( dict ):
    """
    Handles loading and supplying the installer with configuration
    information.
    """

    #=========================================================================

    # define default merge conflict priority (lowest to highest)
    _merge_priority = [ 'USER', 'OSTYPE', 'HOST' ]


    #=========================================================================
    def __init__( self, *args, **kwargs ):
        """
        Initializes a Configuration object.
        """
        super( Configuration, self ).__init__( *args, **kwargs )


    #=========================================================================
    def load( self, fd ):
        """
        Load the configuration into the object from a file-like object.
        """
        self.loads( fd.read() )


    #=========================================================================
    def loads( self, string ):
        """
        Load the configuration into the object from a string.
        """
        tree = json.loads( string )
        for key, value in tree.items():
            if key == 'merge-priorities':
                self._merge_priorities = value
            else:
                if key in self:
                    self._merge_dicts( self[ key ], value )
                else:
                    self[ key ] = value
        if 'environment' in self:
            self._override()


    #=========================================================================
    def _merge_dicts( self, target, source ):
        """
        Replace leaf nodes in a target dict given a source dict.
        """

        # iterate through each item in the source dict
        for key, value in source.items():

            # see if this item's key exists in the target dict,
            # and if the target item is, itself, a dict
            if ( key in target ) and ( type( target[ key ] ) is dict ):

                    # replace the leaf nodes in the target item
                    self._merge_dicts( target[ key ], value )

            # this item doesn't exist in the target dict, or the target item
            # is not a dict
            else:

                # add or replace the leaf node
                target[ key ] = value


    #=========================================================================
    def _override( self ):
        """
        Processes sub-configs under the 'environment' configuration, and
        resolves the top-level configuration values so a user doesn't see
        any base configurations that are overridden because of the
        environment.
        """

        # source of environment information
        source = os.environ

        # get the list of environment keys we will use for overrides
        overrides = self[ 'environment' ].keys()

        # re-arrange the key list in order of priority (lowest to highest)
        priorities = []

        # make a copy of the merge priority list
        merge_priority = list( self._merge_priority )

        # reverse the copy
        merge_priority.reverse()

        # iterate through the reversed priority list
        for key in merge_priority:

            # if an item with a specified priority is in the override list...
            if key in overrides:

                # ...append it to the priority list
                priorities.append( key )

                # remove it from the override list
                overrides.remove( key )

        # append all the remaining override items
        priorities.extend( overrides )

        # reverse the priorities list, so it overrides things correctly
        priorities.reverse()

        # loop through all specified environment variables
        for key in priorities:

            # if the variable exists in the environment...
            if key in source:

                # fetch the variable's value as the subject of the match
                subject = source[ key ]

                # iterate through each item in the environment list
                for okey, ovalue in self[ 'environment' ][ key ].items():

                    # test the key for a match
                    if fnmatch.fnmatchcase( subject, okey ) == True:

                        # override this part of the base configuration
                        self._merge_dicts( self, ovalue )


#=============================================================================
class UserConfiguration( Configuration ):
    """
    Slight modification of the Configuration class to set up a few
    application-specific defaults.
    """

    #=========================================================================
    def __init__( self, *args, **kwargs ):
        """
        Initializes a UserConfiguration object.
        """
        super( UserConfiguration, self ).__init__( *args, **kwargs )
        self[ 'config' ] = {
            'regexp-match' : False
        }
        self[ 'files' ] = {
            'path'      : 'dotfiles',
            'blacklist' : [],
            'whitelist' : None,
        }
        self[ 'auto-exec' ] = {
            'pre'    : [],
            'post'   : [],
            'update' : []
        }
        self[ 'environment' ] = {}


#=============================================================================
class UserEnvironment( object ):
    """
    User environment management class.
    """

    #=========================================================================
    def __init__( self ):
        """
        Initializes a UserEnvironment object.
        """
        super( UserEnvironment, self ).__init__()
        self._test_mode = False


    #=========================================================================
    def install( url ):
        """
        Runs the installation procedure for a new user environment.
        """

        # determine the type of repository that hosts the configuration
        repo_type = get_repo_type( url )
        if repo_type == 'git':
            getter = _which( 'git' )
            if getter is None:
                raise RuntimeError( 'Unable to locate "git" in path.' )
            arguments = [ getter, 'clone', url, '{cdir}' ]
        elif repo_type == 'subversion':
            getter = _which( 'svn' )
            if getter is None:
                raise RuntimeError( 'Unable to locate "svn" in path.' )
            arguments = [ getter, 'checkout', url, '{cdir}' ]
        elif repo_type == 'http':
            clients = [ 'fetch', 'wget', 'curl' ]
            raise NotImplementedError( 'HTTP repositories not supported.' )
        elif repo_type == 'scp':
            raise NotImplementedError( '"scp" repositories not supported.' )
        else:
            raise RuntimeError( 'Unable to determine repository type.' )

        # get the user's home directory
        user_directory = os.path.expanduser( '~' )

        # set the root of file operations
        user_root = user_directory + os.path.sep + target_directory

        # set the root of configuration backups
        backup_root = user_root + os.path.sep + 'backups'

        # set the root of the configuration repository
        config_root = user_root + os.path.sep + 'configs'

        # in test mode, we do not make changes to the user's home
        if self._test_mode == True:

            # modify stuff only in the test directory
            user_directory = user_root + os.path.sep + 'test'

        # first-time user file tree setup
        try:
            os.mkdir( user_root )
        except OSError:
            # directory already exists
            pass
        try:
            os.mkdir( backup_root )
        except OSError:
            # directory already exists
            pass

        # format the command that will fetch the configuration files
        for index, argument in enumerate( arguments ):
            match = re.match( r'\{[^}]*\}', arguments )
            if match is not None:
                arguments[ index ] = cmd_fmt.format(
                    getter = getter,
                    url    = url,
                    udir   = user_root,
                    cdir   = config_root
                )

        # call the command to download the configuration files
        print subprocess.list2cmdline( arguments )
        result = subprocess.call( arguments )

        # make sure the command reported success
        if result != os.EX_OK:
            raise RuntimeError(
                'Unable to retrieve configuration repository.'
            )

        # create a configuration object
        config = Configuration()

        # check for a user.json file
        config_file = config_root + os.path.sep + 'user.json'
        if os.path.is_file( config_file ):
            with open( config_file ) as cfh:
                config.load( cfh )

        # set the path to the dotfiles
        check = config[ 'files' ][ 'path' ]
        if ( check == ''    ) \
        or ( check == '/'   ) \
        or ( check == False ) \
        or ( check is None  ):
            dotfile_path = config_root
        else:
            dotfile_path = config_root + os.path.sep + check

        # get an initial list of the files in the dotfiles directory
        dotfiles = os.listdir( dotfile_path )

        # run pre-installation scripts in repository
        for command in config[ 'auto-exec' ][ 'pre' ]:
            _exec_command_line( command, config_root )

        # check for a whitelist, and filter the list of dotfiles
        if config[ 'files' ][ 'whitelist' ] is not None:
            dotfiles = [
                d for d in config[ 'files' ][ 'whitelist' ]
                if d in dotfiles
            ]

        # assume we're using a blacklist, and filter the list of dotfiles
        else:
            dotfiles = [
                d for d in dotfiles
                if d not in config[ 'files' ][ 'blacklist' ]
            ]

        # install each configuration file
        ### ZIH - need to support files in directories (without nuking
        ###       existing directories)
        for dotfile in dotfiles:

            # build some path strings
            source = dotfile_path + os.path.sep + dotfile
            target = user_directory + os.path.sep + dotfile
            backup = backup_root + os.path.sep + dotfile

            # if the target configuration file already exists...
            if os.path.exists( target ):

                # ...move it to the backups directory
                os.rename( target, backup )

            # create a link to the dotfile in the repository
            os.symlink( source, target )

        # create a state file to record things we might need later
        ### ZIH - do this!

        # run post-installation scripts in repository
        for command in config[ 'auto-exec' ][ 'post' ]:
            _exec_command_line( command, config_root )


    #=========================================================================
    def reset():
        """
        Runs the reset procedure for an existing user environment.
        """
        # prompt to confirm
        # read the configuration source info from .user/info.json
        # run the restore() procedure
        # run the install() procedure with the original URL
        pass


    #=========================================================================
    def restore():
        """
        Runs the restore procedure for an existing user environment.
        """
        # prompt to confirm
        # delete all symlinks noted in .user/info.json
        # copy original files from .user/backup to ~
        # delete .user directory
        pass


    #=========================================================================
    def enable_test_mode( self, enable = True ):
        """
        Enables a no-risk trial.  If you're not satisfied with the way this
        executed, it did nothing to your home directory that you can't undo by
        just deleting the `.user` directory that was created.
        """
        self._test_mode = enable


    #=========================================================================
    def update():
        """
        Runs the update procedure for an existing user environment
        """
        # open up the .user/info.json file
        #   see what command we need to run to do the initial update
        #      e.g. `git pull` vs. `svn up`
        #   check config for update hooks
        pass


#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------


#=============================================================================
def _exec_command_line( command, prefix ):
    """
    Executes a command (from a string), allowing all output to pass to STDOUT.
    """

    # split the arguments
    arguments = shlex.split( command )

    # attempt to detect generic commands (not a relative command)
    proc = arguments[ 0 ]

    # this is probably a generic/system command
    if proc[ 0 ] != '.':
        check = _which( proc )
        if check is None:
            raise RuntimeError(
                'Unable to locate "{}" in path.'.format( proc )
            )
        arguments[ 0 ] = check

    # this needs to be executed relative to the prefix
    else:
        arguments[ 0 ] = prefix + arguments[ 1 : ]

    # print the statement we're about to execute
    print subprocess.list2cmdline( arguments )

    # attempt to execute the requested command
    result = subprocess.call( arguments )

    # return the result of the command
    return result


#=============================================================================
def get_repo_type( url ):
    """
    Determines a repository type (git, subversion, or HTTP) based on the URL.
    """
    match = re.match( r'.+\.git$', url )
    if match is not None:
        return 'git'
    match = re.match( r'^https?://', url )
    if match is not None:
        return 'http'
    match = re.match( r'^svn', url )
    if match is not None:
        return 'subversion'
    match = re.match( r'^[\w\.-]+@[\w\.-]+:|/', url )
    if match is not None:
        return 'scp'
    return False


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

    See Also: http://code.google.com/p/which/source/browse/trunk/which.py
    """

    # attempt to split the target's dirname and basename
    dirname, basename = os.path.split( target )

    # target came with a dirname component
    if dirname == '':

        # if the target is executable...
        if _is_executable( target ) == True:

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
            if _is_executable( target_path ) == True:

                # return the complete path to the program
                return target_path

    # failed to find target in all search paths
    return None


#-----------------------------------------------------------------------------
# Built-in Unit Testing
#-----------------------------------------------------------------------------

#=============================================================================
def _test_config_tree():
    """
    Tests the configuration tree resolution.
    """
    test_config = """{
    "config" : {
        "setting"      : "value",
        "regexp-match" : false
    },
    "files" : {
        "path"      : "user_test",
        "blacklist" : [],
        "whitelist" : []
    },
    "auto-exec" : {
        "pre"    : [],
        "post"   : [],
        "update" : []
    },
    "ssh-keys" : {
        "host" : "ssh-dss 0123456789ABCDEF user@host"
    },
    "environment" : {
        "OSTYPE" : {
            "__0__" : {
                "config" : { "setting" : "__0__" }
            }
        },
        "USER" : {
            "__1__" : {
                "config" : { "new_setting" : "__1__" }
            }
        },
        "HOST" : {
            "__2__" : {
                "config" : { "new_setting" : "__2__" }
            }
        }
    }
}"""

    source = test_config.replace( '{', '{{' ).replace( '}', '}}' )
    source = re.sub( r'__(\d)__', r'{\1}', source )
    source = source.format(
        os.environ[ 'OSTYPE' ],
        os.environ[ 'USER' ],
        os.environ[ 'HOST' ]
    )

    config = Configuration()
    config.loads( source )

    expected = os.environ[ 'OSTYPE' ]
    actual   = config[ 'config' ][ 'setting' ]

    if expected != actual:
        print 'FAILED: {} != {}'.format( expected, actual )
        return False

    expected = os.environ[ 'HOST' ]
    actual   = config[ 'config' ][ 'new_setting' ]

    if expected != actual:
        print 'FAILED: {} != {}'.format( expected, actual )
        return False

    config._merge_priority.reverse()
    config._override()

    expected = os.environ[ 'USER' ]
    actual   = config[ 'config' ][ 'new_setting' ]

    if expected != actual:
        print 'FAILED: {} != {}'.format( expected, actual )
        return False

    return True


#=============================================================================
def _test_get_repo_type():
    """
    Test the get_repo_type() function.
    """
    cases = [
        [ 'git',        'ssh://user@host/path/repo.git',        True  ],
        [ 'git',        'http://user@host:path/repo.git',       True  ],
        [ 'git',        'https://user@host:path/repo.git',      True  ],
        [ 'subversion', 'svn+ssh://user@host/path/repo',        True  ],
        [ 'subversion', 'svn+ssh://user@host:path/repo',        True  ],
        [ 'subversion', 'svn+http://user@host:path/repo',       True  ],
        [ 'subversion', 'ssh://user@host:path/repo',            False ],
        [ 'http',       'http://user@host/path/repo.tar.gz',    True  ],
        [ 'http',       'svn+ssh://user@host/path/repo.tar.gz', False ],
        [ 'scp',        'user@host:path/repo.tar.gz',           True  ]
    ]
    for case in cases:
        actual = get_repo_type( case[ 1 ] )
        if actual != case[ 0 ]:
            if case[ 2 ] == True:
                print 'FAILED: {} != {} ({})'.format(
                    actual,
                    case[ 0 ],
                    case[ 1 ]
                )
                return False
        else:
            if case[ 2 ] == False:
                print 'FAILED: {} == {} ({})'.format(
                    actual,
                    case[ 0 ],
                    case[ 1 ]
                )
                return False
    return True


#=============================================================================
def _test( argv = None ):
    """
    Test various parts of the user configuration installer.
    """
    tests = [ 'config_tree', 'get_repo_type' ]
    for test in tests:
        name = '_test_' + test
        module = sys.modules[ __name__ ]
        if hasattr( module, name ) == True:
            function = getattr( module, name )
            result = function()
            if result == True:
                print 'PASSED: {}'.format( test )
            else:
                # rely on test to print helpful output
                return
        else:
            print 'FAILED: Test "{}" does not have an executor.'.format( test )
            return


#-----------------------------------------------------------------------------
# Script Execution
#-----------------------------------------------------------------------------

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
        description = 'User Configuration Deployment',
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
        '--restore',
        default = False,
        help    = 'Restore the configuration from backups.',
        action  = 'store_true'
    )
    parser.add_argument(
        '-s',
        '--reset',
        default = False,
        help    = 'Revert all changes, and restart installation.',
        action  = 'store_true'
    )
    parser.add_argument(
        '-t',
        '--test',
        default = False,
        help    = 'Run all internal unit tests.',
        action  = 'store_true'
    )
    parser.add_argument(
        '-u',
        '--update',
        default = False,
        help    = 'Run automated configuration updates.',
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
        'url',
        nargs   = '?',
        default = None,
        help    = 'Configuration repository URL.'
    )

    # parse the arguments
    args = parser.parse_args( argv[ 1 : ] )

    # check for running the built-in unit tests
    if ( 'test' in args ) and ( args.test == True ):

        # run the built-in unit tests with optional arguments
        test_result = _test( argv[ 2 : ] )
        return os.EX_OK if test_result == True else os.EX_SOFTWARE

    # create the environment management object
    user_env = UserEnvironment()

    # check for the URL to request a new installation
    if ( 'url' in args ) and ( args.url is not None ):

        # run the installation procedure
        result = user_env.install( args.url )

    # otherwise, attempt to run one of the other management procedures
    else:

        # default the result to detect a bad argument list
        result = None

        # check known procedures
        for proc in [ 'reset', 'restore', 'update' ]:

            # see if this is the requested procedure
            if ( hasattr( args, proc ) == True ) \
                and ( getattr( args, proc ) == True ):

                # run the procedure
                result = getattr( user_env, proc )()
                break


    # make sure a management procedure was executed
    if result is None:
        print 'Nothing to do.  See --help for usage.'
        return os.EX_USAGE

    # return result of management script
    return result


#=============================================================================
if __name__ == "__main__":
    sys.exit( main( sys.argv ) )

