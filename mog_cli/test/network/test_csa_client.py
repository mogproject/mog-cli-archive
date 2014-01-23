#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for CsaClient class."""

import unittest
import logging
import os

from network.csa_client import *
from functools import partial
from test_util import *

SHOGI_SERVER_HOST = os.environ.get('DOCKER_HOST', 'localhost')

# logger.setLevel(logging.INFO)

# counter for making unique username
counter = 0


def setup():
    global counter
    counter += 1
    return CsaClient(SHOGI_SERVER_HOST), 'user{}'.format(counter)


def teardown(client):
    try:
        client.logout()
    except (AssertionError, ProtocolError, ConnectionResetError, ClosedConnectionError):
        pass
    client.close()


def exec_then_get_state(func, client, *args, **kwargs):
    """Returns partial function."""
    def f():
        func(client, *args, **kwargs)
        return client.state
    return f


def replay_history(black, white, history):
    for h in history:
        a, b = black, white
        if h.startswith('-'):
            a, b = b, a
        a.move(h)
        b.get_move()


class TestLogin(unittest.TestCase):

    def setUp(self):
        self.client, self.user = setup()

    def tearDown(self):
        teardown(self.client)

    def test_login(self):
        self.assertEqual(self.client.state, CONNECTED)
        self.assertEqual(self.client.login(self.user, 'pass1'), (True, 'LOGIN:{} OK'.format(self.user)))
        self.assertEqual(self.client.state, GAME_WAITING)

    def test_login_same_username_different_password(self):
        self.assertEqual(self.client.state, CONNECTED)
        with CsaClient(SHOGI_SERVER_HOST) as c:
            self.assertEqual(c.state, CONNECTED)
            c.login(self.user, 'pass1')
            self.assertEqual(c.state, GAME_WAITING)
            self.assertEqual(
                self.client.login(self.user, 'pass2'), (False, 'LOGIN:incorrect'))
        self.assertEqual(self.client.state, CONNECTED)

    def test_login_empty_username_or_password(self):
        self.assertEqual(self.client.state, CONNECTED)
        self.assertEqual(self.client.login('', 'pass1'), (False, 'LOGIN:incorrect'))
        self.assertEqual(self.client.state, CONNECTED)
        self.assertEqual(self.client.login(self.user, ''), (False, 'LOGIN:incorrect'))
        self.assertEqual(self.client.state, CONNECTED)
        self.assertEqual(self.client.login('', ''), (False, 'LOGIN:incorrect'))
        self.assertEqual(self.client.state, CONNECTED)

    def test_login_username_too_long(self):
        self.assertEqual(self.client.state, CONNECTED)
        self.assertEqual(
            self.client.login('0123456789abcdef0123456789abcdef0', 'pass1'), (False, 'LOGIN:incorrect'))
        self.assertEqual(self.client.state, CONNECTED)

    def test_login_username_contains_invalid_character(self):
        self.assertEqual(self.client.state, CONNECTED)
        self.assertEqual(self.client.login('user+', 'pass1'), (False, 'LOGIN:incorrect'))
        self.assertEqual(self.client.state, CONNECTED)

    def test_login_password_contains_space_character(self):
        self.assertEqual(self.client.state, CONNECTED)
        self.assertEqual(self.client.login(self.user, 'pass 2'), (False, 'LOGIN:incorrect'))
        self.assertEqual(self.client.state, CONNECTED)

    def test_login_state_error(self):
        self.assertEqual(self.client.state, CONNECTED)
        self.assertEqual(self.client.login(self.user, 'pass3'), (True, 'LOGIN:{} OK'.format(self.user)))
        self.assertEqual(self.client.state, GAME_WAITING)
        self.assertRaises(AssertionError, self.client.login, '{}x'.format(self.user), 'pass4')  # already game-waiting
        self.assertEqual(self.client.state, GAME_WAITING)


class TestLogout(unittest.TestCase):

    def setUp(self):
        self.client, self.user = setup()

    def tearDown(self):
        teardown(self.client)

    def test_logout(self):
        self.client.login(self.user, 'pass1')
        self.assertEqual(self.client.state, GAME_WAITING)
        self.assertEqual(self.client.logout(), (True, 'LOGOUT:completed'))
        self.assertEqual(self.client.state, CONNECTED)

    def test_logout_state_error(self):
        self.assertRaises(AssertionError, setup()[0].logout)


