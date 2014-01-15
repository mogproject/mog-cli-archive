#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""Test"""

import unittest
import logging

from network.csa_client import *

HOSTNAME = 'docker1'

# logger.setLevel(logging.INFO)


def setup():
    return CsaClient(HOSTNAME)


def teardown(client):
    try:
        client.logout()
    except (StateError, ProtocolError):
        pass
    client.close()


class TestLogin(unittest.TestCase):

    def setUp(self):
        self.client = setup()

    def tearDown(self):
        teardown(self.client)

    def test_login(self):
        self.assertEqual(self.client.state, CONNECTED)
        self.assertEqual(self.client.login('user1', 'pass1'), (True, 'LOGIN:user1 OK'))
        self.assertEqual(self.client.state, GAME_WAITING)

    def test_login_same_username_different_password(self):
        self.assertEqual(self.client.state, CONNECTED)
        with CsaClient(HOSTNAME) as c:
            self.assertEqual(c.state, CONNECTED)
            c.login('user1', 'pass1')
            self.assertEqual(c.state, GAME_WAITING)
            self.assertEqual(
                self.client.login('user1', 'pass2'), (False, 'LOGIN:incorrect'))
        self.assertEqual(self.client.state, CONNECTED)

    def test_login_empty_username_or_password(self):
        self.assertEqual(self.client.state, CONNECTED)
        self.assertEqual(self.client.login('', 'pass1'), (False, 'LOGIN:incorrect'))
        self.assertEqual(self.client.state, CONNECTED)
        self.assertEqual(self.client.login('user1', ''), (False, 'LOGIN:incorrect'))
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
        self.assertEqual(self.client.login('user2', 'pass 2'), (False, 'LOGIN:incorrect'))
        self.assertEqual(self.client.state, CONNECTED)

    def test_login_state_error(self):
        self.assertEqual(self.client.state, CONNECTED)
        self.assertEqual(self.client.login('user3', 'pass3'), (True, 'LOGIN:user3 OK'))
        self.assertEqual(self.client.state, GAME_WAITING)
        self.assertRaises(StateError, self.client.login, 'user4', 'pass4')  # already GameWaiting state
        self.assertEqual(self.client.state, GAME_WAITING)


class TestLogout(unittest.TestCase):

    def setUp(self):
        self.client = setup()

    def tearDown(self):
        teardown(self.client)

    def test_logout(self):
        self.client.login('user1', 'pass1')
        self.assertEqual(self.client.state, GAME_WAITING)
        self.assertEqual(self.client.logout(), (True, 'LOGOUT:completed'))
        self.assertEqual(self.client.state, CONNECTED)

    def test_logout_state_error(self):
        self.assertEqual(self.client.state, CONNECTED)
        self.assertRaises(StateError, self.client.logout)
        self.assertEqual(self.client.state, CONNECTED)


class TestGetGameCondition(unittest.TestCase):

    def setUp(self):
        self.c1 = setup()
        self.c2 = setup()

    def tearDown(self):
        teardown(self.c1)
        teardown(self.c2)

    def test_get_game_condition(self):
        self.c1.login('user1', 'pass1')
        self.c2.login('user2', 'pass2')
        self.assertEqual(self.c1.state, GAME_WAITING)
        self.assertEqual(self.c2.state, GAME_WAITING)
        cond, message = self.c1.get_game_condition()
        summary = cond['Game_Summary']
        self.assertEqual(summary['Protocol_Version'], '1.1')
        self.assertEqual(self.c1.state, AGREE_WAITING)

if __name__ == '__main__':
    unittest.main()
