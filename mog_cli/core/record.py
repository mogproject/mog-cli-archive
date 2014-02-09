#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Read and write CSA-format record

@see protocol -> http://www.computer-shogi.org/protocol/record_v21.html
"""

import re
from core import *

# pattern for record version
_RE_VERSION = re.compile(r'^V([0-9.]+)$')

# patterns for game information
_RE_NAME_BLACK = re.compile(r'^N[+](.+)')
_RE_NAME_WHITE = re.compile(r'^N[-](.+)')
_RE_EVENT = re.compile(r'^[$]EVENT:(.+)')
_RE_SITE = re.compile(r'^[$]SITE:(.+)')
_RE_START_TIME = re.compile(r'^[$]START_TIME:([0-9]{4})/([0-9]{2})/([0-9]{2})(?: ([0-9]{2}):([0-9]{2}):([0-9]{2}))?$')
_RE_END_TIME = re.compile(r'^[$]END_TIME:([0-9]{4})/([0-9]{2})/([0-9]{2})(?: ([0-9]{2}):([0-9]{2}):([0-9]{2}))?$')
_RE_TIME_LIMIT = re.compile(r'^[$]TIME_LIMIT:[0-9]{2}:[0-9]{2}[+][0-9]{2}$')
_RE_OPENING = re.compile(r'^[$]OPENING:(.+)')

# patterns for initial state
_RE_PRESET = re.compile(r'^PI(?:[1-9]{2}[A-Z]{2})*$')
_RE_BOARD = re.compile(r'^P[1-9].{27}$')
_RE_PIECE = re.compile(r'^P[+-](?:[0-9]{2}[A-Z]{2})+$')
_RE_TO_MOVE = re.compile(r'^[+-]$')

# patterns for move history
_RE_MOVE = re.compile(r'[+-][0-9]{2}[1-9]{2}[A-Z]{2}$')
_RE_SPECIAL_MOVE = re.compile(r'%.*$')
_RE_TIME = re.compile(r'T[0-9]*$')


def chunk(iterable, chunk_size):
    return [iterable[i:i + chunk_size] for i in range(0, len(iterable), chunk_size)]


class Record:
    @staticmethod
    def read(iterable):
        """
        @param iterable list or iterator of string
        @return list of tuple, (game_information, initial_state, history)
        """

        ### preprocessor
        lines = list()
        for line in iterable:
            if line.startswith("'"):  # comment line
                continue
            for stmt in line.strip('\n').split(','):  # multiple statements
                if stmt.strip():
                    lines.append(stmt)

        # get version
        versions = [_RE_VERSION.match(line).group(1) for line in lines if _RE_VERSION.match(line)]
        version = versions[0] if versions else '1.0'

        # TODO: read separator and multiple games

        ret = list()
        state = State()
        history = list()

        for line in lines:
            # TODO: read game info
            if _RE_PRESET.match(line):
                xs = chunk(line[2:], 4)
                pass  # TODO: implement preset to Hirate
            elif _RE_BOARD.match(line):
                rank = line[1]
                xs = chunk(line[2:], 3)
                for i, p in enumerate(xs):
                    # print(p + ' ' + str(p[0] in TURNS) + ' ' + p[0])
                    if p[0] in TURNS:
                        state.set('{}{}'.format(9 - i, rank), p)
            elif _RE_PIECE.match(line):
                turn = line[1]
                xs = chunk(line[2:], 4)
                for p in xs:
                    # TODO: apply to '00AL'
                    state.set(p[0:2], turn + p[2:4])
            elif _RE_TO_MOVE.match(line):
                state.to_move = line
            # TODO: parse move history

        ret.append(({}, state, history))

        return ret

