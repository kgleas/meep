#! /usr/bin/env python
import sys
import socket
import miniapp
import datetime
initialize()
app = MeepExampleApp()
app.override_authentication = True

def handle_connection(sock):
    index = 0;
    data = ''
    while 1:
        try:
            d = sock.recv(1)
            data += d;
            if data[-4:] == "\r\n\r\n":
                break
            if not data:
                break

        except socket.error:
            return

    data = miniapp.format_return(data)

    data = str(data)

    sock.sendall(data)
    sock.close()

if __name__ == '__main__':
    port = 8000
    interface = 'localhost'
    

    print 'Binding', interface, port
    sock = socket.socket()
    sock.bind( (interface, port) )
    sock.listen(5)

    while 1:
        print 'waiting...'
        (client_sock, client_address) = sock.accept()
        print 'got connection', client_address
        handle_connection(client_sock)
