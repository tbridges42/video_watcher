import configparser
import daemon
import logging
import signal
import sys
import listener
from os import access, R_OK
from os.path import isfile
from argparse import ArgumentParser

# TODO: Use queue logging
# TODO: Set up email and remote logging

DEFAULT_CONFIG = 'config.ini'
DEFAULT_LOGFILE = 'watcher.log'
DEFAULT_CONSOLE_VERBOSITY = logging.DEBUG
DEFAULT_LOGFILE_VERBOSITY = logging.INFO
DEFAULT_HOSTNAME = ''
DEFAULT_PORT = "9191"
DEFAULT_CERT = ""
DEFAULT_KEY = ""


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    Stolen from 'Link Electric Monk
    <http://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/>
    """

    def __init__(self, mylogger, log_level=logging.INFO):
        self.logger = mylogger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

    def fileno(self):
        return 0


def get_args():
    argparser = ArgumentParser(prog="Watcher",
                               description="A server for processing incoming webcam footage.",
                               epilog="Command line options override values in the config file")
    argparser.add_argument('-c', '--config', default=DEFAULT_CONFIG, help="Define a custom config file.")
    argparser.add_argument('-d', '--daemon', action='store_true', help="Spawn a daemon.")
    # TODO: Implement
    argparser.add_argument('-l', '--logfile', help="Location to log messages.")
    # TODO: Implement
    argparser.add_argument('-v', '--verbose', action='count')
    # TODO: Implement
    argparser.add_argument('-H', '--host', help="The server hostname.")
    # TODO: Implement
    argparser.add_argument('-p', '--port', help="The port to use.")
    # TODO: Implement
    # SSL is set via option list to allow for a None value, in which case we read from the config file
    argparser.add_argument('-s', '--ssl', choices=['y', 'n'], help="Require SSL.")
    # TODO: Implement
    argparser.add_argument('-C', '--cert', help="SSL cert file to use.")
    # TODO: Implement
    argparser.add_argument('-k', '--key', help="SSL key file to use.")
    return argparser.parse_args()


def spawn_daemon(file_handlers=None):
    context = daemon.DaemonContext(working_directory=".",
                                   files_preserve=file_handlers)
    context.signal_map = { signal.SIGTERM: halt }
    context.open()


def create_config(path, parser):
    # TODO: Create default config
    parser['watcher'] = {}
    parser['watcher']['logfile'] = DEFAULT_LOGFILE
    parser['watcher']['logfile_level'] = "INFO"
    parser['watcher']['hostname'] = DEFAULT_HOSTNAME
    parser['watcher']['port'] = DEFAULT_PORT
    parser['watcher']['ssl'] = "True"
    parser['watcher']['key'] = DEFAULT_KEY
    parser['watcher']['cert'] = DEFAULT_CERT
    with open(path, 'w') as configfile:
        parser.write(configfile)


def merge_two_dicts(x, y):
    """
    Given two dicts, merge them into a new dict as a shallow copy.
    """
    y = {k: v for k, v in y.items() if v is not None}
    z = x.copy()
    z.update(y)
    return z


def halt(signum, frame):
    logging.getLogger('watcher').warning("Received shutdown signal")
    listener.halt()
    logging.getLogger('watcher').info("==================================\n")


def setup_logger(options):
    logger = logging.getLogger('watcher')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)8s - %(message)s')

    fh = logging.FileHandler(options['logfile'])
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.debug("Logger created")

    # sys.stdout = StreamToLogger(logger, logging.DEBUG)
    # sys.stderr = StreamToLogger(logger, logging.DEBUG)
    logger.debug("stdout and stderr routed to logger")

    return [fh.stream]


def main():
    args = get_args()
    parser = configparser.ConfigParser()
    path = args.config
    if not (isfile(path) and access(path, R_OK)):
        print(path + " is not a valid config file. Creating " + DEFAULT_CONFIG)
        create_config(DEFAULT_CONFIG, parser)
        path = DEFAULT_CONFIG
    parser.read(path)
    options = merge_two_dicts(dict(parser.items('watcher')), vars(args))
    logging_files = setup_logger(options)
    logging.getLogger('watcher').info("==================================")
    logging.getLogger('watcher').info("Started Watcher")
    logging.getLogger('watcher').info("Set up logging")
    if options['daemon']:
        spawn_daemon(file_handlers=logging_files)
        logging.getLogger('watcher').info("Split off daemon")
    listener.setup(options)


if __name__ == '__main__':
    main()