class TestGetGameCondition(unittest.TestCase):

    def setUp(self):
        self.c1, self.user1 = setup()
        self.c2, self.user2 = setup()

    def tearDown(self):
        teardown(self.c1)
        teardown(self.c2)

    def test_get_game_condition(self):
        self.c1.login(self.user1, 'pass1')
        self.c2.login(self.user2, 'pass2')
        self.assertEqual(self.c1.state, GAME_WAITING)
        self.assertEqual(self.c2.state, GAME_WAITING)

        cond, message = self.c1.get_game_condition()
        summary = cond['Game_Summary']
        self.assertEqual(summary['Protocol_Version'], '1.1')
        self.assertEqual(summary['Protocol_Mode'], 'Server')
        self.assertEqual(summary['Format'], 'Shogi 1.0')
        self.assertEqual(summary['Declaration'], 'Jishogi 1.1')
        self.assertRegex(summary['Game_ID'], r'.+')
        self.assertIn((summary['Name+'], summary['Name-']), [(self.user1, self.user2), (self.user2, self.user1)])
        self.assertIn(summary['Your_Turn'], ['+', '-'])
        self.assertEqual(summary['Rematch_On_Draw'], 'NO')
        self.assertEqual(summary['To_Move'], '+')
        self.assertEqual(summary['Time']['Time_Unit'], '1sec')
        self.assertEqual(summary['Time']['Total_Time'], '1500')
        self.assertEqual(summary['Time']['Least_Time_Per_Move'], '1')
        self.assertEqual(summary['Position'], '\n'.join([
            'P1-KY-KE-GI-KI-OU-KI-GI-KE-KY',
            'P2 * -HI *  *  *  *  * -KA * ',
            'P3-FU-FU-FU-FU-FU-FU-FU-FU-FU',
            'P4 *  *  *  *  *  *  *  *  * ',
            'P5 *  *  *  *  *  *  *  *  * ',
            'P6 *  *  *  *  *  *  *  *  * ',
            'P7+FU+FU+FU+FU+FU+FU+FU+FU+FU',
            'P8 * +KA *  *  *  *  * +HI * ',
            'P9+KY+KE+GI+KI+OU+KI+GI+KE+KY',
            '+'
        ]))
        self.assertEqual(self.c1.state, AGREE_WAITING)

    def test_get_game_condition_state_error(self):
        self.assertRaises(AssertionError, setup()[0].get_game_condition)


class TestAgree(unittest.TestCase):

    def setUp(self):
        self.c1, self.user1 = setup()
        self.c2, self.user2 = setup()
        self.c1.login(self.user1, 'pass1')
        self.c2.login(self.user2, 'pass2')
        self.assertEqual(self.c1.state, GAME_WAITING)
        self.assertEqual(self.c2.state, GAME_WAITING)
        self.cond1, _ = self.c1.get_game_condition()
        self.cond2, _ = self.c2.get_game_condition()
        self.game_id = self.cond1['Game_Summary']['Game_ID']
        assert self.game_id == self.cond2['Game_Summary']['Game_ID']

    def tearDown(self):
        teardown(self.c1)
        teardown(self.c2)

    def test_agree_state_error(self):
        self.assertRaises(AssertionError, setup()[0].agree, {})

    def test_agree(self):
        self.c1.agree(self.cond1)
        self.assertEqual(self.c1.state, START_WAITING)


