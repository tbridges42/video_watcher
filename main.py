import configparser
import daemon
from os import access, R_OK
from os.path import isfile
from argparse import ArgumentParser


def get_args():
    argparser = ArgumentParser(prog="Watcher",
                               description="A server for processing incoming webcam footage.")
    argparser.add_argument('-c', '--config', default='config.ini', help="Optionally define a custom config file.")
    argparser.add_argument('-d', '--daemon', action='store_true', help="If present, spawn a daemon.")
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
