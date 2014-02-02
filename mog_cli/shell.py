#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interactive shell."""

import sys
from command import *


class ShellExit(Exception):
    pass


class CommandError(Exception):
    pass


class CommandArgumentsError(Exception):
    pass


class CommandFailedError(Exception):
    pass


MODE_INIT, MODE_NETWORK, MODE_STANDALONE = range(3)


class Shell:

    def __init__(self, input=sys.stdin, output=sys.stdout):
        self.input = input
        self.output = output
        self.game = None
        self.csa_client = None
        self.set_mode(MODE_INIT)

    def __set_commands(self, *commands):
        self.commands = {}
        for command in commands:
            for alias in command.alias():
                self.commands[alias.upper()] = command

    def set_mode(self, mode):
        if mode == MODE_INIT:
            if self.game:
                self.prompt = lambda s: '[not connected]{}{:03d}(end)> '.format(s.game.turn, len(s.game.history))
            else:
                self.prompt = lambda s: '[not connected]> '
            self.__set_commands(
                LoginCommand(),
                HelpCommand(),
                ExitCommand(),
            )
        elif mode == MODE_NETWORK:
            self.prompt = lambda s: '[{}:{}]{}{:03d}> '.format(
                s.csa_client.host, s.csa_client.port, s.game.to_move, len(s.game.history))
            self.__set_commands(
                HelpCommand(),
                ExitCommand(),
                MoveCommand(),
            )
        elif mode == MODE_STANDALONE:
            # TODO: implement
            pass

    def start(self):
        while True:
            self.output.write(self.prompt(self))
            self.output.flush()

            try:
                line = self.input.readline()
                if not line:  # got EOF
                    raise ShellExit

                line = line.strip()
                if not line:  # empty line
                    continue

                # Get command name.
                cmd_args = line.split(' ')
                cmd_name = cmd_args.pop(0)

                cmd_name_upper = cmd_name.upper()
                cmd = self.commands.get(cmd_name_upper)

                if not cmd:
                    self.output.write('unknown command: {}\n'.format(cmd_name))
                    continue

                self.commands[cmd_name_upper].run(*cmd_args)(self)

            except (ShellExit, EOFError):
                break
            except Exception as e:
                self.output.write('Exception: {}\n'.format(repr(e)))

    def interactive_input(self, prompt, default=None, assertion=lambda: True):
        while True:
            ret = input('{} [{}]? : '.format(prompt, default))
            if ret == '' and default is not None:
                ret = default
            if assertion(ret):
                break
            self.output.write('Invalid input: {}\n'.format(ret))
        return ret

    IS_NOT_EMPTY = lambda s: s.strip() != ''
    IS_DIGIT = lambda s: s.isdigit()


if __name__ == '__main__':
    sh = Shell()
    sh.start()
