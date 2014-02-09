#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""description"""

from command.base_command import Command


class InfoCommand(Command):
    def alias(self):
        return ['INFO', 'I']

    def run(self, *args):
        return lambda sh: sh.output.write('{}\n'.format(sh.game))
