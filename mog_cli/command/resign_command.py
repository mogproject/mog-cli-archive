#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resign command"""

from command import Command, MoveCommand


class ResignCommand(Command):
    """Resign this game"""

    def alias(self):
        return ['RESIGN']

    def run(self, *args):
        return lambda sh: MoveCommand.move_common(sh, sh.csa_client.resign)
