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


# default server port
DEFAULT_PORT = 4081

# new line
LF = '\n'

# state
CONNECTED, GAME_WAITING, AGREE_WAITING, START_WAITING, GAME_TO_MOVE, GAME_TO_WAIT = range(6)

# regexp pattern
PAT_MOVE = re.compile(r'^[/+-]\d{2}[1-9]{2}[A-Z]{2}$')
PAT_MOVE_CONFIRM = re.compile(r'^([/+-]\d{2}[1-9]{2}[A-Z]{2}),T(\d+)$')
PAT_CONFIRM = re.compile(r'.*,T(\d+)$')
PAT_SPECIAL = re.compile(r'^%[A-Z]+$')
PAT_SPECIAL_CONFIRM = re.compile(r'^(%[A-Z]+)(?:,T(\d+))?$')


class CsaClient:

    def __init__(self, host, port=DEFAULT_PORT, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.user = None
        self.buffer = []

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
        """Read one line from socket or its buffer."""
        if not self.buffer:
            self.__sock_read_line()
        return self.buffer.pop(0)

    def __sock_read_line_raw(self):
        """Read from socket until line feed.
        This is a blocking method."""
        line = self.file.readline()

        if not line:
            raise ClosedConnectionError
        return line

    def __sock_read_line(self):
        self.__append_buffer(self.__sock_read_line_raw())

    def __sock_read_all(self):
        """Receive all the messages without waiting."""
        while True:
            orig_timeout = self.sock.gettimeout()
            self.sock.settimeout(0)
            c = self.file.read(1)  # read the first byte
            self.sock.settimeout(orig_timeout)

            if c is None:
                break  # no new message
            elif c == b'':
                raise ClosedConnectionError
            else:
                # found new message
                self.__append_buffer(c + self.__sock_read_line_raw())

    def __append_buffer(self, data):
        """Store a message to buffer."""
        decoded = data[:-1].decode('utf-8')
        logger.debug('{} <- {}'.format(self, repr(decoded)))
        self.buffer.append(decoded)

    def __await(self, predicate=lambda x: True):
        """Wait until receiving the line which satisfies the given predicate."""
        buf = []
        while True:
            m = self.__receive()
            buf.append(m)
            if predicate(m):
                break
        assert buf  # returns non-empty list, or throws exception
        return buf

    def __command(self, command):
        self.__send(command)
        return self.__await()

    def login(self, username, password):
        """
        Run in Connected state (before GameWaiting).
        @return tuple of boolean (true if succeeded) and received message
        """
        assert self.state == CONNECTED, 'illegal state: {}'.format(self.state)
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
        assert self.state == GAME_WAITING, 'illegal state: {}'.format(self.state)
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
        assert self.state == GAME_WAITING, 'illegal state: {}'.format(self.state)

        res = self.__await(lambda x: x == 'END Game_Summary')
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

        State: AGREE_WAITING => START_WAITING
        @param game_condition the dictionary of the game condition
        """
        #TODO: param game_condition -> game_id
        assert self.state == AGREE_WAITING, 'illegal state: {}'.format(self.state)

        game_id = game_condition['Game_Summary']['Game_ID']
        self.__send('AGREE {}'.format(game_id))
        self.state = START_WAITING

    def get_agreement(self, game_condition):
        """
        Receive peer's agree or reject message.

        State: AGREE_WAITING => GAME_TO_MOVE when the peer agrees and initial turn is your turn,
                                GAME_TO_WAIT when the peer agrees and initial turn is not your turn,
                                GAME_WAITING when the peer rejects
        @param game_condition the dictionary of the game condition
        """
        assert self.state == START_WAITING, 'illegal state: {}'.format(self.state)

        game_id = game_condition['Game_Summary']['Game_ID']
        init_turn = game_condition['Game_Summary']['To_Move']
        my_turn = game_condition['Game_Summary']['Your_Turn']

        res = self.__receive()
        if res.startswith('REJECT:{} by '.format(game_id)):
            self.state = GAME_WAITING
            return False, res
        if res == 'START:{}'.format(game_id):
            self.state = GAME_TO_MOVE if init_turn == my_turn else GAME_TO_WAIT
            return True, res
        raise ProtocolError(res)

    def reject(self, game_condition):
        """
        Send reject message.

        State: START_WAITING => GAME_WAITING
        """
        assert self.state == AGREE_WAITING, 'illegal state: {}'.format(self.state)

        game_id = game_condition['Game_Summary']['Game_ID']
        res = self.__command('REJECT {}'.format(game_id))

        if res[0].startswith('REJECT:{} by '.format(game_id)):
            self.state = GAME_WAITING
            return res[0]
        raise ProtocolError(res)

    def __parse_consumed_time(self, line):
        m = PAT_CONFIRM.match(line)
        if m:
            return int(m.group(1))
        else:
            return None

    def move(self, move_string):
        """
        @return tuple of (move_string, elapsed_time, game_end_reason, game_end_result)
                game_end_reason and game_end_result are None when game is continued.

                e.g. ('+7776FU', 15, None, None)
                     ('+7776FU', 3, '#TIMEUP', '#LOSE')
        """
        assert self.state == GAME_TO_MOVE, 'illegal state: {}'.format(self.state)

        assert PAT_MOVE.match(move_string), 'move string format error: {}'.format(move_string)

        # Check timeup before move.
        if self.is_game_end():
            reason = self.buffer.pop(0)
            result = self.buffer.pop(0)
            if (reason, result) not in ['#TIMEUP', '#LOSE']:
                raise ProtocolError((reason, result))
            # timeup
            self.state = GAME_WAITING
            return move_string, None, reason, result

        # Send move command, then get one line.
        res = self.__command(move_string)

        # Check if confirmation comes.
        pat_confirm = re.compile(r'^{},T(\d+)$'.format(move_string.replace('+', '\+')))
        m = pat_confirm.match(res[0])
        if m:
            # found confirmation
            consumed_time = int(m.group(1))
        else:
            consumed_time = None
            self.buffer.insert(0, res[0])  # put back to buffer

        # Check game-end message after move.
        if self.is_game_end():
            reason = self.buffer.pop(0)
            result = self.buffer.pop(0)
            if (reason, result) not in [
                ('#SENNICHITE', '#DRAW'), ('#OUTE_SENNICHITE', '#WIN'), ('#ILLEGAL_MOVE', '#LOSE'),
                ('#TIME_UP', '#LOSE')]:
                raise ProtocolError((reason, result))
            self.state = GAME_WAITING
            return move_string, consumed_time, reason, result

        if not consumed_time:
            raise ProtocolError(res)

        self.state = GAME_TO_WAIT
        return move_string, consumed_time, None, None

    def __move_special(self, command, possible_results):
        assert self.state == GAME_TO_MOVE, 'illegal state: {}'.format(self.state)

        res = self.__command(command)

        # It depends whether consumed time comes or not.
        consumed_time = self.__parse_consumed_time(res[0])
        if res[0].startswith(command) and consumed_time is None:
            reason = res[0]
        else:
            reason = self.__receive()

        # It depends whether command string echoes back or not.
        if reason == command:
            reason = self.__receive()

        if not res[0].startswith(command):
            raise ProtocolError(res)

        result = self.__receive()

        if (reason, result) not in possible_results:
            raise ProtocolError((reason, result))

        self.state = GAME_WAITING
        return command, consumed_time, reason, result

    def resign(self):
        """
        @return tuple of (move_string, elapsed_time, game_end_reason, game_end_result)
                e.g. ('%TORYO', 3, '#RESIGN', '#LOSE')
        """
        return self.__move_special('%TORYO', [('#RESIGN', '#LOSE'), ('#TIME_UP', '#LOSE')])

    def declare_win(self):
        """
        @return tuple of (move_string, elapsed_time, game_end_reason, game_end_result)
                e.g. ('%KACHI', 3, '#JISHOGI', '#WIN')
                     ('%KACHI', 3, '#ILLEGAL_MOVE', '#LOSE')
        """
        return self.__move_special('%KACHI', [('#ILLEGAL_MOVE', '#LOSE'), ('#TIME_UP', '#LOSE'), ('#JISHOGI', '#WIN')])

    def get_move(self):
        """
        @return tuple of (move_string, elapsed_time, game_end_reason, game_end_result)
                game_end_reason and game_end_result are None when game is continued.

                e.g. ('+7776FU', 15, None, None)
                     ('%TORYO', 3, '#RESIGN', '#WIN')
        """
        assert self.state == GAME_TO_WAIT, 'illegal state: {}'.format(self.state)

        # receive one line
        res = self.__receive()

        # move confirmation
        if PAT_MOVE_CONFIRM.match(res):
            command, t = PAT_MOVE_CONFIRM.match(res).groups()
            consumed_time = int(t)
            self.state = GAME_TO_MOVE
        elif PAT_SPECIAL_CONFIRM.match(res):
            command, t = PAT_SPECIAL_CONFIRM.match(res).groups()
            consumed_time = None if t is None else int(t)

            # resign/jishogi commands can be sent twice
            # e.g. ['%KACHI,T12', '%KACHI', '#JISHOGI', '#LOSE']
            check = self.__receive()
            if check != command:
                self.buffer.insert(0, check)
        else:
            # no confirmation, maybe game is end
            command = None
            consumed_time = None
            self.buffer.insert(0, res)  # put back to buffer

        # check if game is end
        if self.is_game_end():
            reason = self.buffer.pop(0)
            result = self.buffer.pop(0)
            if (command, reason, result) not in [
                (command, '#SENNICHITE', '#DRAW'),
                (command, '#OUTE_SENNICHITE', '#LOSE'),
                (command, '#ILLEGAL_MOVE', '#WIN'),
                (None, '#ILLEGAL_MOVE', '#WIN'),
                (None, '#TIME_UP', '#WIN'),
                ('%TORYO', '#RESIGN', '#WIN'),
                ('%KACHI', '#JISHOGI', '#LOSE')]:
                raise ProtocolError((reason, result))
            self.state = GAME_WAITING
            return command, consumed_time, reason, result

        if not consumed_time:
            raise ProtocolError(res)

        self.state = GAME_TO_MOVE
        return command, consumed_time, None, None

    def is_game_end(self):
        self.__sock_read_all()
        if not self.buffer:
            return False
        return all(b.startswith('#') for b in self.buffer[:2])


if __name__ == '__main__':
    pass