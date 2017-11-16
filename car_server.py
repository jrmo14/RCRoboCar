import socket
import serial
import cv2
import numpy as np
import bcolz
import six.moves.cPickle as cP
import struct


class RemoteServer:
    def __init__(self, server_address, server_port, arduino_port, camera_port=0, ramp_frames=30, x_dim=240, y_dim=240):
        """
        General setup
        Need to figure out what the location of the arduino is
        figure out what the address is and what no
        """
        self.server_addr = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((server_address, server_port))

        self.camera_port = camera_port
        self.ramp_frames = ramp_frames
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.camera = cv2.VideoCapture(self.camera_port)

        self.ser = serial.Serial(port=arduino_port)
        self.frames_captured = 0
        self.written_sets = 0
        self.images_and_data = np.ndarray([50, 1, self.x_dim, self.y_dim, 3])

        print(
            "Opened socket at {} on port {}, started communications with arduino at {}".format(server_address,
                                                                                               server_port,
                                                                                               self.ser.port))

    # We should receive a float between -1 and 1
    def handle_controls(self):
        data, addr = self.sock.recvfrom(4096)
        forward, turn, time = cP.loads(data)

        self.ser.write(struct.pack(">BB", forward, turn))
        return forward, turn

    @staticmethod
    def write_array(arr, fname):
        c = bcolz.carray(arr, rootdir=fname, mode='w')
        c.flush()

    def write_image_and_controls(self, forward, turn):
        retval, im = self.camera.read()
        im = cv2.resize(im, (self.x_dim, self.y_dim))
        # This could be completely wrong, each element should be [(forward, turn), image]
        # image is 240 x 240 x 3 array
        self.images_and_data[self.frames_captured, 0] = np.ndarray((forward, turn), im)
        self.frames_captured += 1
        if self.frames_captured == 50:
            self.write_array(self.images_and_data, str(self.written_sets) + '.bcz')
            self.frames_captured = 0

    def run(self):
        while True:
            forward, turn = self.handle_controls()
            self.write_image_and_controls(forward, turn)


server = RemoteServer("roboCar", 1337, "")

server.run()
