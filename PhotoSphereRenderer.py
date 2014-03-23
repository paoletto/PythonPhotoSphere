
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import copy
from math import cos, sin
import numpy
import PIL.Image as Image
import urllib, cStringIO

from ArcBall import *                 # ArcBallT and this tutorials set of points/vectors/matrix types

PI2 = 2.0*3.1415926535            # 2 * PI (not squared!)         // PI Squared

# *********************** Globals *********************** 
# Python 2.2 defines these directly
try:
    True
except NameError:
    True = 1==1
    False = 1==0

g_Transform = Matrix4fT ()
g_Rotation  = Matrix4fT ()
g_Translation = Matrix4fT ()
g_Scaling     = Matrix4fT ()
g_initialRotation = Matrix3fT()



if 1:
    #added
    g_quaternion = Quat4fT()
    g_quaternion[0]  = sqrt(0.5)
    g_quaternion[1]  = 0
    g_quaternion[2]  = 0
    g_quaternion[3]  = sqrt(0.5)
    g_initialRotation = Matrix3fSetRotationFromQuat4f(g_quaternion)
    g_Transform = Matrix4fSetRotationFromMatrix3f(g_Transform, g_initialRotation)



g_LastRot = Matrix3fT ()
g_ThisRot = Matrix3fT ()
g_fLastScale = 1.0
g_fThisScale = 1.0
g_vecLastTranslation = Vector3fT()
g_vecThisTranslation = Vector3fT()

if 1:
    #added
    g_ThisRot = Matrix3fSetRotationFromQuat4f(g_quaternion)

g_ArcBall = ArcBallT (640, 480)
g_isDragging = False
g_rightDragging = False
g_midDragging = False
g_quadratic = None
g_sphereRadius = 0.1
g_FOV = 75.0
g_textures = numpy.zeros(1,numpy.int32)

g_texWidth = 0
g_texHeight = 0
g_texData = 0

g_pctOffset=0.15


def loadImage( imageName = "/local/photo/SR71.jpg" ): # "/local/photo/montagna.jpg" ):
    global g_texWidth
    global g_texHeight
    global g_texData    



    file = cStringIO.StringIO(urllib.urlopen(imageName).read())
    im = Image.open(file)
    #im = Image.open(imageName)
#    try:
#        g_texWidth, g_texHeight, g_texData = im.size[0], im.size[1], im.tostring("raw", "RGBA", 0, -1)
#    except SystemError:
#       g_texWidth, g_texHeight, g_texData = im.size[0], im.size[1], im.tostring("raw", "RGBX", 0, -1)
#       
#       
#    im = Image.open("/home/paolo/Desktop/GLBALL/GLball/wall01.tga")
    width, height = im.size
    
    pixels = im.getdata()
    pixelData = im.load()
    
    c  = numpy.zeros(width * int (height * (1 + 2*g_pctOffset))  * 3, numpy.uint8)
    rowSkip = int (height*g_pctOffset)
    
    curHeight =     int (height * (1+2*g_pctOffset))
    
    for hj in range(curHeight):    
        for i in range(width):
            j = hj - rowSkip
            if (j >= 0) and (j < height):
                d = pixelData[i,j]
                c[3*(hj*width + i) ] = d[0]
                c[3*(hj*width + i)+1 ] = d[1]
                c[3*(hj*width + i)+2 ] = d[2] 
            
    g_texWidth, g_texHeight, g_texData = width, height, c
    g_texWidth, g_texHeight, g_texData = width, curHeight, c
    
#    imOutput = Image.new( 'RGB', (width,height), "black") # create a new black image
#    pixelsOutput = imOutput.load() # create the pixel map
#    for j in range(height):    
#        for i in range(width): 
#            pixelsOutput[i,j] = (c[3*(j*width + i) ], c[3*(j*width + i)+1 ], c[3*(j*width + i)+2 ])
#        
#    
#    imOutput.show()

