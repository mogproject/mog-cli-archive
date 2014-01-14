#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""logger settings"""

import logging

logger = logging.getLogger("mog-cli")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


if __name__ == '__main__':
    pass