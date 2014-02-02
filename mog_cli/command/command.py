#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""description"""

import re
from network.csa_client import CsaClient, DEFAULT_HOST, DEFAULT_PORT
import shell
from core.game import Game

__all__ = ['ExitCommand', 'HelpCommand', 'LoginCommand', 'MoveCommand', 'ResignCommand', 'WinCommand']
# TODO: Separate commands to each file.


def interactive_input(prompt, default=None, assertion=lambda: True):
    while True:
        ret = input('{} [{}]? : '.format(prompt, default))
        if ret == '' and default is not None:
            ret = default
        if assertion(ret):
            break
        print('Invalid input: {}'.format(ret))
    return ret

IS_NOT_EMPTY = lambda s: s.strip() != ''
IS_DIGIT = lambda s: s.isdigit()


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


class HelpCommand(Command):
    """Print help message"""

    def alias(self):
        return ['HELP', '?', 'H']

    def run(self, command=None, *args):
        buf = ['']

        def f(shell):
            # Print overview help.
            buf.append('{:20s}: brief description'.format('command (alias)'))
            buf.append('')

            for name, cmd in sorted((c.name(), c) for c in set(shell.commands.values())):
                alias = ', '.join(filter(lambda x: x != name, cmd.alias()))
                alias = '({})'.format(alias) if alias else ''
                buf.append('{:20s}: {}'.format('{} {}'.format(name, alias), cmd.__doc__))

            buf.append('')
            buf.append("see more messages to type 'help <command>'\n\n")
            shell.output.write('\n'.join(('  ' + x if x else '' for x in buf)))

        def g(shell):
            # Print specific help.
            c = shell.commands.get(command.upper())
            if not c:
                super(HelpCommand, self).run(command, *args)(shell)
            else:
                buf.append('{} - {}'.format(c.name(), c.__doc__))
                buf.append('')
                buf.append('{}'.format(c.help()))
                buf.append('\n')
            shell.output.write('\n'.join(('  ' + x if x else '' for x in buf)))

        return f if command is None else g


class ExitCommand(Command):
    """Exit interactive shell"""

    def alias(self):
        return ['EXIT', 'QUIT', 'Q']

    def run(self, *args):
        # ignore args
        raise shell.ShellExit


class LoginCommand(Command):
    """Login to the server"""

    def alias(self):
        return ['LOGIN']

    def run(self, *args):
        # TODO
        def f(shell):
            raise NotImplementedError
        return f


class MoveCommand(Command):
    def alias(self):
        return ['MOVE', 'M']

    def run(self, *args):
        # TODO
        def f(shell):
            raise NotImplementedError
        return f


class ResignCommand(Command):
    def alias(self):
        return ['MOVE', 'M']

    def run(self, *args):
        # TODO
        def f(shell):
            raise NotImplementedError
        return f


class WinCommand(Command):
    def alias(self):
        return ['MOVE', 'M']

    def run(self, *args):
        # TODO
        def f(shell):
            raise NotImplementedError
        return f


class InfoCommand(Command):
    def alias(self):
        return ['INFO', 'I']

    def run(self, *args):
        return lambda sh: sh.output.write(self.game + '\n')


class SaveCommand(Command):
    def alias(self):
        return ['SAVE']

    def run(self, *args):
        # TODO
        def f(shell):
            raise NotImplementedError
        return f


class LoadCommand(Command):
    def alias(self):
        return ['SAVE']

    def run(self, *args):
        # TODO
        def f(shell):
            raise NotImplementedError
        return f
