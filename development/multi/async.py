#!/usr/bin/env python
##############################################################################
#
# async.py
#
##############################################################################


import asyncore
import socket


class EchoHandler( asyncore.dispatcher_with_send ):
    def handle_read( self ):
        data = self.recv( 128 ).strip()
        if data:
            self.send( data.upper() )

class EchoServer( asyncore.dispatcher ):
    def __init__( self, host, port ):
        asyncore.dispatcher.__init__( self )
        self.create_socket( socket.AF_INET, socket.SOCK_STREAM )
        self.set_reuse_addr()
        self.bind( ( host, port ) )
        # 5 is the maximum connection backlog (5 is often the max)
        self.listen( 5 )
    def handle_accept( self ):
        conn = self.accept()
        if conn is not None:
            sock, addr = conn
            handler = EchoHandler( sock )


#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv         Arguments passed to the script
    @return             Exit code (0 = success)
    """


    eserver = EchoServer( 'localhost', 2142 )

    # poll for connections
    asyncore.loop()

    # return success
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
