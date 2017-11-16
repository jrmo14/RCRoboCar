import six.moves.cPickle as cP
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = 'localhost'
server_port = 7777

print('Starting up on {} on port {}'.format(server_address, server_port))
sock.bind((server_address, server_port))

while True:
    print('waiting for data')
    data, addr = sock.recvfrom(4096)
    data = cP.loads(data)
    print('Received {} bytes from {}'.format(len(data), addr))

    print(data)

    if data[0]:
        sent = sock.sendto(cP.dumps(data), addr)
        print('Sent {} bytes back to {}'.format(sent, addr))
