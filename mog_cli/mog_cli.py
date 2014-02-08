#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""Command Line Interface for CSA Shogi Client"""


import sys
import argparse
from shell import Shell
from util.logger import logger


def main():
    parser = argparse.ArgumentParser(prog='mog_cli', description='Command line interface for CSA shogi client')
    parser.add_argument('-H', '--host', metavar='DEFAULT_HOST', default='localhost',
                        help='default host of shogi-server')
    parser.add_argument('-P', '--port', metavar='DEFAULT_PORT', default=4081, type=int,
                        help='default port of shogi-server')
    parser.add_argument('-u', dest='username', metavar='DEFAULT_USERNAME', help='default login username')
    parser.add_argument('-p', dest='password', metavar='DEFAULT_PASSWORD', help='default login password')
    args = parser.parse_args()

    logger.debug('Starting shell with args: {}'.format(args))

    sh = Shell(args.host, args.port, args.username, args.password)
    sh.start()


if __name__ == '__main__':
    sys.exit(main())
