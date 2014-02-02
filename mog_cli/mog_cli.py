#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""Command Line Interface for CSA Shogi Client"""


import sys
from shell import Shell


def main():
    sh = Shell()
    sh.start()


if __name__ == '__main__':
    sys.exit(main())
