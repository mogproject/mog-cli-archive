#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Login command"""

import re
from network.csa_client import CsaClient, DEFAULT_PORT
import shell
from core import Move, Game
import command


class LoginCommand(command.Command):
    """Login to the server"""
#TODO: Implement help for login command
    # Username should be composed by numbers(0-9), alphabets(A-Za-z), underscores(_) and hyphens(-).
    # Username and password are 1 to 32 byte length, inclusive.

    PAT_USERNAME = re.compile(r'^[_\-0-9A-Za-z]{1,32}$')
    PAT_PASSWORD = re.compile(r'^.{1,32}$')
    PAT_LOGIN = re.compile(r'LOGIN(?:\s+(.+)(?:[:](\d+))?(?:\s+([_\-0-9A-Za-z]+))?(?:\s+(.+))?)')
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

        # check requirements
        if None in [host, port, username, password]:
            raise shell.CommandArgumentsError

        if not self.PAT_USERNAME.match(username):
            raise shell.CommandArgumentsError('invalid username: {}'.format(username))
        if not self.PAT_PASSWORD.match(password):
            raise shell.CommandArgumentsError('invalid password: {}'.format(password))

        return host, port, username, password

    def run(self, *args):
        def f(sh):
            host, port, username, password = self._parse_args(sh, *args)
            c = CsaClient(host, port)
            ret_login = c.login(username, password)
            if not ret_login[0]:
                raise shell.CommandFailedError('failed to login')

            sh.sys_message('waiting for peer...')
            game_cond = c.get_game_condition()[0]
            game = Game(game_cond)

            # print game condition
            sh.output.write('{}\n'.format(game))
            ret = input('agree to this game? [Y/n]: ')

            if ret == '' or ret.upper() == 'Y':
                c.agree(game_cond)
                sh.sys_message('waiting for agreement...')
                ret_agree = c.get_agreement(game_cond)
                if not ret_agree[0]:
                    sh.sys_message('game was rejected by peer.')
                    return

                sh.sys_message('game started: {}'.format(game.id))

                sh.game = game
                sh.csa_client = c
                sh.set_mode(shell.MODE_NETWORK)

                if not game.is_my_turn():
                    command.MoveCommand.wait_move(sh)
            else:
                c.reject(game_cond)
                sh.csa_client = None

        return f