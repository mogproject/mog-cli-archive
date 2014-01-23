#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Interactive shell."""

import sys


class Shell:

    def __init__(self):
        self.prompt = lambda: 'not connected> '
        pass

    def start(self):
        while True:
            sys.stdout.write(self.prompt())
            sys.stdout.flush()

            line = sys.stdin.readline()
            if not line:
                break

            # TODO: catch event tab key down

            line = line.strip()
            if not line:
                continue

             # TODO: parse command
            print(line)




