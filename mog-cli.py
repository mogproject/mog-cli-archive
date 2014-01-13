#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""Command Line Interface for CSA Shogi Client"""


import sys
import socket
from time import time
import re
import logging
from optparse import OptionParser

# default port number
CSA_DEFAULT_PORT = 4081

# line terminators (we always output LF, and accept only LF)
LF = '\n'

# logger settings
logger = logging.getLogger("mog-cli")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# custom errors
class ErrorCommandInappropriate(Exception): pass
class ErrorProtocol(Exception): pass
class ErrorDisconnected(Exception): pass
class ErrorLoginFailed(Exception): pass
class ErrorGameRejected(Exception): pass


class CsaClientStatus:
    welcome, game_waiting, agree_waiting, in_game = range(4)


class CsaClient:
    def __init__(self, host, port=CSA_DEFAULT_PORT, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        # create connection
        self.sock = socket.create_connection((host, port), timeout)
        self.file = self.sock.makefile('rb')

        self.host = host
        self.port = port
        self.status = CsaClientStatus.welcome

    def __str__(self):
        return 'CsaClient@{:X}'.format(id(self))

    def __raw_send(self, message):
        logger.debug('{} -> {}'.format(self, message))
        self.sock.sendall('{} {}'.format(message, LF).encode('utf-8'))

    def __raw_receive(self):
        message = self.file.readline()

        if not message:
            raise ErrorDisconnected

        octets = len(message)
        decoded = message[:-1].decode('utf-8')
        logger.debug('{} <- {}'.format(self, decoded))

        return decoded, octets

    def __raw_await(self, until=''):
        buf = []
        octets = 0
        while True:
            m, o = self.__raw_receive()
            buf.append(m)
            octets += o
            if until == '' or until == m: break
        return buf

    def __raw_command(self, command):
        self.__raw_send(command)
        return self.__raw_await()

    def __raw_login(self, username, password):

        res = self.__raw_command('LOGIN {} {}'.format(username, password))

        if res[0] == 'LOGIN:incorrect': raise ErrorLoginFailed
        if res[0] != 'LOGIN:{} OK'.format(username): raise ErrorProtocol(res)
        self.status = CsaClientStatus.game_waiting

    def login(self, username, password):
        """
        Send user name and password, return response.
        Status: welcome => game_waiting
        Args:
          username: str, the user name
          password: str, the password of the user
        """
        if self.status != CsaClientStatus.welcome: raise ErrorCommandInappropriate

        self.__raw_login(username, password)

    def find_game(self):
        if self.status != CsaClientStatus.game_waiting: raise ErrorCommandInappropriate

        self.__raw_await('END Game_Summary')


def main():
    a = CsaClient('docker1')
    b = CsaClient('docker1')
    a.login('foo', 'foofoo')
    b.login('bar', 'barbar')
    a.find_game()
    b.find_game()




if __name__ == '__main__':
    sys.exit(main())
    pass
