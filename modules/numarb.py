#!/usr/bin/env python
##############################################################################
#
# numarb.py
#
# Numeric object arbitration base class.  Allows a sub-class to quickly
# benefit from routine numeric operations.  This pattern is helpful when an
# object is providing a front-end to a single value (or set of values that can
# be simply reduced to a single value).
#
# ZIH - note: implementation is incomplete.  currently researching the
# descriptor protocol to replace some of the redundant type checking
#
##############################################################################


import copy


#=============================================================================
class numarb( object ):


    #=========================================================================
    def __init__( self, field = 'value' ):
        """
        """

        # ZIH - some people will always call super() before setting up
        #   instance attributes, so this isn't a good check
        #if hasattr( self, field ) == False:
        #    raise AttributeError( 'attribute "%s" not available' % field )

        # store the numeric field name
        self._na_field = field

        # get the attribute
        attr = getattr( self, self._na_field )

        # see if the attribute is a method
        if callable( attr ):
            # ZIH - looking into descriptors to see if i can make it easy
            #   to specify a get/set protocol for all objects
            #self._na_get = attr
            pass

        # point to an object copier (can be overridden)
        self._na_copier = copy.copy


    #=========================================================================
    def __add__( self, other ):
        """
        """

        v = getattr( self, self._na_field )
        if isinstance( other, ( int, float ) ) == True:
            return self._na_dup( v + other )
        elif hasattr( other, self._na_field ):
            return self._na_dup( v + getattr( other, self._na_field ) )
        raise NotImplemented


    #=========================================================================
    def __cmp__( self, other ):
        """
        """

        v = getattr( self, self._na_field )
        if isinstance( other, ( int, float ) ) == True:
            return other - v
        elif hasattr( other, self._na_field ):
            return getattr( other, self._na_field ) - v
        raise NotImplemented


    #=========================================================================
    def __div__( self, other ):
        """
        """

        v = getattr( self, self._na_field )
        if isinstance( other, ( int, float ) ) == True:
            return self._na_dup( v + other )
        elif hasattr( other, self._na_field ):
            return self._na_dup( v + getattr( other, self._na_field ) )
        raise NotImplemented


    #=========================================================================
    def __float__( self ):
        """
        """

        return float( self._na_get() )


    #=========================================================================
    def __int__( self ):
        """
        """

        return int( self._na_get() )


    #=========================================================================
    def __mul__( self, other ):
        """
        """

        v = getattr( self, self._na_field )
        if isinstance( other, ( int, float ) ) == True:
            return self._na_dup( v * other )
        elif hasattr( other, self._na_field ):
            return self._na_dup( v * getattr( other, self._na_field ) )
        raise NotImplemented


    #=========================================================================
    def __radd__( self, other ):
        """
        """

        return self.__add__( other )


    #=========================================================================
    def __rdiv__( self, other ):
        """
        """

        pass


    #=========================================================================
    def __rmul__( self, other ):
        """
        """

        return self.__mul__( other )


    #=========================================================================
    def __rsub__( self, other ):
        """
        """

        pass


    #=========================================================================
    def __sub__( self, other ):
        """
        """

        v = getattr( self, self._na_field )
        if isinstance( other, ( int, float ) ) == True:
            return self._na_dup( v - other )
        elif hasattr( other, self._na_field ):
            return self._na_dup( v - getattr( other, self._na_field ) )
        raise NotImplemented


    #=========================================================================
    def _na_dup( self, value ):
        """
        """

        c = self._na_copier( self )
        c._na_set( value )
        return c


    #=========================================================================
    def _na_get( self ):
        """
        """

        return getattr( self, self._na_field )


    #=========================================================================
    def _na_set( self, value ):
        """
        """

        return setattr( self, self._na_field, value )


#=============================================================================
def main( argv ):
    """ Script execution entry point """



    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
