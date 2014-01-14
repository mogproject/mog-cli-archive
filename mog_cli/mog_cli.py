#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""Command Line Interface for CSA Shogi Client"""


import sys
import network


def main():
    network.csa_client.main()


if __name__ == '__main__':
    sys.exit(main())