class TestGetAgreement(unittest.TestCase):

    def setUp(self):
        self.c1, self.user1 = setup()
        self.c2, self.user2 = setup()
        self.c1.login(self.user1, 'pass1')
        self.c2.login(self.user2, 'pass2')
        self.assertEqual(self.c1.state, GAME_WAITING)
        self.assertEqual(self.c2.state, GAME_WAITING)
        self.cond1, _ = self.c1.get_game_condition()
        self.cond2, _ = self.c2.get_game_condition()
        self.game_id = self.cond1['Game_Summary']['Game_ID']
        assert self.game_id == self.cond2['Game_Summary']['Game_ID']
        if self.cond1['Game_Summary']['To_Move'] == self.cond1['Game_Summary']['Your_Turn']:
            self.black = self.c1
            self.white = self.c2
        else:
            self.black = self.c2
            self.white = self.c1

    def tearDown(self):
        teardown(self.c1)
        teardown(self.c2)

    def test_get_agreement_state_error(self):
        self.assertRaises(AssertionError, setup()[0].get_agreement, {})

    def test_get_agreement_after_peer_agree(self):
        self.c2.agree(self.cond2)
        self.c1.agree(self.cond1)

        self.assertEqual(self.c1.get_agreement(self.cond1), (True, 'START:{}'.format(self.game_id)))
        self.assertEqual(self.c2.get_agreement(self.cond2), (True, 'START:{}'.format(self.game_id)))

        self.assertEqual(self.black.state, GAME_TO_MOVE)
        self.assertEqual(self.white.state, GAME_TO_WAIT)

    def test_get_agreement_after_peer_reject(self):
        self.c2.reject(self.cond2)
        self.c1.agree(self.cond1)

        self.assertEqual(self.c1.get_agreement(self.cond1),
                         ((False, 'REJECT:{} by {}'.format(self.game_id, self.user2))))
        self.assertEqual(self.c1.state, GAME_WAITING)

    def test_get_agreement_before_peer_agree(self):
        self.c1.agree(self.cond1)
        ret, state2 = a_before_b(partial(CsaClient.get_agreement, self.c1, self.cond1),
                                 exec_then_get_state(CsaClient.agree, self.c2, self.cond2))

        self.assertEqual(ret, (True, 'START:{}'.format(self.game_id)))

        self.c2.state = state2  # fix state of subprocess
        self.c2.get_agreement(self.cond2)

        self.assertEqual(self.black.state, GAME_TO_MOVE)
        self.assertEqual(self.white.state, GAME_TO_WAIT)

    def test_get_agreement_before_peer_reject(self):
        self.c1.agree(self.cond1)
        ret, state2 = a_before_b(partial(CsaClient.get_agreement, self.c1, self.cond1),
                                 exec_then_get_state(CsaClient.reject, self.c2, self.cond2))

        self.assertEqual(ret, ((False, 'REJECT:{} by {}'.format(self.game_id, self.user2))))
        self.assertEqual(self.c1.state, GAME_WAITING)


class TestReject(unittest.TestCase):

    def setUp(self):
        self.c1, self.user1 = setup()
        self.c2, self.user2 = setup()
        self.c1.login(self.user1, 'pass1')
        self.c2.login(self.user2, 'pass2')
        self.assertEqual(self.c1.state, GAME_WAITING)
        self.assertEqual(self.c2.state, GAME_WAITING)
        self.cond1, _ = self.c1.get_game_condition()
        self.cond2, _ = self.c2.get_game_condition()
        self.game_id = self.cond1['Game_Summary']['Game_ID']
        assert self.game_id == self.cond2['Game_Summary']['Game_ID']

    def tearDown(self):
        teardown(self.c1)
        teardown(self.c2)

    def test_reject_state_error(self):
        self.assertRaises(AssertionError, setup()[0].reject, {})

    def test_reject_before_peer_respond(self):
        self.assertEqual(self.c1.reject(self.cond1), ('REJECT:{} by {}'.format(self.game_id, self.user1)))
        self.assertEqual(self.c1.state, GAME_WAITING)

    def test_reject_after_peer_agree(self):
        ret, state2 = a_after_b(partial(CsaClient.reject, self.c1, self.cond1),
                                exec_then_get_state(CsaClient.agree, self.c2, self.cond2))
        self.assertEqual(ret, ('REJECT:{} by {}'.format(self.game_id, self.user1)))
        self.assertEqual(self.c1.state, GAME_WAITING)

    def test_reject_after_peer_reject(self):
        ret, state2 = a_after_b(partial(CsaClient.reject, self.c1, self.cond1),
                                exec_then_get_state(CsaClient.reject, self.c2, self.cond2))
        self.assertEqual(ret, ('REJECT:{} by {}'.format(self.game_id, self.user2)))
        self.assertEqual(self.c1.state, GAME_WAITING)


