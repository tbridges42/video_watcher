import logging
import multiprocessing
import os
import socket
import ssl
import datetime

terminate = False
logger = logging.getLogger("watcher")


def handle(connection):
    try:
        logger.debug("In do_stuff")
        datestamp = datetime.datetime.now().isoformat()
        logger.debug("Got datetime")
        with open(datestamp + ".h264", "wb") as file:
            logger.debug("Opened file")
            data = connection.recv(1024)
            logger.debug("Received first chunk")
            while data and not terminate:
                file.write(data)
                data = connection.recv(1024)
                logging.getLogger("watcher").debug("Receiving...")
            stats = os.stat(file.fileno())
            logging.getLogger("watcher").info("Wrote " + str(stats.st_size) + " bytes to " + file.name)
    except:
        logger.exception("Problem handling request")
    finally:
        connection.close()




def setup(config):
    logging.debug("In setup")
    hostname = config['hostname']
    if not hostname:
        hostname = ''
    port = config['port']
    certfile = config['cert']
    keyfile = config['key']
    sslcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sslcontext.options |= ssl.OP_NO_SSLv2
    sslcontext.options |= ssl.OP_NO_SSLv3
    sslcontext.load_cert_chain(certfile, keyfile)
    sock = socket.socket()
    sock.bind((hostname, int(port)))
    sock.listen(5)
    if hostname:
        logging.getLogger('watcher').info("Listening on " + hostname + ":" + port)
    else:
        logging.getLogger('watcher').info("Listening on port " + port)
    while not terminate:
        newsocket, fromaddr = sock.accept()
        logging.getLogger('watcher').info("Received connection")
        connection = sslcontext.wrap_socket(newsocket, server_side=True)
        logging.getLogger('watcher').info("SSL established")
        try:
            process = multiprocessing.Process(target=handle, args=(connection,))
            process.daemon = True
            process.start()
        except Exception as error:
            logging.getLogger('watcher').critical(error)
        finally:
            logging.getLogger('watcher').info("Terminating server")
            logging.getLogger('watcher').info("==================================\n")
            logging.shutdown()
            handlers = logger.handlers
            for handler in handlers:
                handler.close()
                logger.removeHandler(handler)


def halt():
    global terminate
    terminate = True
