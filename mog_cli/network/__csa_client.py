#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""
Command Line Interface for CSA Shogi Client

Protocol document: http://www.computer-shogi.org/protocol/tcp_ip_server_113.html
"""


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
logger = logging.getLogger("csa_client")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s %(message)s")
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
        self.user = None
        self.status = CsaClientStatus.welcome

    def __str__(self):
        return 'CsaClient@{}'.format(self.user if self.user else '{:X}'.format(id(self)))

    def __raw_send(self, message):
        """The lowest level socket data writing function."""
        logger.debug('{} -> {}'.format(self, repr(message)))
        self.sock.sendall('{}{}'.format(message, LF).encode('utf-8'))

    def __raw_receive(self):
        """The lowest level socket data reading function."""
        message = self.file.readline()

        if not message:
            raise ErrorDisconnected

        octets = len(message)
        decoded = message[:-1].decode('utf-8')
        logger.debug('{} <- {}'.format(self, repr(decoded)))

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

        if res[0] == 'LOGIN:incorrect':
            raise ErrorLoginFailed
        if res[0] != 'LOGIN:{} OK'.format(username):
            raise ErrorProtocol(res)

    def __raw_agree(self, game_id=''):
        # res = self.__cmd(('AGREE %s' % game_id).rstrip())
        res = self.__raw_command(('AGREE{}'.format(' ' + game_id if game_id else '')))

        if res[0].startswith('REJECT:'):
            raise ErrorGameRejected(res)
        if res[0].startswith('START:'):
            if game_id:
                if res[0].split(':')[1] != game_id:
                    raise ErrorProtocol(res)

    def agree(self, game_id=''):
        """
        Send agree message.
        Status: agree_waiting => in_game
                                 game_waiting (if rejected by peer)
        @param game_id the game id to agree
        """
        try:
            self.__raw_agree(game_id)
            self.status = CsaClientStatus.in_game
        except ErrorGameRejected:
            self.status = CsaClientStatus.game_waiting

    def login(self, username, password):
        """
        Send user name and password, return response.
        Status: welcome => game_waiting

        @param username
        @param password
        """
        if self.status != CsaClientStatus.welcome:
            raise ErrorCommandInappropriate

        self.__raw_login(username, password)
        self.user = username
        self.status = CsaClientStatus.game_waiting

    def find_game(self):
        """


        @return game id
        """
        if self.status != CsaClientStatus.game_waiting:
            raise ErrorCommandInappropriate

        self.__raw_await('END Game_Summary')
        # TODO: return game id


def main():
    from multiprocessing import Process
    user1 = Process(target=test_login, args=('foo',))
    user2 = Process(target=test_login, args=('bar',))
    user1.start()
    user2.start()
    user1.join()
    user2.join()


def test_login(username):
    c = CsaClient('docker1')
    c.login(username, 'pass')
    c.find_game()
    c.agree()



if __name__ == '__main__':
    main()