class TestMove(unittest.TestCase):

    def setUp(self):
        self.c1, self.user1 = setup()
        self.c2, self.user2 = setup()
        self.c1.login(self.user1, 'pass1')
        self.c2.login(self.user2, 'pass2')
        self.assertEqual(self.c1.state, GAME_WAITING)
        self.assertEqual(self.c2.state, GAME_WAITING)
        self.cond1, _ = self.c1.get_game_condition()
        self.cond2, _ = self.c2.get_game_condition()
        self.game_id = self.cond1['Game_Summary']['Game_ID']
        assert self.game_id == self.cond2['Game_Summary']['Game_ID']
        if self.cond1['Game_Summary']['To_Move'] == self.cond1['Game_Summary']['Your_Turn']:
            self.black = self.c1
            self.white = self.c2
        else:
            self.black = self.c2
            self.white = self.c1
        self.c1.agree(self.cond1)
        self.c2.agree(self.cond2)
        self.c1.get_agreement(self.cond1)
        self.c2.get_agreement(self.cond2)

    def tearDown(self):
        teardown(self.c1)
        teardown(self.c2)

    def test_move_state_error(self):
        self.assertRaises(AssertionError, setup()[0].move, '+7776FU')

    def test_move(self):
        # includes test of get_move method
        self.assertEqual(self.black.move('+7776FU'), (True, 1))
        self.assertEqual(self.white.get_move(), (True, ('+7776FU', 1)))
        self.assertEqual(self.black.state, GAME_TO_WAIT)
        self.assertEqual(self.white.state, GAME_TO_MOVE)

    def test_move_illegal(self):
        # includes test of get_move method
        self.assertEqual(self.black.move('+7777FU'), (False, (None, '#ILLEGAL_MOVE', '#LOSE')))
        self.assertIn(self.white.get_move(),
                      [(False, (x, y, '#ILLEGAL_MOVE', '#WIN')) for x, y in [(None, None), ('+7777FU', 1)]])
        self.assertEqual(self.black.state, GAME_WAITING)
        self.assertEqual(self.white.state, GAME_WAITING)

    def test_move_illegal_percent(self):
        self.assertRaisesRegexp(AssertionError, 'move string format error: %', CsaClient.move, self.black, '%')

    def test_move_illegal_hash(self):
        self.assertRaisesRegexp(AssertionError, 'move string format error: #', CsaClient.move, self.black, '#')

    def test_move_sennichite(self):
        # includes test of get_move method
        replay_history(self.black, self.white, ['+5958OU'] + ['-5152OU', '+5859OU', '-5251OU', '+5958OU'] * 3)

        self.assertIn(self.white.move('-5152OU'),
                      [(False, (x, '#SENNICHITE', '#DRAW')) for x in [None, 1]])
        self.assertIn(self.black.get_move(),
                      [(False, (x, y, '#SENNICHITE', '#DRAW')) for x, y in [(None, None), ('-5152OU', 1)]])

        self.assertEqual(self.black.state, GAME_WAITING)
        self.assertEqual(self.white.state, GAME_WAITING)

    def test_move_oute_sennichite(self):
        # includes test of get_move method
        replay_history(self.black, self.white, [
            '+7776FU', '-3334FU', '+8833UM', '-5152OU', '+3343UM',
        ] + ['-5251OU', '+4333UM', '-5152OU', '+3343UM'] * 3)

        self.assertIn(self.white.move('-5251OU'),
                      [(False, (x, '#OUTE_SENNICHITE', '#WIN')) for x in [None, 1]])
        self.assertIn(self.black.get_move(),
                      [(False, (x, y, '#OUTE_SENNICHITE', '#LOSE')) for x, y in [(None, None), ('-5251OU', 1)]])

        self.assertEqual(self.black.state, GAME_WAITING)
        self.assertEqual(self.white.state, GAME_WAITING)


class TestResign(unittest.TestCase):

    def setUp(self):
        self.c1, self.user1 = setup()
        self.c2, self.user2 = setup()
        self.c1.login(self.user1, 'pass1')
        self.c2.login(self.user2, 'pass2')
        self.assertEqual(self.c1.state, GAME_WAITING)
        self.assertEqual(self.c2.state, GAME_WAITING)
        self.cond1, _ = self.c1.get_game_condition()
        self.cond2, _ = self.c2.get_game_condition()
        self.game_id = self.cond1['Game_Summary']['Game_ID']
        assert self.game_id == self.cond2['Game_Summary']['Game_ID']
        if self.cond1['Game_Summary']['To_Move'] == self.cond1['Game_Summary']['Your_Turn']:
            self.black = self.c1
            self.white = self.c2
        else:
            self.black = self.c2
            self.white = self.c1
        self.c1.agree(self.cond1)
        self.c2.agree(self.cond2)
        self.c1.get_agreement(self.cond1)
        self.c2.get_agreement(self.cond2)

    def tearDown(self):
        teardown(self.c1)
        teardown(self.c2)

    def test_resign_state_error(self):
        self.assertRaises(AssertionError, setup()[0].resign)

    def test_resign(self):
        # includes test of get_move method
        self.assertIn(self.black.resign(), [(x, '#RESIGN', '#LOSE') for x in [None, 1]])
        self.assertIn(self.white.get_move(),
                      [(False, ('%TORYO', x, '#RESIGN', '#WIN')) for x in [None, 1]])
        self.assertEqual(self.black.state, GAME_WAITING)
        self.assertEqual(self.white.state, GAME_WAITING)


