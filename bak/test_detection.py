from numpy import *
import cv2
import kinect as kin

kinect = kin.Kinect()


cv2.namedWindow('depth')
cv2.namedWindow('color')

def on_mouse( event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global d_mark_xy
        d_mark_xy = x,y

cv2.setMouseCallback('depth', on_mouse)
d_mark_xy = None   


def coord_correction((x,y)):
    u = 15 + x*(1 - 30./480)
    v = 30 + y*(1 - 30./320)
    return u,v

   
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

    cv2.imshow( 'zero', (d_zero*255./4096).astype(uint8) )
    ##cv2.imshow( 'fluct', (d_fluct*255./4096).astype(uint8) )

        

    # Main loop
    print 'Loop...'
    while 1:

        d_data_16, rgb_data = kinect.read()
        
        d_data = d_data_16.astype(float)
        d_data_8 = (255./4096 * d_data_16).astype(uint8)

        
        # only masked pixels will be used
        floor_range = 250  ##400
        d_mask =  (d_data < d_zero - 10 - 2*d_fluct) # object nearer than on reference (-> above ground)
        ##d_mask =  (d_data < d_zero - 20) # object nearer than on reference (-> above ground)
        d_mask &= (d_data > d_zero - floor_range )  # object too far above ground
        d_mask &= (d_data != 0)  # drop invalid pixels

        ##kernel = ones( (3,3), uint8 )
        ke5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        ke3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        d_mask = cv2.morphologyEx(d_mask.astype(uint8), cv2.MORPH_OPEN, ke5)
        d_mask = cv2.dilate( d_mask, ke5 )
        
        ##d_data_16[ d_mask.astype(bool) ] = 0
        
        cv2.imshow( 'mask', (255.* d_mask).astype(uint8) ) 

        ##diff = ( - d_data_16.astype(float) + d_zero).clip(min=0)
        ##d_data_8 = (255./4096 * diff).astype(uint8)
        ##cv2.imshow( 'diff', (255./4096 * diff).astype(uint8) )


        m_, cont, hier = cv2.findContours(d_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cont:
            A = cv2.contourArea( c )
            ac = c[:,0]
            ##amin = argmax( ac[:,1] )
            ##xm,ym = ac[amin]
            maxy = max(ac[:,1])
            xm,ym = mean(ac[ac[:,1]>maxy-10], axis=0)
            min_area = 100
            if A > min_area:
                cv2.drawContours(rgb_data, [c], 0, (0,0,255), 2)  # accepted
                x1,y1 = coord_correction( (xm,ym) )
                cv2.circle( rgb_data, (int(x1),int(y1)), 30, (0,255,255), 2 )
                # Mark position in original image
            else:
                cv2.drawContours(rgb_data, [c], 0, (255,0,0), 2)  # rejected

        if d_mark_xy != None:
            x,y = d_mark_xy
            d16 = d_data_16[y,x]
            d8 = d_data_8[y,x]
            d_data_8[y, x-5:x+5] = 255
            d_data_8[y-5:y+5, x] = 255
            cv2.putText( d_data_8, '%d,%d: %d'%(x,y,d16), d_mark_xy,
                         cv2.FONT_HERSHEY_PLAIN, 1, 255 )

        cv2.imshow( 'depth', d_data_8 ) 
        cv2.imshow( 'color', rgb_data )

        key = cv2.waitKey(1)
        if key >= 0:
            if key == ord('q'): break
            if key == ord('s'):
                print 'Save frames'
                cv2.imwrite( 'depth.png', (255./4096 * d_data_16).astype(uint8) )
                cv2.imwrite( 'color.png', rgb_data )
        

finally:
    kinect.close()
    cv2.destroyAllWindows()
    
    