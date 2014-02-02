#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""description"""

from command.base_command import Command
import shell


class MoveCommand(Command):
    """Login to the server"""

    def alias(self):
        return ['MOVE', 'M']

    def run(self, *args):
        # TODO
        def f(shell):
            raise NotImplementedError
        return f
