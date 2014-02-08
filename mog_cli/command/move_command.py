#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""description"""

import functools
import network.csa_client
from command.base_command import Command
import shell
from core import Move


class MoveCommand(Command):
    """Send the move and wait for peer's move"""

    def alias(self):
        return ['MOVE', 'M']

    def run(self, *args):
        if len(args) != 1:
            raise shell.CommandArgumentsError('Invalid number of arguments: {}'.format(args))

        def f(sh):
            s = args[0]
            if not s.startswith(sh.game.my_turn):
                s = sh.game.my_turn + s

            MoveCommand.move(sh, Move(s)) and MoveCommand.wait_move(sh)

        return f

    @staticmethod
    def __move(sh, func):
        """inner function for move/wait_move"""
        def f(m):
            sh.sys_message('move: {}'.format(m))
            sh.game.move(m)

        mv, tm, reason, result = func()

        # special move
        if reason is not None:
            f(Move(reason, tm))
            sh.game_end_banner(result)

            try:
                sh.csa_client.logout()
            except (ConnectionResetError, network.csa_client.ClosedConnectionError):
                pass  # ignore this

            sh.set_mode(shell.MODE_INIT)
            return False

        # normal move
        f(Move(mv, tm))
        return True


    @staticmethod
    def move(sh, m):
        return MoveCommand.__move(sh, functools.partial(sh.csa_client.move, m.move_str))


    @staticmethod
    def wait_move(sh):
        sh.sys_message("waiting for peer's move...")
        return MoveCommand.__move(sh, sh.csa_client.get_move)

