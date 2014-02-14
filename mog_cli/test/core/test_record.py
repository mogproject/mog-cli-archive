#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""unit test for reading/writing records"""

import unittest
import core.record
from core import *


class TestReadRecord(unittest.TestCase):
# TODO: write clause graph of the csa record format to cacoo
    def test_hirate_initial(self):
        txt = """PI\n+"""

        self.assertEqual(core.record.Record.read(txt.splitlines()), [({}, State(BLACK, {
            '91': '-KY', '81': '-KE', '71': '-GI', '61': '-KI', '51': '-OU', '41': '-KI', '31': '-GI', '21': '-KE',
            '11': '-KY', '82': '-HI', '22': '-KA', '93': '-FU', '83': '-FU', '73': '-FU', '63': '-FU', '53': '-FU',
            '43': '-FU', '33': '-FU', '23': '-FU', '13': '-FU', '97': '+FU', '87': '+FU', '77': '+FU', '67': '+FU',
            '57': '+FU', '47': '+FU', '37': '+FU', '27': '+FU', '17': '+FU', '88': '+KA', '28': '+HI', '99': '+KY',
            '89': '+KE', '79': '+GI', '69': '+KI', '59': '+OU', '49': '+KI', '39': '+GI', '29': '+KE', '19': '+KY',
        }, {}), [])])

    def test_hirate_customized(self):
        txt = """PI28HI88KA19KY99KY\n+"""

        self.assertEqual(core.record.Record.read(txt.splitlines()), [({}, State(BLACK, {
            '91': '-KY', '81': '-KE', '71': '-GI', '61': '-KI', '51': '-OU', '41': '-KI', '31': '-GI', '21': '-KE',
            '11': '-KY', '82': '-HI', '22': '-KA', '93': '-FU', '83': '-FU', '73': '-FU', '63': '-FU', '53': '-FU',
            '43': '-FU', '33': '-FU', '23': '-FU', '13': '-FU', '97': '+FU', '87': '+FU', '77': '+FU', '67': '+FU',
            '57': '+FU', '47': '+FU', '37': '+FU', '27': '+FU', '17': '+FU', '89': '+KE', '79': '+GI', '69': '+KI',
            '59': '+OU', '49': '+KI', '39': '+GI', '29': '+KE',
        }, {}), [])])


    def test_start_with_white(self):
        txt = """PI\n-"""

        self.assertEqual(core.record.Record.read(txt.splitlines()), [({}, State(WHITE, {
            '91': '-KY', '81': '-KE', '71': '-GI', '61': '-KI', '51': '-OU', '41': '-KI', '31': '-GI', '21': '-KE',
            '11': '-KY', '82': '-HI', '22': '-KA', '93': '-FU', '83': '-FU', '73': '-FU', '63': '-FU', '53': '-FU',
            '43': '-FU', '33': '-FU', '23': '-FU', '13': '-FU', '97': '+FU', '87': '+FU', '77': '+FU', '67': '+FU',
            '57': '+FU', '47': '+FU', '37': '+FU', '27': '+FU', '17': '+FU', '88': '+KA', '28': '+HI', '99': '+KY',
            '89': '+KE', '79': '+GI', '69': '+KI', '59': '+OU', '49': '+KI', '39': '+GI', '29': '+KE', '19': '+KY',
            }, {}), [])])

    def test_board_initial(self):
        # TODO: implement more test cases
        pass


if __name__ == '__main__':
    unittest.main()
