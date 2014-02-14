#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""state"""

from core import *


class State:
    """Represents the state of the game"""
    # TODO: consider to be immutable class

    def __init__(self, to_move=BLACK, board={}, hand={}):
        self.to_move = to_move

        # board: {Pos, Piece} e.g. {'77': '+FU', '51': '-OU'}
        self.board = board

        # hand: {Piece, count} e.g. {'+FU': 3, '-HI': 0}
        self.hand = hand

    def __str__(self):
        buf = []

        # board
        for r in range(1, 10):
            buf.append('P{}{}'.format(r, ''.join(self.get_board('{}{}'.format(f, r)) for f in range(9, 0, -1))))

        # hand
        for t in TURNS:
            buf.append('P{}{}'.format(t, ''.join('00{}'.format(pt) * self.get_hand(t + pt) for pt in HAND_PIECE_TYPES)))

        # turn to move
        buf.append(self.to_move)

        return '\n'.join(buf)

    def __repr__(self):
        return 'State({})'.format(self.__str__())

    def __eq__(self, other):
        f = lambda x: (x.to_move, x.board, x.hand)
        return f(self) == f(other)

    def copy(self):
        return State(self.to_move, self.board.copy(), self.hand.copy())

    def set(self, pos, piece):
        self.set_hand(piece) if pos == POS_HAND else self.set_board(pos, piece)

    def set_board(self, pos, piece):
        self.board[pos] = piece

    def set_hand(self, piece):
        self.hand[piece] += 1

    def get_board(self, pos, empty_val=' * '):
        return self.board.get(pos, empty_val)

    def get_hand(self, piece):
        return self.hand.get(piece, 0)

    def reset(self, pos, piece):
        return self.reset_hand(piece) if pos == POS_HAND else self.reset_board(pos)

    def reset_board(self, pos):
        if pos in self.board:
            del self.board[pos]

    def reset_hand(self, piece):
        if piece in self.hand:
            del self.hand[piece]

    def set_hirate(self):
        self.to_move = BLACK
        self.board = {
            '91': '-KY', '81': '-KE', '71': '-GI', '61': '-KI', '51': '-OU', '41': '-KI', '31': '-GI', '21': '-KE',
            '11': '-KY',
            '82': '-HI', '22': '-KA',
            '93': '-FU', '83': '-FU', '73': '-FU', '63': '-FU', '53': '-FU', '43': '-FU', '33': '-FU', '23': '-FU',
            '13': '-FU',
            '97': '+FU', '87': '+FU', '77': '+FU', '67': '+FU', '57': '+FU', '47': '+FU', '37': '+FU', '27': '+FU',
            '17': '+FU',
            '88': '+KA', '28': '+HI',
            '99': '+KY', '89': '+KE', '79': '+GI', '69': '+KI', '59': '+OU', '49': '+KI', '39': '+GI', '29': '+KE',
            '19': '+KY',
        }
        self.hand = {}

