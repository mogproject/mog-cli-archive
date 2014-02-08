#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Win command"""

from command import Command, MoveCommand


class WinCommand(Command):
    """Declare win to this game"""

    def alias(self):
        return ['WIN']

    def run(self, *args):
        return lambda sh: MoveCommand.move_common(sh, sh.csa_client.declare_win)
