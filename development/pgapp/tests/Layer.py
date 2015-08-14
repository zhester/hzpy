
import os
import sys

import pygame

sys.path.append(
    os.path.dirname( os.path.dirname( os.path.realpath( __file__ ) ) )
)

from lib.Context import Context
from lib.Layer import Layer

def run( test, verify ):

    conf    = { 'size' : ( 128, 128 ) }
    context = Context.create_root( conf )

    pygame.init()

    screen = pygame.display.set_mode(
        context.conf[ 'size' ],
        0,
        context.conf[ 'depth' ]
    )

    screen.fill( ( 255, 255, 0 ) )

    layer = Layer( context )

    #layer.surface.fill( ( 0, 0, 255 ) )
    #layer.blit( screen )

    loops = 10
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
        if loops <= 0:
            break
        loops -= 1
        pygame.time.wait( 50 )

    pygame.quit()

    return True

