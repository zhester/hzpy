#!/usr/bin/env python
##############################################################################
#
# cpblock.py
#
##############################################################################


import os
import re


#=============================================================================
def cpblock( infile, block, outfile ):

    ifh = open( infile, 'rb' )
    ofh = open( outfile, 'wb' )

    if block.find( ',' ) != -1:
        ( start, stop ) = block.split( ',', 1 )
        start  = getoffset( start )
        length = getoffset( stop ) - start

    else:
        ( start, length ) = block.split( ':', 1 )
        start  = getoffset( start )
        length = getoffset( length )

    ifh.seek( start, os.SEEK_SET )
    copied = cpbytes( ofh, ifh, length )

    ofh.close()
    ifh.close()

    return copied


#=============================================================================
def cpbytes( target_handle, source_handle, length ):
    copy_chunk = 4096
    if length > copy_chunk:
        copied = 0
        while copied < length:
            target_handle.write( source_handle.read( copy_chunk ) )
            copied += copy_chunk
        return copied

    target_handle.write( source_handle.read( length ) )
    return length


#=============================================================================
def getint( data ):
    if type( data ) is str:
        if re.match( '^\s*0(x|X)', data ) is not None:
            return int( data, 16 )
    return int( data )


#=============================================================================
def getoffset( offset ):
    if offset.find( '*' ) != -1:
        ( lh, rh ) = offset.split( '*', 1 )
        return getint( lh ) * getint( rh )
    return getint( offset )


#=============================================================================
def main( argv ):
    """ Script execution entry point """

    if len( argv ) < 4:
        print 'usage: cpblock.py <input> <start>:<length> <output>'
        print '       cpblock.py <input> <start>,<stop> <output>'
        print '         note: offsets and lengths can use multiplication:'
        print '               cpblock.py in.dat 100:100*4 out.dat'
        return 0

    copied = cpblock( argv[ 1 ], argv[ 2 ], argv[ 3 ] )
    size   = os.path.getsize( argv[ 3 ] )

    if copied != size:
        print 'Error encountered copying data to %s (%d bytes off).' % (
            argv[ 3 ],
            ( size - copied )
        )
        return 1

    print 'Copied %d bytes from %s to %s.' % ( copied, argv[ 1 ], argv[ 3 ] )

    return 0


#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
