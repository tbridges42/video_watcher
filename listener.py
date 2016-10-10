import socket
import ssl


def setup(config):
    hostname = config['watcher']['hostname']
    port = config['watcher']['port']
    certfile = config['watcher']['cert']
    keyfile = config['watcher']['key']
    sslcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sslcontext.options |= ssl.OP_NO_SSLv2
    sslcontext.options |= ssl.OP_NO_SSLv3
    sslcontext.load_cert_chain(certfile, keyfile)
    sock = socket.create_connection((hostname, port))
    sslcontext.wrap_socket(sock, server_side=True)

    sock.listen(1)

