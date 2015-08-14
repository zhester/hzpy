
import os
import sys

sys.path.append(
    os.path.dirname( os.path.dirname( os.path.realpath( __file__ ) ) )
)

from lib.Context import Context


def run( test, verify ):

    # create a root context
    context = Context.create_root()

    # tests a single, root context

    depth = context.conf.get( 'depth', 'failed' )
    if depth == 'failed':
        print( 'Configuration resolution failure.' )
        return False

    fgc = context.styles.get( 'foreground-color', 'failed' )
    if fgc == 'failed':
        print( 'Style resolution failure.' )
        return False

    # create a child context

    child = context.create()

    depth = child.conf.get( 'depth', 'failed' )
    if depth == 'failed':
        print( 'Child configuration resolution failure.' )
        return False

    # tests a grandchild context

    grandchild = child.create()

    depth = grandchild.conf.get( 'depth', 'failed' )
    if depth == 'failed':
        print( 'Grandchild configuration resolution failure.' )
        return False

    return True

