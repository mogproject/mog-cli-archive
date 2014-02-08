#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""Command Line Interface for CSA Shogi Client"""


import sys
import argparse
import logging
from shell import Shell
from util.logger import logger


def main():
    # parse arguments
    parser = argparse.ArgumentParser(prog='mog_cli', description='Command line interface for CSA shogi client')
    parser.add_argument('-H', '--host', metavar='DEFAULT_HOST', default='localhost',
                        help='default host of shogi-server')
    parser.add_argument('-P', '--port', metavar='DEFAULT_PORT', default=4081, type=int,
                        help='default port of shogi-server')
    parser.add_argument('-u', dest='username', metavar='DEFAULT_USERNAME', help='default login username')
    parser.add_argument('-p', dest='password', metavar='DEFAULT_PASSWORD', help='default login password')
    parser.add_argument('--debug', dest='log_level', action='store_const', const=logging.DEBUG, default=logging.INFO,
                        help='set log level to DEBUG')
    args = parser.parse_args()

    logger.setLevel(args.log_level)
    logger.debug('Starting shell with args: {}'.format(args))

    sh = Shell(args.host, args.port, args.username, args.password)
    sh.start()


if __name__ == '__main__':
    sys.exit(main())
