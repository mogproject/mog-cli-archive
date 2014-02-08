#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command to print the history of the game moves."""

from command.base_command import Command
import shell


class HistoryCommand(Command):
    """Print move history"""

    def alias(self):
        return ['HISTORY']

    def run(self, *args):
        # Print all history of the current game.

        if args:
            raise shell.CommandArgumentsError('Invalid arguments: {}'.format(args))

        def f(sh):
            if not sh.game:
                return 'no game'
            if not sh.game.history:
                return 'no history'
            return '\n'.join('{:03d}: {}'.format(t[0], t[1]) for t in enumerate(sh.game.history))

        return lambda sh: sh.output.write(f(sh) + '\n')
