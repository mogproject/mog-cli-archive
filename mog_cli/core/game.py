#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""game"""


class Game:

    def __init__(self, game_condition):
        # TODO
        self.cond = game_condition
        self.turn = '+'
        self.history = []

    def __str__(self):
        return self.conf
