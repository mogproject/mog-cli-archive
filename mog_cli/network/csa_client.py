#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""
Raw communications for CSA Shogi Client

Protocol document: http://www.computer-shogi.org/protocol/tcp_ip_server_113.html
"""

import socket

from util.logger import logger


class ClosedConnectionError(Exception):
    pass


class ProtocolError(Exception):
    pass

class StateError(Exception):
    pass

# default server port
DEFAULT_PORT = 4081

# new line
LF = '\n'

# state
Connected, GameWaiting, GamePlaying = range(3)


class CsaClient:

    def __init__(self, host, port=DEFAULT_PORT, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.user = None

        # open connection
        self.sock = socket.create_connection((self.host, self.port), self.timeout)
        self.file = self.sock.makefile('rb')
        self.state = Connected

    def close(self):
        """Close connection."""
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __str__(self):
        return 'CsaClient@{}'.format(self.user if self.user else '{:X}'.format(id(self)))

    def __send(self, message):
        """The lowest level socket data writing function."""
        logger.debug('{} -> {}'.format(self, repr(message)))
        self.sock.sendall('{}{}'.format(message, LF).encode('utf-8'))

    def __receive(self):
        """The lowest level socket data reading function."""
        message = self.file.readline()

        if not message:
            raise ClosedConnectionError

        # octets = len(message)
        decoded = message[:-1].decode('utf-8')
        logger.debug('{} <- {}'.format(self, repr(decoded)))

        return decoded
        # return decoded, octets

    def __await(self, until=''):
        buf = []
        # octets = 0
        while True:
            # m, o = self.__receive()
            m = self.__receive()
            buf.append(m)
            # octets += o
            if until == '' or until == m:
                break
        assert buf  # buf must be not empty, or throws exception
        return buf

    def __command(self, command):
        self.__send(command)
        return self.__await()

    def __assertState(self, *states):
        if self.state not in states:
            raise StateError('current state {} is not in {}'.format(self.state, states))

    def login(self, username, password):
        """
        @return tuple of boolean (true if succeeded) and received message
        """
        self.__assertState(Connected)
        res = self.__command('LOGIN {} {}'.format(username, password))

        if res[0] == 'LOGIN:incorrect':
            return False, res[0]
        if res[0] != 'LOGIN:{} OK'.format(username):
            raise ProtocolError(res)
        self.state = GameWaiting
        return True, res[0]

    def logout(self):
        """
        @return tuple of boolean (always true) and received message
        """
        self.__assertState(GameWaiting)
        res = self.__command('LOGOUT')
        if res[0] != 'LOGOUT:completed':
            raise ProtocolError(res)
        return True, res[0]

    def get_game_condition(self):
        pass
# TODO
# def validate_username(username):
#     pass
# #数字('0'-'9')、英大文字('A'-'Z')、英小文字('a'-'z')、アンダースコア('_')、ハイフン('-')のいずれかの文字を用 いた32バイト以内

# class CsaRawCommands:
#     # status
#
#
#     def __raw_agree(self, game_id=''):
#         # res = self.__cmd(('AGREE %s' % game_id).rstrip())
#         res = self.__raw_command(('AGREE{}'.format(' ' + game_id if game_id else '')))
#
#         if res[0].startswith('REJECT:'):
#             raise ErrorGameRejected(res)
#         if res[0].startswith('START:'):
#             if game_id:
#                 if res[0].split(':')[1] != game_id:
#                     raise ErrorProtocol(res)
#
#     def agree(self, game_id=''):
#         """
#         Send agree message.
#         Status: agree_waiting => in_game
#                                  game_waiting (if rejected by peer)
#         @param game_id the game id to agree
#         """
#         try:
#             self.__raw_agree(game_id)
#             self.status = CsaClientStatus.in_game
#         except ErrorGameRejected:
#             self.status = CsaClientStatus.game_waiting
#
#     def login(self, username, password):
#         """
#         Send user name and password, return response.
#         Status: welcome => game_waiting
#
#         @param username
#         @param password
#         """
#         if self.status != CsaClientStatus.welcome:
#             raise ErrorCommandInappropriate
#
#         self.__raw_login(username, password)
#         self.user = username
#         self.status = CsaClientStatus.game_waiting
#
#     def find_game(self):
#         """
#
#
#         @return game id
#         """
#         if self.status != CsaClientStatus.game_waiting:
#             raise ErrorCommandInappropriate
#
#         self.__raw_await('END Game_Summary')
#         # TODO: return game id

if __name__ == '__main__':
    pass