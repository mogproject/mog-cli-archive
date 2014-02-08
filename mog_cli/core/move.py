#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""move class"""


class Move:
    def __init__(self, move_str, elapsed_time=None):
        # TODO: parse string
        self.move_str = move_str.upper()
        self.elapsed_time = elapsed_time

    def __str__(self):
        return self.move_str + ('' if self.elapsed_time is None else ',T{}'.format(self.elapsed_time))

    def is_special(self):
        return self.move_str.startswith('#')


class IllegalMove(Move):
    pass


class Resign(Move):
    pass


class DeclareWin(Move):
    pass