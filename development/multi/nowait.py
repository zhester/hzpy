#!/usr/bin/env python
##############################################################################
#
# nowait.py
#
##############################################################################


import multiprocessing
import Queue
import time


# this simulates workers that have a finite and uninterruptable task to
# complete (large file parsing with private datebase storage)

# the parent process should be a long-running daemon that accepts requests
# from the outside, and spawns new workers to handle the tasks
# the parent process will also be queried to determine the status of each
# task that the workers are processing


#=============================================================================
def worker( status_queue, job ):
    progress = 0
    while( progress < 5 ):
        # simulate doing something that takes a while
        time.sleep( 2 )
        progress += 1
        # update the parent on how well we're doing
        status_queue.put( progress )


#=============================================================================
def main( argv ):
    """
    Script execution entry point
    @param argv         Arguments passed to the script
    @return             Exit code (0 = success)
    """


    # create a queue for reporting the status from a worker process
    status_queue = multiprocessing.Queue()

    # pretend we just received a request to execute a task
    # create a worker to handle a new task
    w = multiprocessing.Process(
        target = worker,
        args   = ( status_queue, 'do it' ),
        name   = 'peon'
    )

    # the worker is about to begin his task
    print 'worker is starting'
    w.start()


    # keep the current progress around in case someone else needs it
    current_progress = 0

    # simulate the parent daemon loop
    while( 1 ):

        # on this pass, check for status updates
        try:
            # non-blocking read from the status queue
            progress = status_queue.get_nowait()
        except Queue.Empty:
            # i don't care if there are no updates, i'm busy, anyway
            pass
        else:
            # good to know the worker is still doing his job
            current_progress = progress
            print 'worker says he\'s done %d of his job' % progress

        # let's see if this worker killed himself after finishing his job
        if w.is_alive() == False:
            print 'worker has finished'

            # for this example, we can stop, too
            break

        # like i said, i'm busy...zzzzzz
        time.sleep( 1 )
        print 'manager probably did something useful here'

    # let multiprocessing do any necessary cleanup
    w.join()

    # return success
    return 0

#=============================================================================
if __name__ == "__main__":
    import sys
    sys.exit( main( sys.argv ) )

