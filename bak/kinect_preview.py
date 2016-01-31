from numpy import *
import cv2
import kinect as kin

devs = kin.list_devices()
if devs: print 'Devices:', devs
else: print 'No NI device found'; exit()

kinect = kin.Kinect()


cv2.namedWindow('depth')
cv2.namedWindow('color')

def on_mouse( event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print 'mouse'
        global d_mark_xy
        d_mark_xy = x,y

cv2.setMouseCallback('depth', on_mouse)
d_mark_xy = None   

   
try:
    while 1:

        d_data_16, rgb_data = kinect.read()
        d_data_8 = (255./4096 * d_data_16).astype(uint8)
        

        if d_mark_xy != None:
            x,y = d_mark_xy
            d16 = d_data_16[y,x]
            d_data_8[y, x-5:x+5] = 255
            d_data_8[y-5:y+5, x] = 255
            cv2.putText( d_data_8, '%d'%d16, d_mark_xy, cv2.FONT_HERSHEY_PLAIN, 1, 255 )

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
    
    