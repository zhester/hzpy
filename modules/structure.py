##############################################################################
#
#   structure.py - Structure Data Access Class
#
##############################################################################


import struct


#=============================================================================
class structure:
    """
    Cleanly implements redundant methods to access structured data in binary
    streams.
    """


    #=========================================================================
    def __init__( self, format, fields ):
        """
        Constructor
        @param format Packed data format string
        @param fields List (or tuple) of parsed field name strings
        """

        self.format = format
        self.fields = fields
        self.sizeof = struct.calcsize( format )


    #=========================================================================
    def load_data( self, obj, data ):
        """
        Load parsed data into specified object.
        @param obj Dictionary (or object) to which data is loaded
        @param data Binary data string from which to load
        @return True if successful
        """

        # Ensure data is correctly specified
        if ( data is None ) or ( len( data ) != self.sizeof ):
            return False

        # Unpack the data string into primitive types
        parts = struct.unpack( self.format, data )

        # Iterate over each parsed field
        for i in range( len( parts ) ):

            # The field name is specified
            if ( len( self.fields ) > i ) and ( self.fields[ i ] is not None ):

                # Assign this data to the dictionary field
                if type( obj ) is dict:
                    obj[ self.fields[ i ] ] = parts[ i ]

                # Assign this data to a member of the field's name
                else:
                    setattr( obj, self.fields[ i ], parts[ i ] )

            # The field name is not specified
            else:

                # Assign this data to the dictionary field
                if type( obj ) is dict:
                    obj[ '_anon_%d' % i ] = parts[ i ]

                # Assign this data to a generated field name
                else:
                    setattr( obj, '_anon_' + i, parts[ i ] )

        # Data properly loaded
        return True


    #=========================================================================
    def load_from_handle( self, obj, handle ):
        """
        Load parsed data into specified object from a file handle.
        @param obj Dictionary (or object) to which data is loaded
        @param handle File handle from which data is read
        @return True if successful
        """

        return self.load_data( obj, handle.read( self.sizeof ) )


    #=========================================================================
    def pack( self, *args ):
        """
        Pack data into string representation.
        @param *args Data values to pack according to structure format
        @return Byte string of packed data
        """
        return struct.pack( self.format, *args )

    #=========================================================================
    def pack_from_object( self, obj ):
        """
        Pack data into string representation from a compatible object.
        @param obj Dictionary (or object) from which data is extracted
        @return Byte string of packed data
        """
        args = []
        for field in self.fields:
            if type( obj ) is dict:
                args.append( obj[ field ] )
            else:
                args.append( getattr( obj, field ) )
        return self.pack( *args )


#=============================================================================
def main( argv ):
    """ Test script execution entry point """

    print "structure module test not yet implemented.  Sorry."
    ##test = structure()


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