# A general OpenGL initialization function.  Sets all of the initial parameters. 
def Initialize (Width, Height, fileUrl):                # We call this right after our OpenGL window is created.
    global g_quadratic
    global g_textures
    
    #loadImage("file:///local/www/web/wci/uppete/ups/PANO_20130727_160023403796945.jpg")
    #loadImage("http://bonas.us/uppete/ups/PANO_20130727_160023403796945.jpg")
    loadImage(fileUrl)



    glClearColor(0.0, 0.0, 0.0, 1.0)                    # This Will Clear The Background Color To Black
    glClearDepth(1.0)                                    # Enables Clearing Of The Depth Buffer
    glDepthFunc(GL_LEQUAL)                                # The Type Of Depth Test To Do
    glEnable(GL_DEPTH_TEST)                                # Enables Depth Testing
    glShadeModel (GL_FLAT);                                # Select Flat Shading (Nice Definition Of Objects)
    #glShadeModel (GL_SMOOTH);                                # Select Flat Shading (Nice Definition Of Objects)
    glHint (GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)     # Really Nice Perspective Calculations

    g_quadratic = gluNewQuadric();
    gluQuadricOrientation(g_quadratic,GLU_INSIDE)
    gluQuadricOrientation(g_quadratic,GLU_OUTSIDE)
    gluQuadricNormals(g_quadratic, GLU_SMOOTH);
    gluQuadricDrawStyle(g_quadratic, GLU_FILL); 
    gluQuadricTexture(g_quadratic, GL_TRUE); 
    # Why? this tutorial never maps any textures?! ? 
    # gluQuadricTexture(g_quadratic, GL_TRUE);            # // Create Texture Coords

    glEnable (GL_LIGHT0)
    glEnable (GL_LIGHTING)

    glEnable (GL_COLOR_MATERIAL)


    glEnable ( GL_TEXTURE_2D );
    glPixelStorei ( GL_UNPACK_ALIGNMENT, 1 );
    glGenTextures (1, g_textures);
    
    glBindTexture ( GL_TEXTURE_2D, g_textures[0] );
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
    glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGB, g_texWidth, g_texHeight, 0,
            GL_RGB, GL_UNSIGNED_BYTE, g_texData
        )

    return True




def Upon_Drag (cursor_x, cursor_y):
    """ Mouse cursor is moving
        Glut calls this function (when mouse button is down)
        and pases the mouse cursor postion in window coords as the mouse moves.
    """
    global g_isDragging, g_rightDragging, g_midDragging, g_LastRot, g_Transform, g_ThisRot, g_fLastScale, g_fThisScale , g_vecLastTranslation, g_vecThisTranslation
    global g_Rotation, g_Translation, g_Scaling

    mouse_pt = Point2fT (cursor_x, cursor_y)
    if (g_isDragging):
        #print "g_leftDragging"

        ThisQuat = g_ArcBall.drag (mouse_pt)                        # // Update End Vector And Get Rotation As Quaternion
        g_ThisRot = Matrix3fSetRotationFromQuat4f (ThisQuat)        # // Convert Quaternion Into Matrix3fT
        # Use correct Linear Algebra matrix multiplication C = A * B
        g_ThisRot = Matrix3fMulMatrix3f (g_LastRot, g_ThisRot)        # // Accumulate Last Rotation Into This One
        g_Rotation = Matrix4fSetRotationFromMatrix3f (g_Transform, g_ThisRot)    # // Set Our Final Transform's Rotation From This One
    elif (g_midDragging):
        #print "g_midDragging"
        #panning =  translation
        pass
    elif (g_rightDragging):
        #print "g_rightDragging"
        fZoomAmt = g_ArcBall.zoom(mouse_pt)
        fZoom = g_fLastScale + fZoomAmt
        fZoom = numpy.clip(10.0,0.05, fZoom)
        g_fLastScale = fZoom
        
        g_Scaling = getScalingF(fZoom)
        
                
        pass
    
    g_Transform = copy.copy (g_Rotation)
    g_Transform = Matrix3fMulMatrix3f(g_Transform, g_Translation)
    g_Transform = Matrix3fMulMatrix3f(g_Transform, g_Scaling)
    return

def Upon_Click (button, button_state, cursor_x, cursor_y):
    """ Mouse button clicked.
        Glut calls this function when a mouse button is
        clicked or released.
    """
    global g_isDragging, g_rightDragging, g_midDragging, g_LastRot, g_Transform, g_ThisRot

    g_isDragging = g_rightDragging = g_midDragging = False
    if (button == GLUT_RIGHT_BUTTON and button_state == GLUT_UP):
        # Right button click
        g_rightDragging = False
        ##g_LastRot = Matrix3fSetIdentity ();                            # // Reset Rotation
        ##g_ThisRot = Matrix3fSetIdentity ();                            # // Reset Rotation
        ##g_Transform = Matrix4fSetRotationFromMatrix3f (g_Transform, g_ThisRot);    # // Reset Rotation
    elif (button == GLUT_RIGHT_BUTTON and button_state == GLUT_DOWN):
        g_rightDragging = True
        mouse_pt = Point2fT (cursor_x, cursor_y)
        g_ArcBall.click (mouse_pt);    
        pass
    elif (button == GLUT_MIDDLE_BUTTON and button_state == GLUT_UP):
        g_midDragging = False
        pass
    elif (button == GLUT_MIDDLE_BUTTON and button_state == GLUT_DOWN):
        mouse_pt = Point2fT (cursor_x, cursor_y)
        g_ArcBall.click (mouse_pt);            
        g_midDragging = True
        pass
    elif (button == GLUT_LEFT_BUTTON and button_state == GLUT_UP):
        # Left button released
        g_LastRot = copy.copy (g_ThisRot);                            # // Set Last Static Rotation To Last Dynamic One
    elif (button == GLUT_LEFT_BUTTON and button_state == GLUT_DOWN):
        # Left button clicked down
        g_LastRot = copy.copy (g_ThisRot)               # // Set Last Static Rotation To Last Dynamic One
        g_isDragging = True                                            # // Prepare For Dragging
        mouse_pt = Point2fT (cursor_x, cursor_y)
        g_ArcBall.click (mouse_pt);                                # // Update Start Vector And Prepare For Dragging
    return



