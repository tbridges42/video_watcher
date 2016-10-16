import socket
import ssl


terminate = False


def do_stuff(connection):
    with open("servertest.h264", "wb") as file:
        data = connection.recv(1024)
        while data and not terminate:
            file.write(data)
            data = connection.recv(1024)


def setup(config):
    print("In setup")
    hostname = config['hostname']
    if not hostname:
        hostname = ''
    port = config['port']
    certfile = config['cert']
    keyfile = config['key']
    print(hostname + ":" + port)
    sslcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sslcontext.options |= ssl.OP_NO_SSLv2
    sslcontext.options |= ssl.OP_NO_SSLv3
    sslcontext.load_cert_chain(certfile, keyfile)
    sock = socket.socket()
    sock.bind((hostname, int(port)))
    sock.listen(5)
    print("Bound socket")
    while not terminate:
        newsocket, fromaddr = sock.accept()
        connection = sslcontext.wrap_socket(newsocket, server_side=True)

        try:
            do_stuff(connection)
        finally:
            connection.shutdown(socket.SHUT_RDWR)
            connection.close()


def halt():
    global terminate
    terminate = True
