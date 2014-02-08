#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""description"""

import re
from network.csa_client import CsaClient, DEFAULT_PORT
import shell
from core import Move, Game
import command


class LoginCommand(command.Command):
    """Login to the server"""

    def alias(self):
        return ['LOGIN']

    def run(self, *args):
        # TODO
        def f(shell):
            raise NotImplementedError
        return f


class LoginCommand(command.Command):
    """Login to the server"""

    # TODO: check the specification
    PAT_LOGIN = re.compile(r'LOGIN(?:\s+(.+)(?:[:](\d+))?(?:\s+([0-9A-Za-z]+))?(?:\s+(.+))?)')
    PAT_HOST_PORT = re.compile(r'^([^:]+)(?:[:](\d+))?$')

    def alias(self):
        return ['LOGIN']

    def _parse_args(self, sh, host_port=None, username=None, password=None, *args):
        if args:
            raise shell.CommandArgumentsError

        if host_port is None:
            host = sh.default_host
            port = sh.default_port or DEFAULT_PORT
            if host is None:
                # prompt

                raise NotImplementedError

            # host = interactive_input('hostname', DEFAULT_HOST, IS_NOT_EMPTY)
            # port = int(interactive_input('port', DEFAULT_PORT, IS_DIGIT))
        else:
            m = self.PAT_HOST_PORT.match(host_port)
            if not m:
                raise shell.CommandArgumentsError('hostname[:port]: {}'.format(host_port))
            port = DEFAULT_PORT if m.group(2) is None else int(m.group(2))
            host = m.group(1)

        username = username or sh.default_user
        password = password or sh.default_pass

        if None in [host, port, username, password]:
            raise shell.CommandArgumentsError

        return host, port, username, password

    def run(self, *args):
        def f(sh):
            host, port, username, password = self._parse_args(sh, *args)
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

                sh.game = game
                sh.csa_client = c
                sh.set_mode(shell.MODE_NETWORK)

                if not game.is_my_turn():
                    command.MoveCommand.wait_move(sh)

                    #
                    # sh.output.write('Waiting...\n')
                    # is_continue, info = c.get_move()
                    # if is_continue:
                    #     m = Move(*info)
                    #     sh.output.write('{}{}\n'.format(sh.prompt(), m))
                    #     game.move(m)
                    # else:
                    #     cmd, tm, reason, result = info
                    #
                    #     sh.output.write('{}{}\n'.format(sh.prompt(), reason))
                    #     # TODO: append to move history
                    #     sh.output.write('\n'.join(['*' * 80, '*' + {
                    #         '#WIN': 'YOU WIN!', '#LOSE': 'YOU LOSE!', '#DRAW': 'DRAW!'
                    #     }[result].center(78) + '*', '*' * 80, '']))
                    #
                    #     sh.set_mode(shell.MODE_INIT)
                    #     try:
                    #         c.logout()
                    #     except network.csa_client.ClosedConnectionError:
                    #         pass  # ignore this

            else:
                c.reject(game_cond)
                sh.csa_client = None

        return f