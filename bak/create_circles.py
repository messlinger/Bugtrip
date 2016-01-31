
import cv2
from numpy import *

width, height = 1024, 768
nx, ny = 8, 6  # faces = dots+1 

img = full( (height, width, 3), 255 , dtype=uint8 )

for y in range(height/ny/2, height, height/ny):
    for x in range(width/nx/2, width, width/nx):
        cv2.circle(img, (x,y), 10, 0, -1 )

cv2.imwrite('circles.png', img)
