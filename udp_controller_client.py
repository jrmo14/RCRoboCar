import six.moves.cPickle as cP
import socket
import controller_reader
import time
# Create a UDP socket
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# server_address = ('localhost', 7777)
# # message = b'This is the message.  It will be repeated.'
# message = (1, "hello")
# message = cP.dumps(message)


class ControllerClient:

    def __init__(self, server_address, port, controller_port=0, delay=0.05, debug=False,
                 invert_x=False, invert_y=False):

        self.controller_reader = controller_reader.ControllerReader(controller_port)
        self._address = server_address
        self._port = port
        self.init_time = time.time()
        self.delay = delay
        self.sock = None
        self.debug = debug
        self.x_sign = -1 if invert_x else 1
        self.y_sign = -1 if invert_y else 1

    def send_message(self, msg):
        self.sock.sendto(msg, (self._address, self._port))

    def run(self):
        try:
            print("connecting...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("Connected to socket")
            while True:
                # These return a value of -1 to 1
                # self.controller_reader.update_events()
                # dunno which is x or y
                turn = self.controller_reader.joystick.get_axis(0) * self.x_sign
                power = self.controller_reader.joystick.get_axis(1) * self.y_sign

                if self.debug:
                    print("Turn:", turn)
                    print("Power:", power)

                message = (power, turn, time.time() - self.init_time)

                message_enc = cP.dumps(message)
                self.sock.sendto(message_enc, (self._address, self._port))

                time.sleep(self.delay)
        finally:
            self.sock.close()


if __name__ == '__main__':
    client = ControllerClient("localhost", 7777, debug=True, controller_port=2, invert_y=True)
    client.run()
