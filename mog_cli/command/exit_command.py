#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""description"""

from command.base_command import Command
import shell


class ExitCommand(Command):
    """Exit interactive shell"""

    def alias(self):
        return ['EXIT', 'QUIT', 'Q']

    def run(self, *args):
        # ignore args
        raise shell.ShellExit
