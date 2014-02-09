#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""move class"""

from core import *


class Move:
    def __init__(self, move_str, elapsed_time=None):
        move_str = move_str.upper()

        if move_str.startswith('#'):
            self.is_special = True
            self.turn = None
            self.move_from = None
            self.move_to = None
            self.piece_type = None
        else:
            assert(len(move_str) == 7)

            self.is_special = False
            self.turn = move_str[0]
            self.move_from = move_str[1:3]
            self.move_to = move_str[3:5]
            self.piece_type = move_str[5:7]

            assert(self.turn in TURNS)
            if self.move_from == POS_HAND:
                assert(all('1' <= c <= '9' for c in self.move_to))
                assert(self.piece_type in HAND_PIECE_TYPES)
            else:
                assert(all('1' <= c <= '9' for c in self.move_from))
                assert(all('1' <= c <= '9' for c in self.move_to))
                assert(self.piece_type in PIECE_TYPES)

        self.move_str = move_str
        self.elapsed_time = elapsed_time

    def __str__(self):
        return self.move_str + ('' if self.elapsed_time is None else ',T{}'.format(self.elapsed_time))

    def __repr__(self):
        return 'Move({})'.format(self.__str__())
