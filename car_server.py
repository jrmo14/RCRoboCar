import socket
import serial
import cv2
import numpy as np
import bcolz
import six.moves.cPickle as cP
import struct
from time import sleep


class CarServer:
    def __init__(self, server_address, server_port, arduino_port, camera_port=0, ramp_frames=30, x_dim=240, y_dim=240,
                 save_loc='/home/nvidia/train_data/'):
        """
        General setup
        Need to figure out what the location of the arduino is
        figure out what the address is and what no
        """
        self.server_addr = server_address
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((server_address, server_port))

        self.save_loc = save_loc

        self.camera_port = camera_port
        self.ramp_frames = ramp_frames
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.camera = cv2.VideoCapture(self.camera_port)

        self.ser = serial.Serial(port=arduino_port)
        self.frames_captured = 0
        self.written_sets = 0
        self.images_shape = (50, self.x_dim, self.y_dim, 3)
        self.labels_shape = (50, 2)
        self.images_buffer = np.ndarray(self.images_shape)
        self.labels_buffer = np.ndarray(self.labels_shape)
        print(
            "Opened socket at {} on port {}, started communications with arduino at {}".format(server_address,
                                                                                               server_port,
                                                                                               self.ser.port))

    # We should receive a float between -1 and 1
    def handle_controls(self):
        data, addr = self.sock.recvfrom(4096)
        forward, turn, time = cP.loads(data)
        # Arduino is expecting int between -100 and 100
        forward = int(forward * 100)
        turn = int(turn * 100)
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
        self.images_buffer[self.frames_captured] = im
        self.labels_buffer[self.frames_captured] = np.asarray((forward, turn))
        self.frames_captured += 1
        if self.frames_captured == 50:
            np.save(self.save_loc + str(self.written_sets) + 'data', self.images_buffer)
            np.save(self.save_loc + str(self.written_sets) + 'labels', self.labels_buffer)
            self.images_buffer = np.empty(self.images_shape)
            self.labels_buffer = np.empty(self.labels_shape)
            self.frames_captured = 0

    # Jank AF event handling
    def __wait_for_connections(self):
        while 1:
            data, addr = self.sock.recvfrom(4096)
            if data == 'r':
                break
            sleep(.001)
        while 1:
            self.ser.write('r')
            if self.ser.read() == 'r':
                return
            sleep(.001)

    def run(self):
        self.__wait_for_connections()

        while True:
            forward, turn = self.handle_controls()
            self.write_image_and_controls(forward, turn)


server = CarServer("roboCar", 7777, "")

server.run()
