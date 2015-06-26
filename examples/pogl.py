#!/cygdrive/c/Python27/python.exe

#
# PyOpenGL Hello World
#
# Official Site with Documentation:
#   http://pyopengl.sourceforge.net/
#
# Windows installer doesn't install dependencies (like the site says it
# should).  The unofficial release does:
#
#   http://www.lfd.uci.edu/~gohlke/pythonlibs/
#
# Match "cp##" with Python version.
# Match 32-bit vs. 64-bit against Python installation (not OS).
#
# Download the ".whl" file, and run Windows' `pip` to install it:
#
#   pip install path\to\PyOpenGL-3.1.1a1-cp27-none-win32.whl
#

import OpenGL as ogl
import OpenGL.GLUT
import OpenGL.GLU

def display():
    ogl.GL.glClear( ogl.GL.GL_COLOR_BUFFER_BIT )
    ogl.GL.glBegin( ogl.GL.GL_POINTS )
    ogl.GL.glVertex2i( 100, 50 )
    ogl.GL.glVertex2i( 100, 130 )
    ogl.GL.glVertex2i( 150, 130 )
    ogl.GL.glEnd()
    ogl.GL.glFlush()

if __name__ == '__main__':

    # GLUT setup
    ogl.GLUT.glutInit()
    ogl.GLUT.glutInitWindowSize( 640, 480 )
    ogl.GLUT.glutCreateWindow( 'Hello World' )
    ogl.GLUT.glutInitDisplayMode( ogl.GLUT.GLUT_SINGLE | ogl.GLUT.GLUT_RGB )
    ogl.GLUT.glutDisplayFunc( display )

    # initialization
    ogl.GL.glClearColor( 1.0, 1.0, 1.0, 0.0 )
    ogl.GL.glColor3f( 0.0, 0.0, 0.0 )
    ogl.GL.glPointSize( 4.0 )
    ogl.GL.glMatrixMode( ogl.GL.GL_PROJECTION )
    ogl.GL.glLoadIdentity()
    ogl.GLU.gluOrtho2D( 0.0, 640.0, 0.0, 480.0 )

    # application loop
    ogl.GLUT.glutMainLoop()

