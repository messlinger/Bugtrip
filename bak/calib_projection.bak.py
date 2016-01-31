
from numpy import *
import cv2, time, sys
import kinect as kin

W,H = 1024, 768 # Window size
Wscr,Hscr = 1280, 1024  # Screen size

if sys.platform=='win32':
    from win32api import GetSystemMetrics
    Ws,Hs = GetSystemMetrics(0), GetSystemMetrics(1)


#------------------------------------------------------------
try:
    # Camera 
    kinect = kin.Kinect()

    # Display window
    cv2.namedWindow('frame')
    cv2.resizeWindow('frame', W, H)
    cv2.moveWindow( 'frame', (Wscr-W)/2, (Hscr-H)/2 )
    cv2.imshow('frame', zeros((H,W), dtype=uint8) )
    cv2.waitKey(1)  # required to show window

    # Zero image
    for i in range(30): d_data_16, rgb_data = kinect.read()
    d_data_16, rgb_data = kinect.read()
    zero_img = cv2.flip( rgb_data, 1 ) # horizontally
    zero_img = cv2.cvtColor( zero_img, cv2.COLOR_BGR2GRAY)

    # Load calibration image
    circles = cv2.imread('circles.png')
    cv2.imshow('frame', circles)
    cv2.waitKey(1)

    # Read camera image
    time.sleep(0.2)
    for i in range(30): d_data_16, rgb_data = kinect.read()
    d_data_16, rgb_data = kinect.read()
    circles2 = cv2.flip( rgb_data, 1 ) # horizontally
    circles2 = cv2.cvtColor( circles2, cv2.COLOR_BGR2GRAY)
    circles2 = cv2.subtract( circles2, zero_img )
    cv2.imwrite('diff.png', circles2)
    

    # Get screen transformation
    r, pts =   cv2.findCirclesGrid( circles, (8,6) )  # in the original image
    r2, pts2 = cv2.findCirclesGrid( circles2, (8,6) ) # in the camera image
    if not r*r2: raise Exception('### Error getting calibration points')
    cam_to_scr, mask = cv2.findHomography( pts2, pts )

    # Save transformation matrix
    savetxt('calib_projection.dat', cam_to_scr)


    #---Show feedback image until program is killed---

    cv2.imshow('frame', zeros((H,W,3), dtype=uint8) )
    cv2.waitKey(1)
    for i in range(10): cap.read()

    nframes = 0       # total number of acquired frames
    t0 = time.time()  # start time

    # Acquisition loop
    while 1:
        # Read next image from camera
        ret, img = cap.read()
        if not ret: raise Exception("Camera error")

        # Transform to screen 
        img = cv2.flip( img,  -1 )  # rotate
        img = cv2.warpPerspective( img, cam_to_scr, (W,H) )
        
        # Show image
        A = 1.0
        img = cv2.addWeighted( img, A, img, 0, 0 )
        cv2.imshow('frame', img)

        # Calculate average framerate
        nframes += 1
        if nframes%100 == 0:
            t = time.time()
            print 'frames/sec =', nframes/(t-t0)
            t0 = t
            nframes = 0

        # Image window events
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        if key == ord('s'):
            print 'Save frame'
            cv2.imwrite('frame.png',img)

finally: # Clean up
    kinect.close()
    cv2.destroyAllWindows()



    