class TestDeclareWin(unittest.TestCase):

    def setUp(self):
        self.c1, self.user1 = setup()
        self.c2, self.user2 = setup()
        self.c1.login(self.user1, 'pass1')
        self.c2.login(self.user2, 'pass2')
        self.assertEqual(self.c1.state, GAME_WAITING)
        self.assertEqual(self.c2.state, GAME_WAITING)
        self.cond1, _ = self.c1.get_game_condition()
        self.cond2, _ = self.c2.get_game_condition()
        self.game_id = self.cond1['Game_Summary']['Game_ID']
        assert self.game_id == self.cond2['Game_Summary']['Game_ID']
        if self.cond1['Game_Summary']['To_Move'] == self.cond1['Game_Summary']['Your_Turn']:
            self.black = self.c1
            self.white = self.c2
        else:
            self.black = self.c2
            self.white = self.c1
        self.c1.agree(self.cond1)
        self.c2.agree(self.cond2)
        self.c1.get_agreement(self.cond1)
        self.c2.get_agreement(self.cond2)

    def tearDown(self):
        teardown(self.c1)
        teardown(self.c2)

    def test_declare_win_state_error(self):
        self.assertRaises(AssertionError, setup()[0].declare_win)

    def test_declare_win(self):
        # includes test of get_move method
        replay_history(self.black, self.white, [
            '+7776FU', '-4142KI', '+8833KA', '-5141OU', '+3342KA', '-4132OU', '+4231UM', '-3233OU',
            '+3122UM', '-3324OU', '+2211UM', '-2414OU', '+1121UM', '-1424OU', '+2143UM', '-2414OU',
            '+4361UM', '-1424OU', '+6171UM', '-2414OU', '+7182UM', '-1424OU', '+8281UM', '-2414OU',
            '+8191UM', '-1424OU', '+5968OU', '-2414OU', '+6877OU', '-1424OU', '+7766OU', '-2414OU',
            '+7675FU', '-1424OU', '+6665OU', '-2414OU', '+7574FU', '-1424OU', '+7473TO', '-2414OU',
            '+7363TO', '-1424OU', '+2878HI', '-2414OU', '+7872RY', '-1424OU', '+6564OU', '-2414OU',
            '+6453OU', '-1424OU', '+0043KE', '-2414OU', '+0033GI', '-1415OU', '+0011HI', '-1514OU',
            '+0012KA', '-1415OU', '+0042KI', '-1514OU', '+0052KY', '-1415OU', '+0073FU', '-1514OU',
        ])

        self.assertEqual(self.black.declare_win(), (1, '#JISHOGI', '#WIN'))
        self.assertEqual(self.white.get_move(), (False, ('%KACHI', 1, '#JISHOGI', '#LOSE')))
        self.assertEqual(self.black.state, GAME_WAITING)
        self.assertEqual(self.white.state, GAME_WAITING)

    def test_declare_win_illegal(self):
        # includes test of get_move method
        self.assertIn(self.black.declare_win(), [(x, '#ILLEGAL_MOVE', '#LOSE') for x in [None, 1]])
        self.assertIn(self.white.get_move(),
                      [(False, (x, y, '#ILLEGAL_MOVE', '#WIN')) for x, y in [(None, None), ('%KACHI', 1)]])
        self.assertEqual(self.black.state, GAME_WAITING)
        self.assertEqual(self.white.state, GAME_WAITING)


class TestGetMove(unittest.TestCase):
    def test_declare_win_state_error(self):
        self.assertRaises(AssertionError, setup()[0].get_move)


if __name__ == '__main__':
    unittest.main()
