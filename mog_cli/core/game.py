#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""game"""


class Game:

    def __init__(self, game_condition):
        # TODO parse condition and create initial state (and history if need)
        self.cond = game_condition

        self.history = []
        self.id = self.cond['Game_Summary']['Game_ID']
        self.to_move = self.cond['Game_Summary']['To_Move']
        self.my_turn = self.cond['Game_Summary']['Your_Turn']

    def __str__(self):
        return self.cond

    def is_my_turn(self):
        return self.to_move == self.my_turn

    def move(self, mv):
        self.history.append(mv)
