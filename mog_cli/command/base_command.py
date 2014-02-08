#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base class of commands"""


class Command:
    """Base class of commands"""

    def __init__(self):
        pass

    def help(self):
        return 'default help message'

    def name(self):
        return self.alias()[0]

    def alias(self):
        raise NotImplementedError

    def run(self, *args):
        """args => (Shell => Unit)"""
        return lambda sh: sh.output.write('Invalid arguments for {}: {}\n'.format(self.name(), args))
