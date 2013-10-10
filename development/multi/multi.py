#!/usr/bin/env python
##############################################################################
#
# multi.py
#
##############################################################################


import multiprocessing
import os
import time


#=============================================================================
def daemon( pipe ):

    # daemonic loop
    while( 1 ):

        # this blocks until a message is received
        message = pipe.recv()

        # shutdown message
        if message[ 'event' ] == 42:
            break

        # print something message
        elif message[ 'event' ] == 1:
            print message[ 'content' ]

        # return something message
        elif message[ 'event' ] == 2:
            pipe.send( message[ 'content' ].upper() )


#=============================================================================
def proc_info( name ):
    print name
    print 'module name:', __name__
    if hasattr( os, 'getppid' ):
        print 'parent process:', os.getppid()
    print 'process id:', os.getpid()


#=============================================================================
def proc( com ):
    #proc_info( 'function proc' )
    com.put( 'dear mom...' )



#=============================================================================
def main( argv ):
    """ Script execution entry point """

    off = '''
    q = multiprocessing.Queue()
    p = multiprocessing.Process(
        target = proc,
        args   = ( q, ),
        name   = 'my child'
    )
    p.start()
    print q.get()
    p.join()
    '''

    # create a duplex pipe
    ( p_pipe, c_pipe ) = multiprocessing.Pipe( True )

    # create a process object for the daemon process
    d = multiprocessing.Process(
        target = daemon,
        args   = ( c_pipe, ),
        name   = 'damien'
    )

    # start the daemon process
    d.start()

    # send a simple, no-feedback message to the daemon process
    p_pipe.send( { 'event' : 1, 'content' : 'Hi, Son!' } )

    # send a message that expects feedback
    p_pipe.send( { 'event' : 2, 'content' : 'hello' } )
    response = p_pipe.recv()

    # confirm the daemon is still alive
    print 'Daemon is alive:', d.is_alive()

    # send the shutdown message to the daemon
    p_pipe.send( { 'event' : 42 } )

    # wait for everything to stablize (example only, don't do this)
    time.sleep( 1 )

    # confirm the daemon has been killed
    print 'Daemon is alive:', d.is_alive()

    # ensure the daemon process has shut down
    d.join()

    # confirm the daemon is really dead
    print 'Daemon is alive:', d.is_alive()

    # return success
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )
