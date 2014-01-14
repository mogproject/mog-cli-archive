#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""Test"""

import unittest
from network.csa_client import CsaClient, StateError


class TestLogin(unittest.TestCase):

    def setUp(self):
        self.client = CsaClient('docker1')

    def tearDown(self):
        self.client.close()

    def test_login(self):
        self.assertEqual(self.client.login('user1', 'pass1'), (True, 'LOGIN:user1 OK'))

    def test_login_username_too_long(self):
        self.assertEqual(
            self.client.login('0123456789abcdef0123456789abcdef0', 'pass1'), (False, 'LOGIN:incorrect'))

    def test_login_username_contains_invalid_character(self):
        self.assertEqual(self.client.login('user+', 'pass1'), (False, 'LOGIN:incorrect'))

    def test_login_password_contains_space_character(self):
        self.assertEqual(self.client.login('user2', 'pass 2'), (False, 'LOGIN:incorrect'))

    def test_login_state_error(self):
        self.assertEqual(self.client.login('user3', 'pass3'), (True, 'LOGIN:user3 OK'))
        self.assertRaises(StateError, self.client.login, 'user4', 'pass4')  # already GameWaiting state


class TestLogout(unittest.TestCase):

    def setUp(self):
        self.client = CsaClient('docker1')

    def tearDown(self):
        self.client.close()

    def test_logout(self):
        self.assertEqual(self.client.login('user1', 'pass1'), (True, 'LOGIN:user1 OK'))
        self.assertEqual(self.client.logout(), (True, 'LOGOUT:completed'))

    def test_logout_state_error(self):
        self.assertRaises(StateError, self.client.logout)


if __name__ == '__main__':
    unittest.main()
