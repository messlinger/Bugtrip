from numpy import *
import cv2
from primesense import openni2 as ni2

ni2.initialize('C:\Programming\OpenNI2\Redist')        


def list_devices():
    return ni2.Device.enumerate_uris()


class Kinect:
    dev = None
    def __init__(self):
        self.dev = ni2.Device.open_any()
        self.dev.set_depth_color_sync_enabled(1)
        self.d_stream = self.dev.create_depth_stream()
        self.rgb_stream = self.dev.create_color_stream()
        self.d_stream.start()
        self.rgb_stream.start()

    def close(self):
        if self.dev != None:
            self.d_stream.stop()
            self.rgb_stream.stop()
            self.dev.close()
            self.dev = None

    def __del__(self):
        self.close()

    def read(self):
        d_frame = self.d_stream.read_frame()
        d_buffer_16 = d_frame.get_buffer_as_uint16()
        d_data_16 = frombuffer( d_buffer_16, dtype=uint16 )
        d_data_16.shape = d_frame.height, d_frame.width
        
        rgb_frame = self.rgb_stream.read_frame()
        rgb_buffer = rgb_frame.get_buffer_as_triplet()
        rgb_data = frombuffer( rgb_buffer, dtype=uint8 )
        rgb_data.shape = rgb_frame.height, rgb_frame.width, 3
        rgb_data = cv2.cvtColor( rgb_data, cv2.COLOR_RGB2BGR )

        return d_data_16, rgb_data
