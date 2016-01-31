import pygame
pygame.init()
from math import sqrt, pi, tan, sin, cos, atan2
from helper import ir


class MovingSprite(pygame.sprite.Sprite):
    x,y = None, None     # Position
    vx,vy = None, None   # Velocity in pix/second
    base_image = None   # Unrotated
    base_orientation = None  # Orientation of base_image
    image = None  # Rotated
    img_orientation = None  # Current orientation
    orientation_offs = 0
    

    def __init__(self, (x,y)=(0,0), (vx,vy)=(0,0),
                 image=None, img_orientation=0 ):

        super(MovingSprite, self).__init__()

        # Default image
        if self.base_image == None:
            self.base_image = pygame.Surface((40,40)).convert_alpha()
            self.base_image.fill( (255,0,0) )
            self.base_orientation = 0
        else:
            self.base_image = image
            self.base_orientation = img_orientation

        self.image = self.base_image
        self.img_orientation = self.base_orientation
        self.rect = self.image.get_rect()
        self.set_pos( x,y )
        self.set_vel( vx,vy )

    def set_pos(self, xy, y=None):
        if y==None: x,y = xy
        else: x,y = xy, y
        self.x, self.y = x,y
        self.rect.x = ir(x - self.rect.w/2.)
        self.rect.y = ir(y - self.rect.h/2.)
    
    def set_vel(self, vxy, vy=None):
        if vy==None: vx,vy = vxy
        else: vx, vy = vxy, vy
        self.vx, self.vy = vx, vy
        # Rotate image to match motion direction if necessary
        phi = atan2(self.vy, self.vx) + self.orientation_offs
        if abs(phi - self.img_orientation) > 0.003:  # (approx. 02 deg)
            self.image = pygame.transform.rotate( self.base_image,
                                -(phi*180./pi - self.base_orientation) )
            self.img_orientation = phi
            self.rect = self.image.get_rect()
            self.set_pos( self.x, self.y )

    set_velocity = set_vel

    def speedup(self, fact):
        self.set_vel( fact*self.vx, fact*self.vy )

    def rotate_vel(self, angle, absolute=0):
        """Rotate velocity direction by angle (in rad) while preserving the absolute velocity.
        absolute=0 only rotates by a angle relative to the current direction,
        absolute=1 sets a new absolute velocity direction angle."""
        if absolute:
            va = sqrt(self.vx**2 + self.vy**2)
            vx, vy = va*cos(angle), va*sin(angle)
        else:
            vx = cos(angle)*self.vx - sin(angle)*self.vy
            vy = sin(angle)*self.vx + cos(angle)*self.vy
        self.set_vel( vx, vy )

    def set_orientation(self, angle):
        """Set an orientation offset angle."""
        self.orientation_offs = angle
        
    def update(self, dt=1., world=None):
        # Motion integration step
        self.set_pos( self.x + self.vx*dt, self.y + self.vy*dt )
        if world != None:
            W, H = world.W, world.H
            if self.x<0:
                self.set_pos( -self.x, self.y)
                self.set_vel( -self.vx, self.vy )
            if self.x>W:
                self.set_pos(2*W-self.x, self.y)
                self.set_vel( -self.vx, self.vy )
            if self.y<0:
                self.set_pos( self.x, -self.y)
                self.set_vel( self.vx, -self.vy )
            if self.y>H:
                self.set_pos( self.x, 2*H-self.y)
                self.set_vel( self.vx, -self.vy )
