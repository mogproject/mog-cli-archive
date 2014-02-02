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
