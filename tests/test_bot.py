"""Module used to test bot worker module methods."""

import unittest

import bot.worker as worker

__author__ = 'Jonarzz'


class BotWorkerTest(unittest.TestCase):
    """Class used to test bot worker module.
    Inherits from TestCase class of unittest module.
    """

    def test_prepare_response(self):
        """Method that tests the prepare_response method from dotaresponses module.

        It checks whether the returned value is the same as the expected string.
        """
        self.assertEqual(worker.parse_comment("That's a great idea!!!"), "that s a great idea")
        self.assertEqual(worker.parse_comment("  WoNdErFuL  "), "wonderful")
        self.assertEqual(worker.parse_comment("How are you?"), "how are you")
