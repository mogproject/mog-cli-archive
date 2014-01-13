#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""Command Line Interface for CSA Shogi Client"""


import sys


def main():
    import network.csa_client
    network.csa_client.main()


if __name__ == '__main__':
    sys.exit(main())
