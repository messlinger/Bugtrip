
from numpy import *
import cv2, time, sys, os
import pygame
import kinect as kin


# Pygame stuff
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
W,H = 1024,768
fullscreen = 1  # overrides resolution

def ir(x):  # for convenience: transform scalar or list to int
    try: return [int(round(i)) for i in x]  # try to iterate
    except: return int(round(x))


#------------------------------------------------------------
try:
    # Camera 
    kinect = kin.Kinect()

    # Display window
    if fullscreen:
        screen = pygame.display.set_mode( (0,0), pygame.FULLSCREEN )
        W = pygame.display.Info().current_w
        H = pygame.display.Info().current_h
    else:
        screen = pygame.display.set_mode( (W,H) )
    pygame.display.set_caption("Image Calibration")
    screen.fill((0,0,0))
    pygame.display.flip()

    # Zero image
    for i in range(30): d_data_16, rgb_data = kinect.read()
    d_data_16, rgb_data = kinect.read()
    zero_img = cv2.flip( rgb_data, 1 ) # horizontally
    zero_img = cv2.cvtColor( zero_img, cv2.COLOR_BGR2GRAY)

    # Calibration points
    # Create on point after another
    nx, ny = 8, 6
    pt_orig = []
    pt_warped = []
    last_img = zero_img
    for y in range(H/ny/2, H, H/ny):
        for x in range(W/nx/2, W, W/nx):
            pt_orig.append( (x,y) )
            
            screen.fill((0,0,0))
            pygame.draw.circle( screen, (255,255,255), ir((x,y)), 40, 0 )
            pygame.display.flip()
            
            for i in range(15):
                d_data_16, rgb_data = kinect.read()
            new_img = cv2.flip( rgb_data, 1 ) # horizontally
            new_img = cv2.cvtColor( new_img, cv2.COLOR_BGR2GRAY )
            diff_img = cv2.subtract( new_img, zero_img )
            
            diff_img = cv2.medianBlur( diff_img, 5 )
            diff_img = (diff_img*255./diff_img.max()).astype(uint8)
            cv2.imwrite( 'img/cal_%d_%d.png' % (x,y), diff_img )
            
            ##th_img = cv2.adaptiveThreshold( diff_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, 0)
            r,th_img = cv2.threshold(diff_img, 200, 255, cv2.THRESH_BINARY)
            thimg_, cont, hier = cv2.findContours( th_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE )
            Amax, xw, yw = 0, 0, 0
            for c in cont:
                A = cv2.contourArea(c)
                if A>Amax:
                    (xw,yw),ax,ang = cv2.fitEllipse(c)
            if (xw,yw)==(0,0):
                raise Exception('Error at point %d,%d:' % (x,y) + 'Cannot find image point')
            pt_warped.append( (xw,yw) )
                    


    # Calibration image (only for test)
    circles = cv2.imread('circles.png')
    r, pts =   cv2.findCirclesGrid( circles, (8,6) )  # in the original image
    
    # Get screen transformation
    cam_to_scr, mask = cv2.findHomography( array(pt_warped), array(pt_orig) )

    # Save transformation matrix
    savetxt('calib_projection.dat', cam_to_scr)


    #---Show feedback image until program is killed---

    nframes = 0       # total number of acquired frames
    t0 = time.time()  # start time

    # Acquisition loop
    while 1:

        # Pygame events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or \
                   event.key == pygame.K_ESCAPE:
                    break
            if event.type == pygame.QUIT:
                break


        # Read next image from camera
        d_data_16, rgb_data = kinect.read()

        # Transform to screen 
        img = cv2.flip( rgb_data,  1 )
        img = cv2.warpPerspective( img, cam_to_scr, (W,H) )
        
        # Show image
        A = 1.0
        img = cv2.addWeighted( img, A, img, 0, 0 )
        pygame_img = pygame.image.frombuffer( img.tostring(), (W,H), "RGB" )
        screen.blit( pygame_img, pygame.Rect(0,0,W,H) )
        pygame.display.flip()

        # Calculate average framerate
        nframes += 1
        if nframes%100 == 0:
            t = time.time()
            print 'frames/sec =', nframes/(t-t0)
            t0 = t
            nframes = 0


finally: # Clean up
    kinect.close()
    pygame.quit()



    




