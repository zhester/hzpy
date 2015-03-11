#!/usr/bin/env python
##############################################################################
#
# client.py
#
##############################################################################


import socket


#=============================================================================
def main( argv ):
    """ Script execution entry point """

    # build a message to send
    request = ' '.join( argv[ 1 : ] )

    # create a TCP socket object
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

    try:
        # connect to host over TCP @ port 2142
        sock.connect( ( 'localhost', 2142 ) )

        # send some data over the connection
        sock.sendall( request + '\n' )

        #receive some data from the server
        response = sock.recv( 128 )

    finally:

        # close the connection to the server
        sock.close()

    # display some results
    print 'Request:  %s' % request
    print 'Response: %s' % response

    # Return success.
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
