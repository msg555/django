from subprocess import CalledProcessError, PIPE
from unittest import mock, skipUnless

from django.db import connection
from django.db.backends.sqlite3.client import DatabaseClient
from django.test import TestCase


@skipUnless(connection.vendor == 'sqlite', 'SQLite tests')
class SqliteDbshellCommandTestCase(TestCase):

    def test_exec(self):
        client = DatabaseClient(connection)
        run_result = client.runshell(input=b'.databases\n', stdout=PIPE, stderr=PIPE)
        self.assertTrue(run_result.stdout)
        self.assertFalse(run_result.stderr)

    def test_fail_exec(self):
        client = DatabaseClient(connection)
        self.assertRaises(CalledProcessError, client.runshell, input=b'.invalid\n', stdout=PIPE, stderr=PIPE)
