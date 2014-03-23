# This tool is based on NeHe Tutorial Lesson 48 pythonic version
# created by Brian Leair.
# It has been modified by Paolo Angelelli ((c) 2013)
# and released under GPL v2.0 license.
#
# Original Notes:
# -----
# This code is not an ideal example of Pythonic coding or use of OO 
# techniques. It is a simple and direct exposition of how to use the 
# Open GL API in Python via the PyOpenGL package. It also uses GLUT, 
# a high quality platform independent library. Due to using these APIs, 
# this code is more like a C program using procedural programming.
#
# To run this example you will need:
# Python     - www.python.org (v 2.3 as of 1/2004)
# PyOpenGL     - pyopengl.sourceforge.net (v 2.0.1.07 as of 1/2004)
# Numeric Python    - (v.22 of "numpy" as of 1/2004) numpy.sourceforge.net
#
#

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys

from PhotoSphereRenderer import *        # Draw (), Initialize () and all the real OpenGL work.
from ArcBall import *        # // *NEW* ArcBall header
from PyQt4 import QtGui, QtCore

# *********************** Globals *********************** 
# Python 2.2 defines these directly
try:
    True
except NameError:
    True = 1==1
    False = 1==0


# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

# Number of the glut window.
window = 0


fileUrl = ""


# Reshape The Window When It's Moved Or Resized
def ReSizeGLScene(Width, Height):
    if Height == 0:                        # Prevent A Divide By Zero If The Window Is Too Small 
        Height = 1

    glViewport(0, 0, Width, Height)        # Reset The Current Viewport And Perspective Transformation
    glMatrixMode(GL_PROJECTION)            # // Select The Projection Matrix
    glLoadIdentity()                    # // Reset The Projection Matrix
    # // field of view, aspect ratio, near and far
    # This will squash and stretch our objects as the window is resized.
    # Note that the near clip plane is 1 (hither) and the far plane is 1000 (yon)
    gluPerspective(g_FOV, float(Width)/float(Height), 0.00, 100.0)

    glMatrixMode (GL_MODELVIEW);        # // Select The Modelview Matrix
    glLoadIdentity ();                    # // Reset The Modelview Matrix
    g_ArcBall.setBounds (Width, Height)    # //*NEW* Update mouse bounds for arcball
    return


# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
def keyPressed(*args):
    global g_quadratic
    # If escape is pressed, kill everything.
    key = args [0]
    if key == ESCAPE:
        gluDeleteQuadric (g_quadratic)
        sys.exit ()



def main():
    global window
    # pass arguments to init
    glutInit(sys.argv)

    # Select type of Display mode:   
    #  Double buffer 
    #  RGBA color
    # Alpha components supported 
    # Depth buffer
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    
    # get a 640 x 480 window 
    glutInitWindowSize(640, 480)
    
    # the window starts at the upper left corner of the screen 
    glutInitWindowPosition(0, 0)
    
    # Okay, like the C version we retain the window id to use when closing, but for those of you new
    # to Python, remember this assignment would make the variable local and not global
    # if it weren't for the global declaration at the start of main.
    window = glutCreateWindow("PhotoSphere Python viewer  -- (c) Paolo Angelelli 2013")

       # Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
    # set the function pointer and invoke a function to actually register the callback, otherwise it
    # would be very much like the C version of the code.    
    glutDisplayFunc(Draw)
    
    # Uncomment this line to get full screen.
    #glutFullScreen()

    # When we are doing nothing, redraw the scene.
    glutIdleFunc(Draw)
    
    # Register the function called when our window is resized.
    glutReshapeFunc(ReSizeGLScene)
    
    # Register the function called when the keyboard is pressed.  
    glutKeyboardFunc(keyPressed)


    # GLUT When mouse buttons are clicked in window
    glutMouseFunc (Upon_Click)

    # GLUT When the mouse mvoes
    glutMotionFunc (Upon_Drag)


    # We've told Glut the type of window we want, and we've told glut about
    # various functions that we want invoked (idle, resizing, keyboard events).
    # Glut has done the hard work of building up thw windows DC context and 
    # tying in a rendering context, so we are ready to start making immediate mode
    # GL calls.
    # Call to perform inital GL setup (the clear colors, enabling modes
    Initialize (640, 480, fileUrl)

    # Start Event Processing Engine    
    glutMainLoop()

# Print message to console, and kick off the main to get it rolling.








class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):      

        self.btn = QtGui.QPushButton('OK', self)
        self.btn.move(20, 20)
        self.btn.clicked.connect(self.showDialog)
        
        self.le = QtGui.QLineEdit(self)
        self.le.move(130, 22)
        
        self.fdBtn = QtGui.QPushButton('Choose', self)
        self.fdBtn.move(280, 20)
        self.fdBtn.clicked.connect(self.chooseFile)
        
        self.setGeometry(300, 300, 390, 150)
        self.setWindowTitle('Input dialog')
        self.show()
        
    def chooseFile(self):
        sFileName =  QtGui.QFileDialog.getOpenFileName(self, "Open File", "","Files (*.*)" )
        self.le.setText("file:///"+sFileName)
        self.showDialog()
        
    def showDialog(self):
        global fileUrl
        text = (str(self.le.text()))
        fileUrl = text
        QtCore.QCoreApplication.instance().quit()
            
        
def qtmain():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    ret = app.exec_()
    return ret




if __name__ == '__main__':
    ret = qtmain()
    # Your code that must run when the application closes goes here
    main()
    sys.exit(ret)


















if __name__ == "__main__":
    print "Hit ESC key to quit."
    main()

