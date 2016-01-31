from numpy import *
import cv2, pygame, os
import kinect as kin

kinect = kin.Kinect()


# Pygame stuff
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
W,H = 1024,768
fullscreen = 1  # overrides resolution

def ir(x):  # for convenience: transform scalar or list to int
    try: return [int(round(i)) for i in x]  # try to iterate
    except: return int(round(x))


cam_to_scr = loadtxt('calib_projection.dat')

def transform_cam_to_scr( (x,y) ):
    a = cv2.perspectiveTransform( array((((1.*x,1.*y),),)), cam_to_scr )  # XXX needs a 3 dim float array
    u,v = a[0][0] # and also returns a 3 dim array
    return u,v


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

   
try:

    # Zero image
    print 'Zero image...'
    n_zero = 100
    images = []
    for i in range(n_zero):
        d_data_16, rgb_data = kinect.read()
        images.append( d_data_16.astype(float) )
    images = array(images)

    d_zero = sum( images, axis=0 )    # zero image
    n_zero = sum( images>0, axis=0 )  # number of usable images (depth > 0)
    d_zero /= n_zero

    d_fluct = images.max( axis=0 ) - d_zero  # fluctuation (don't use min, may be zero on invalid pixels)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
    d_fluct = cv2.dilate( d_fluct, kernel )  # spread error estimation a little

    
    # Main loop
    print 'Loop...'
    run = 1
    while run:

         # Pygame events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or \
                   event.key == pygame.K_ESCAPE:
                    run = 0
            if event.type == pygame.QUIT:
                run = 0
        if not run: break

        # Clear playground
        screen.fill((0,0,0))

        d_data_16, rgb_data = kinect.read()
        
        d_data = d_data_16.astype(float)
        d_data_8 = (255./4096 * d_data_16).astype(uint8)

        
        # only masked pixels will be used
        floor_range = 250
        d_mask =  (d_data < d_zero - 10 - 2*d_fluct) # object nearer than on reference (-> above ground)
        ##d_mask =  (d_data < d_zero - 20) # object nearer than on reference (-> above ground)
        d_mask &= (d_data > d_zero - floor_range )  # object too far above ground
        d_mask &= (d_data != 0)  # drop invalid pixels

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        d_mask = cv2.morphologyEx(d_mask.astype(uint8), cv2.MORPH_OPEN, kernel)
        
        m_, cont, hier = cv2.findContours(d_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cont:
            A = cv2.contourArea( c )

            # Centroid
            M = cv2.moments(c)
            xc, yc = M['m10']/M['m00'], M['m01']/M['m00']

            # Lower bound
            ac = c[:,0]
            maxy = max(ac[:,1])
            xm,ym = mean(ac[ac[:,1]>maxy-10], axis=0)
            xm = d_data.shape[1]-1-xm
            xm,ym = transform_cam_to_scr( (xm,ym) )

            # Convert to playground coordinates
            xc = d_data.shape[1]-1-xc # image was calibrated flipped
            xc,yc = transform_cam_to_scr( (xc,yc) )

            min_area = 200
            if A > min_area:  # accepted
                pygame.draw.circle( screen, (255,255,255), ir((xm,ym)), 60, 0 )
                pygame.draw.circle( screen, (255,0,0), ir((xm,ym)), 60, 2 )
            else:   # rejected
                pygame.draw.circle( screen, (0,0,255), ir((xm,ym)), 60, 0 )

        pygame.draw.rect( screen, (255,255,255), (0,0,W,H), 10 )
        pygame.display.flip()

        key = cv2.waitKey(1)
        if key >= 0:
            if key == ord('q'): break
            if key == ord('s'):
                print 'Save frames'
                cv2.imwrite( 'depth.png', (255./4096 * d_data_16).astype(uint8) )
                cv2.imwrite( 'color.png', rgb_data )
        

finally:
    kinect.close()
    pygame.quit()
    
    