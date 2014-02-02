#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""description"""

import re
from network.csa_client import CsaClient, DEFAULT_HOST, DEFAULT_PORT
import shell
from core.game import Game
from command.base_command import Command


class LoginCommand(Command):
    """Login to the server"""

    def alias(self):
        return ['LOGIN']

    def run(self, *args):
        # TODO
        def f(shell):
            raise NotImplementedError
        return f


class LoginCommand(Command):
    """Login to the server"""

    # TODO: check the specification
    PAT_LOGIN = re.compile(r'LOGIN(?:\s+(.+)(?:[:](\d+))?(?:\s+([0-9A-Za-z]+))?(?:\s+(.+))?)')
    PAT_HOST_PORT = re.compile(r'^([^:]+)(?:[:](\d+))?$')

    def alias(self):
        return ['LOGIN']

    def _parse_args(self, host_port, username, password, *args):
        if args:
            raise shell.CommandArgumentsError

        if host_port is None:
            host = DEFAULT_HOST
            port = DEFAULT_PORT
            # host = interactive_input('hostname', DEFAULT_HOST, IS_NOT_EMPTY)
            # port = int(interactive_input('port', DEFAULT_PORT, IS_DIGIT))
        else:
            m = self.PAT_HOST_PORT.match(host_port)
            if not m:
                raise shell.CommandArgumentsError('hostname[:port]: {}'.format(host_port))
            port = DEFAULT_PORT if m.group(2) is None else int(m.group(2))
            host = m.group(1)

        # username = interactive_input('username', None, IS_NOT_EMPTY) if username is None else username
        # password = interactive_input('password', None, IS_NOT_EMPTY) if password is None else password

        return host, port, username, password

    def run(self, *args):
        host, port, username, password = self._parse_args(*args)

        def f(sh):
            c = CsaClient(host, port)
            ret_login = c.login(username, password)
            if not ret_login[0]:
                raise shell.CommandFailedError('failed to login')

            game_cond = c.get_game_condition()[0]
            game = Game(game_cond)

            ret = input('agree to this game? [Y/n]: ')

            if ret == '' or ret.upper() == 'Y':
                c.agree(game_cond)
                ret_agree = c.get_agreement(game_cond)
                if not ret_agree[0]:
                    sh.output.write('Game was rejected by peer.\n')
                    return

                sh.output.write('Game started: {}\n'.format(game.id))
                if not game.is_my_turn():
                    sh.output.write('Waiting...\n')
                    is_continue, info = c.get_move()
                    if is_continue:
                        m, tm = info
                        game.move(m, tm)
                    else:
                        # TODO: append to history
                        c.logout()

                sh.game = game
                sh.csa_client = c
                sh.set_mode(shell.MODE_NETWORK)
            else:
                c.reject(game_cond)

        return f