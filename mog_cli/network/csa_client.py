#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""
Raw communications for CSA Shogi Client

Protocol document: http://www.computer-shogi.org/protocol/tcp_ip_server_113.html
"""

import socket
import re

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
CONNECTED, GAME_WAITING, AGREE_WAITING, MOVE_WAITING, GAME_PLAYING = range(5)


class CsaClient:

    def __init__(self, host, port=DEFAULT_PORT, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.user = None

        # open connection
        self.sock = socket.create_connection((self.host, self.port), self.timeout)
        self.file = self.sock.makefile('rb')
        self.state = CONNECTED

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
        Run in Connected state (before GameWaiting).
        @return tuple of boolean (true if succeeded) and received message
        """
        self.__assertState(CONNECTED)
        res = self.__command('LOGIN {} {}'.format(username, password))

        if res[0] == 'LOGIN:incorrect':
            return False, res[0]
        if res[0] != 'LOGIN:{} OK'.format(username):
            raise ProtocolError(res)

        self.user = username
        self.state = GAME_WAITING
        return True, res[0]

    def logout(self):
        """
        Run in GameWaiting state.
        @return tuple of boolean (always true) and received message
        """
        self.__assertState(GAME_WAITING)
        res = self.__command('LOGOUT')
        if res[0] != 'LOGOUT:completed':
            raise ProtocolError(res)
        self.state = CONNECTED
        return True, res[0]

    def get_game_condition(self):
        """
        Wait for receiving game condition.

        Run in GameWaiting state.
        @return tuple of GameCondition object and received message
        """
        self.__assertState(GAME_WAITING)

        res = self.__await('END Game_Summary')
        cond = self.__parse_game_condition(res)
        self.state = AGREE_WAITING
        return cond, res

    def __parse_game_condition(self, lines):
        pat_tag_begin = re.compile(r'BEGIN (\w+)')
        pat_key_value = re.compile(r'([\w+-]+):(.+)')

        def f(ls):
            d = {}
            while ls:
                head = ls.pop(0)

                if pat_tag_begin.match(head):
                    tag = pat_tag_begin.match(head).group(1)

                    # Find first closing tag (if not found, throws ValueError).
                    j = ls.index('END {}'.format(tag))

                    if tag == 'Position':
                        d[tag] = '\n'.join(ls[:j])
                    else:
                        d[tag] = f(ls[:j])
                    ls = ls[j + 1:]
                    continue

                if pat_key_value.match(head):
                    m = pat_key_value.match(head)
                    d[m.group(1)] = m.group(2)
                    continue

                raise ProtocolError(head)
            return d

        return f(lines)

    def agree(self, game_condition):
        """
        Send agree message.

        State: AGREE_WAITING => GAME_PLAYING when the peer agrees and initial turn is your turn,
                                MOVE_WAITING when the peer agrees and initial turn is not your turn,
                                GAME_WAITING when the peer rejects
        @param game_condition the dictionary of the game condition
        """
        self.__assertState(AGREE_WAITING)

        game_id = game_condition['Game_Summary']['Game_ID']
        init_turn = game_condition['Game_Summary']['To_Move']
        my_turn = game_condition['Game_Summary']['Your_Turn']
        res = self.__command('AGREE {}'.format(game_id))

        if res[0].startswith('REJECT:{} by '.format(game_id)):
            self.state = GAME_WAITING
            return False, res[0]
        if res[0] == 'START:{}'.format(game_id):
            self.state = GAME_PLAYING if init_turn == my_turn else GAME_WAITING
            return True, res[0]
        raise ProtocolError(res)

    def reject(self, game_condition):
        """
        Send reject message.

        State: AGREE_WAITING => GAME_WAITING
        """
        self.__assertState(AGREE_WAITING)

        game_id = game_condition['Game_Summary']['Game_ID']
        res = self.__command('REJECT {}'.format(game_id))

        if res[0].startswith('REJECT:{} by '.format(game_id)):
            self.state = GAME_WAITING
            return res[0]
        raise ProtocolError(res)



# TODO
# def validate_username(username):
#     pass
# #数字('0'-'9')、英大文字('A'-'Z')、英小文字('a'-'z')、アンダースコア('_')、ハイフン('-')のいずれかの文字を用 いた32バイト以内

# result_occasion
#     #SENNICHITE
# -- (draw by repetition)
#
# #OUTE_SENNICHITE
# -- (illegal move by repetition)
#
# #ILLEGAL_MOVE
# -- (other illegal moves including illegal use of %KACHI)
#
# #TIME_UP
#
# #RESIGN
# -- (one player resigned by '%TORYO')
#
# #JISHOGI
# -- (one player declared a win by '%KACHI' and the declaration is legal)
#


if __name__ == '__main__':
    pass