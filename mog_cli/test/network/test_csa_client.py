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

logger.setLevel(logging.INFO)

# counter for making unique username
counter = 0


def setup():
    global counter
    counter += 1
    return CsaClient(SHOGI_SERVER_HOST), 'user{}'.format(counter)


def teardown(client):
    try:
        client.logout()
    except (StateError, ProtocolError, ConnectionResetError, ClosedConnectionError):
        pass
    client.close()


def exec_then_get_state(func, client, *args, **kwargs):
    """Returns partial function."""
    def f():
        func(client, *args, **kwargs)
        return client.state
    return f


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
        self.assertRaises(StateError, self.client.login, '{}x'.format(self.user), 'pass4')  # already GameWaiting state
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
        self.assertEqual(self.client.state, CONNECTED)
        self.assertRaises(StateError, self.client.logout)
        self.assertEqual(self.client.state, CONNECTED)


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
        self.assertEqual(self.c1.state, CONNECTED)
        self.assertRaises(StateError, self.c1.get_game_condition)
        self.assertEqual(self.c1.state, CONNECTED)


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

    def tearDown(self):
        teardown(self.c1)
        teardown(self.c2)

    def test_agree_after_peer_agree(self):
        ret, state2 = a_after_b(partial(CsaClient.agree, self.c1, self.cond1),
                                exec_then_get_state(CsaClient.agree, self.c2, self.cond2))

        self.assertEqual(ret, (True, 'START:{}'.format(self.game_id)))
        if self.cond1['Game_Summary']['To_Move'] == self.cond1['Game_Summary']['Your_Turn']:
            self.assertEqual(self.c1.state, GAME_PLAYING)
            self.assertEqual(state2, GAME_WAITING)
        else:
            self.assertEqual(self.c1.state, GAME_WAITING)
            self.assertEqual(state2, GAME_PLAYING)

    def test_agree_after_peer_reject(self):
        ret, state2 = a_after_b(partial(CsaClient.agree, self.c1, self.cond1),
                                exec_then_get_state(CsaClient.reject, self.c2, self.cond2))

        self.assertEqual(ret, ((False, 'REJECT:{} by {}'.format(self.game_id, self.user2))))
        self.assertEqual(self.c1.state, GAME_WAITING)

    def test_agree_before_peer_agree(self):
        ret, state2 = a_before_b(partial(CsaClient.agree, self.c1, self.cond1),
                                 exec_then_get_state(CsaClient.agree, self.c2, self.cond2))

        self.assertEqual(ret, (True, 'START:{}'.format(self.game_id)))
        if self.cond1['Game_Summary']['To_Move'] == self.cond1['Game_Summary']['Your_Turn']:
            self.assertEqual(self.c1.state, GAME_PLAYING)
            self.assertEqual(state2, GAME_WAITING)
        else:
            self.assertEqual(self.c1.state, GAME_WAITING)
            self.assertEqual(state2, GAME_PLAYING)

    def test_agree_before_peer_reject(self):
        ret, state2 = a_before_b(partial(CsaClient.agree, self.c1, self.cond1),
                                 exec_then_get_state(CsaClient.reject, self.c2, self.cond2))

        self.assertEqual(ret, ((False, 'REJECT:{} by {}'.format(self.game_id, self.user2))))
        self.assertEqual(self.c1.state, GAME_WAITING)

    def test_agree_state_error(self):
        c = setup()[0]
        self.assertEqual(c.state, CONNECTED)
        self.assertRaises(StateError, c.agree, ({}, ))
        self.assertEqual(c.state, CONNECTED)


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

    def tearDown(self):
        teardown(self.c1)
        teardown(self.c2)

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

    def test_reject_state_error(self):
        c = setup()[0]
        self.assertEqual(c.state, CONNECTED)
        self.assertRaises(StateError, c.reject, ({}, ))
        self.assertEqual(c.state, CONNECTED)


if __name__ == '__main__':
    unittest.main()
