import socket
import serial
import cv2
import numpy as np
import bcolz
import six.moves.cPickle as cP
import struct


class RemoteServer:
    def __init__(self):
        # General setup
        # Need to figure out what the location of the arduino is
        ard_port = ""
        self.ser = serial.Serial(port=ard_port)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # figure out what the address is and what no
        server_addr = "roboCar"
        server_port = 1337
        self.sock.bind((server_addr, server_port))

        self.camera_port = 0
        self.ramp_frames = 30
        self.camera = cv2.VideoCapture(self.camera_port)
        self.x_dim = 240
        self.y_dim = 240

        self.forward = 0
        self.turn = 0
        self.frames_captured = 0
        self.written_sets = 0
        self.images_and_data = np.ndarray([50, 1, self.x_dim, self.y_dim, 3])

        print(
            "Opened socket at {} on port {}, started communications with arduino at {}".format(server_addr, server_port,
                                                                                               self.ser.port))

    def handle_controls(self):
        data, addr = self.sock.recvfrom(4096)
        self.forward, self.turn = data
        data = cP.loads(data)
        self.forward = data[0]
        self.turn = data[1]
        self.ser.write(struct.pack(">B", self.forward))
        self.ser.write(struct.pack(">B", self.turn))

    def write_array(self, arr, fname):
        c = bcolz.carray(arr, rootdir=fname, mode='w')
        c.flush()

    def write_image_and_controls(self):
        retval, im = self.camera.read()
        im = cv2.resize(im, (self.x_dim, self.y_dim))
        # This could be completely wrong, each element should be [(forward, turn), image]
        # image is 240 x 240 x 3 array
        self.images_and_data[self.frames_captured, 0] = np.ndarray((self.forward, self.turn), im)
        self.frames_captured += 1
        if self.frames_captured == 50:
            self.write_array(self.images_and_data, str(self.written_sets) + '.bcz')
            self.frames_captured = 0

    def run(self):
        while True:
            self.handle_controls()
            self.write_image_and_controls()


server = RemoteServer()

server.run()