def Torus(MinorRadius, MajorRadius):        
    # // Draw A Torus With Normals
    glBegin( GL_TRIANGLE_STRIP );                                    # // Start A Triangle Strip
    for i in xrange (20):                                             # // Stacks
        for j in xrange (-1, 20):                                         # // Slices
            # NOTE, python's definition of modulus for negative numbers returns
            # results different than C's
            #       (a / d)*d  +  a % d = a
            if (j < 0):
                wrapFrac = (-j%20)/20.0
                wrapFrac *= -1.05
            else:
                wrapFrac = (j%20)/20.0;
            phi = PI2*wrapFrac;
            sinphi = sin(phi);
            cosphi = cos(phi);

            r = MajorRadius + MinorRadius*cosphi;

            glNormal3f (sin(PI2*(i%20+wrapFrac)/20.0)*cosphi, sinphi, cos(PI2*(i%20+wrapFrac)/20.0)*cosphi);
            glVertex3f (sin(PI2*(i%20+wrapFrac)/20.0)*r, MinorRadius*sinphi, cos(PI2*(i%20+wrapFrac)/20.0)*r);

            glNormal3f (sin(PI2*(i+1%20+wrapFrac)/20.0)*cosphi, sinphi, cos(PI2*(i+1%20+wrapFrac)/20.0)*cosphi);
            glVertex3f (sin(PI2*(i+1%20+wrapFrac)/20.0)*r, MinorRadius*sinphi, cos(PI2*(i+1%20+wrapFrac)/20.0)*r);
    glEnd();                                                        # // Done Torus
    return

def Draw ():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);                # // Clear Screen And Depth Buffer
    glLoadIdentity();  
    if 0:                                              # // Reset The Current Modelview Matrix
        glTranslatef(-1.5,0.0,-6.0);                                    # // Move Left 1.5 Units And Into The Screen 6.0
    
        glPushMatrix();                                                    # // NEW: Prepare Dynamic Transform
        glMultMatrixf(g_Transform);                                        # // NEW: Apply Dynamic Transform
        glColor3f(0.75,0.75,1.0);
        Torus(0.30,1.00);
        glPopMatrix();                                                    # // NEW: Unapply Dynamic Transform
    
        glLoadIdentity();                                                # // Reset The Current Modelview Matrix
        glTranslatef(0.0,0.0,-0.30);                                        # // Move Right 1.5 Units And Into The Screen 7.0

    glDisable(GL_LIGHTING)
    glDisable(GL_CULL_FACE)
    glPushMatrix();                                                    # // NEW: Prepare Dynamic Transform
    glMultMatrixf(g_Transform);                                        # // NEW: Apply Dynamic Transform
    glColor3f(1.0,0.75,0.75);
    glColor3f(1.0,1.0,1.0);
    #glDisable(GL_TEXTURE_2D)
    glEnable(GL_TEXTURE_2D)
    glBindTexture ( GL_TEXTURE_2D, g_textures[0] );
    if 1:
        gluSphere(g_quadratic,g_sphereRadius,50,50);
    else:
        glBegin(GL_QUADS);
        glColor4f(1.0,1.0,1.0,1.0); 
        glNormal3f(0,0,1); 
        glTexCoord2f(0,0); 	
        glVertex3f(-1,-1,0);
        glTexCoord2f(1,0);	
        glVertex3f(1,-1,0);
        glTexCoord2f(1,1);	
        glVertex3f(1,1,0);
        glTexCoord2f(0,1);	
        glVertex3f(-1,1,0);
        glEnd();    
    glBindTexture(GL_TEXTURE_2D, 0)
    glPopMatrix();                                                    # // NEW: Unapply Dynamic Transform

    glFlush ();                                                        # // Flush The GL Rendering Pipeline
    glutSwapBuffers()
    return

