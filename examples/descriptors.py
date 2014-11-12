#!/usr/bin/env python


"""
Descriptor Examples
"""


__version__ = '0.0.0'


#=============================================================================
class class_style( object ):
    """
    Class Style Descriptor
    """

    #=========================================================================
    def __init__( self, name ):
        """
        Initializes a class_style descriptor object.
        """
        self.name = name

    #=========================================================================
    def __get__( self, obj, objtype = None ):
        """
        Getter
        """
        return obj.proxied[ self.name ]

    #=========================================================================
    def __set__( self, obj, value ):
        """
        Setter
        """
        obj.proxied[ self.name ] = value


#=============================================================================
class dict_proxy( object ):
    """
    Dictionary proxy descriptor.
    """

    #=========================================================================
    def __init__( self, dname, kname ):
        """
        Initializes a dict_proxy object.
        """
        super( dict_proxy, self ).__init__()
        self._dname = dname
        self._kname = kname


    #=========================================================================
    def __get__( self, obj, objtype = None ):
        """
        Retrieves data from a proxied dictionary.
        Note: Allow underlying exceptions to be raised.
        """
        dobj = getattr( obj, self._dname )
        return dobj[ self._kname ]


    #=========================================================================
    def __set__( self, obj, value ):
        """
        Modifies data in a proxied dictionary.
        Note: Allow underlying exceptions to be raised.
        """
        dobj = getattr( obj, self._dname )
        dobj[ self._kname ] = value


    #=========================================================================
    def __del__( self, obj ):
        """
        Removes data from a proxied dictionary.
        """
        dobj = getattr( obj, self._dname )
        del dobj[ self._kname ]


#=============================================================================
class owner( object ):
    """
    Models some object that owns the descriptors.
    """

    # descriptors appear to be class properties
    a = class_style( 'a' )
    b = class_style( 'b' )
    c = dict_proxy( 'proxied', 'a' )
    d = dict_proxy( 'proxied', 'b' )

    #=========================================================================
    def __init__( self ):
        """
        Initializes an owner object.
        """
        super( owner, self ).__init__()
        self.proxied = {
            'a' : 'AAA',
            'b' : 'BBB'
        }


#=============================================================================
def test_descriptors():
    """
    Runs some example tests of descriptor code.
    """

    # can we intercept a request for proxied data?
    instance = owner()
    print 'instance.a == "{}"'.format( instance.a )

    # can we intercept modification of proxied data?
    instance.a = 'aaa'
    print 'instance.a = "aaa"'
    print 'instance.a == "{}"'.format( instance.a )

    # can we muck about with proxied data from other descriptors?
    print 'instance.c == "{}"'.format( instance.c )
    print 'instance.d == "{}"'.format( instance.d )

    # are these descriptors truly bound to the instance?
    instance2 = owner()
    instance2.b = '222'
    print 'instance2.b = "222"'
    print 'instance.d == "{}"'.format( instance.d )
    print 'instance2.d == "{}"'.format( instance2.d )


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
        description = 'Descriptor Examples',
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

    # check args.* for script execution here
    test_descriptors()

    # return success
    return 0


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )

