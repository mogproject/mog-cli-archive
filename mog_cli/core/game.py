#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""
game
"""

from core import *
from core.record import Record


class Game:

    def __init__(self, game_condition):
        self.__load_text(game_condition['Game_Summary']['Position'])  # set state and history
        self.id = game_condition['Game_Summary']['Game_ID']
        self.my_turn = game_condition['Game_Summary']['Your_Turn']
        self.condition = game_condition

    def __str__(self):
        s = self.condition['Game_Summary']
        buf = list()
        buf.append('[Game Summary]')
        buf.append('  Id                 : {}'.format(self.id))
        buf.append('  Name+              : {}{}'.format(s['Name+'], " (You!)" if self.my_turn == BLACK else ''))
        buf.append('  Name-              : {}{}'.format(s['Name-'], " (You!)" if self.my_turn == WHITE else ''))
        buf.append('  Rematch On Draw    : {}'.format(s['Rematch_On_Draw']))
        buf.append('[Time Settings]')
        buf.append('  Time Unit          : {}'.format(s['Time']['Time_Unit']))
        buf.append('  Total Time         : {}'.format(s['Time']['Total_Time']))
        buf.append('  Byoyomi            : {}'.format(s['Time']['Byoyomi']))
        buf.append('  Least Time Per Move: {}'.format(s['Time']['Least_Time_Per_Move']))
        buf.append('[Position]')
        buf.extend(('  {}'.format(s) for s in str(self.state).splitlines()))
        buf.append('[History]')
        buf.extend(('  {}'.format(s) for s in self.history_str().splitlines()))
        return '\n'.join(buf)

    def __repr__(self):
        return 'Game({})'.format(self.__str__())

    def is_my_turn(self):
        return self.state.to_move == self.my_turn

    def history_str(self):
        width = 4
        if not self.history:
            return 'no history'
        buf = ['{:03d}: {}    {}'.format(
            i, h, '\n' if (i + 1) % width == 0 else '') for i, h in enumerate(self.history)]
        # TODO: align chars
        return ''.join(buf)

    def __load_text(self, text):
        game_records = Record.read(text.splitlines())
        _, self.state, self.history = game_records[0]

    def move(self, mv):
        if not mv.is_special:
            captured = self.state.board[mv.move_to]
            if captured[0] in TURNS:
                self.state.set(POS_HAND, mv.turn + LOWER_PIECE_TYPE(captured[1:]))
            self.state.reset(mv.move_from, mv.turn + mv.piece_type)
            self.state.set(mv.move_to, mv.turn + mv.piece_type)
            self.state.to_move = FLIP_TURN[mv.turn]
        self.history.append(mv)
