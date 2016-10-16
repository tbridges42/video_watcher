import configparser
import daemon
import logging
from os import access, R_OK
from os.path import isfile
from argparse import ArgumentParser

# TODO: Use queue logging
# TODO: Set up email and remote logging

DEFAULT_CONFIG = 'config.ini'
DEFAULT_LOGFILE = '/var/log/watcher/log'
DEFAULT_CONSOLE_VERBOSITY = logging.ERROR
DEFAULT_LOGFILE_VERBOSITY = logging.INFO
DEFAULT_HOSTNAME = ''
DEFAULT_PORT = "9191"
DEFAULT_CERT = ""
DEFAULT_KEY = ""


def get_args():
    argparser = ArgumentParser(prog="Watcher",
                               description="A server for processing incoming webcam footage.",
                               epilog="Command line options override values in the config file")
    argparser.add_argument('-c', '--config', default=DEFAULT_CONFIG, help="Define a custom config file.")
    argparser.add_argument('-d', '--daemon', action='store_true', help="Spawn a daemon.")
    # TODO: Implement
    argparser.add_argument('-l', '--logfile', default=DEFAULT_LOGFILE, help="Location to log messages.")
    # TODO: Implement
    argparser.add_argument('-H', '--host', default=DEFAULT_HOSTNAME,
                           help="The server hostname. If not present, will use the system hostname")
    # TODO: Implement
    # SSL is set via option list to allow for a None value, in which case we read from the config file
    argparser.add_argument('-s', '--ssl', choices=['y', 'n'], help="Require SSL.")
    # TODO: Implement
    argparser.add_argument('-p', '--port', help="The port to use.")
    # TODO: Implement
    argparser.add_argument('-C', '--cert', help="SSL cert file to use.")
    # TODO: Implement
    argparser.add_argument('-k', '--key', help="SSL key file to use.")
    return argparser.parse_args()


def spawn_daemon():
    print("getting context")
    out = open("watcher.log", "w+")
    context = daemon.DaemonContext(stdout=out, stderr=out, working_directory="/home/kodi/")
    # TODO: set up daemon parameters
    print("opening context")
    context.open()
    print("In daemon")


def create_config(path, parser):
    # TODO: Create default config
    parser['watcher'] = {}
    parser['watcher']['hostname'] = ""
    parser['watcher']['port'] = "9191"
    parser['watcher']['key'] = "server.key"
    parser['watcher']['cert'] = "server.crt"
    with open(path, 'w') as configfile:
        parser.write(configfile)


def main():
    print("starting")
    args = get_args()
    parser = configparser.ConfigParser()
    path = args.config
    if not (isfile(path) and access(path, R_OK)):
        create_config(path, parser)
    parser.read(path)
    if args.daemon:
        print("spawning")
        spawn_daemon()
    import listener
    listener.setup(parser)


if __name__ == '__main__':
    main()
