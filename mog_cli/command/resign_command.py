#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""description"""

from command.base_command import Command
import shell


class ResignCommand(Command):
    def alias(self):
        return ['RESIGN']

    def run(self, *args):
        # TODO
        def f(shell):
            raise NotImplementedError
        return f
