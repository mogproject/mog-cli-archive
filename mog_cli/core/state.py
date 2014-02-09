#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""state"""

from collections import defaultdict
from core import *


class State:
    def __init__(self):
        self.to_move = BLACK

        # board: {Pos, Piece} e.g. {'77': '+FU', '51': '-OU'}
        self.board = defaultdict(lambda: ' * ')

        # hand: {Piece, count} e.g. {'+FU': 3, '-HI': 0}
        self.hand = defaultdict(int)

    def __str__(self):
        buf = []

        # board
        for r in range(1, 10):
            buf.append('P{}{}'.format(r, ''.join(self.board['{}{}'.format(f, r)] for f in range(9, 0, -1))))

        # hand
        for t in TURNS:
            buf.append('P{}{}'.format(t, ''.join('00{}'.format(pt) * self.hand[t + pt] for pt in HAND_PIECE_TYPES)))

        # turn to move
        buf.append(self.to_move)

        return '\n'.join(buf)

    def __repr__(self):
        return 'State({})'.format(self.__str__())

    def set(self, pos, piece):
        if pos == POS_HAND:
            self.hand[piece] += 1
        else:
            self.board[pos] = piece

    def reset(self, pos, piece):
        if pos == POS_HAND:
            assert(self.hand[piece] > 0)
            self.hand[piece] -= 1
        else:
            del self.board[pos]
