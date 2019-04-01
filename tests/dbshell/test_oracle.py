from subprocess import CalledProcessError, PIPE
from unittest import mock, skipUnless

from django.db import connection
from django.db.backends.oracle.client import DatabaseClient
from django.test import TestCase


@skipUnless(connection.vendor == 'oracle', 'Oracle tests')
class OracleDbshellTests(TestCase):
    def _run_dbshell(self, rlwrap=False, **run_kwargs):
        """Run runshell command and capture its arguments."""
        def _mock_subprocess_call(*args, **kwargs):
            self.subprocess_args = tuple(*args)
            self.subprocess_kwargs = dict(kwargs)
            return 0

        client = DatabaseClient(connection)
        self.subprocess_args = None
        with mock.patch('subprocess.run', new=_mock_subprocess_call):
            with mock.patch('shutil.which', return_value='/usr/bin/rlwrap' if rlwrap else None):
                client.runshell(**run_kwargs)
        return self.subprocess_args, self.subprocess_kwargs

    def test_without_rlwrap(self):
        run_args, run_kwargs = self._run_dbshell(rlwrap=False)
        self.assertEqual(
            run_args,
            ('sqlplus', '-L', connection._connect_string()),
        )
        self.assertEqual(
            run_kwargs,
            {'check': True},
        )

    def test_with_rlwrap(self):
        run_args, run_kwargs = self._run_dbshell(rlwrap=True)
        self.assertEqual(
            run_args,
            ('/usr/bin/rlwrap', 'sqlplus', '-L', connection._connect_string()),
        )
        self.assertEqual(
            run_kwargs,
            {'check': True},
        )

    def test_with_input(self):
        run_args, run_kwargs = self._run_dbshell(rlwrap=True, input=b'testdata')
        self.assertEqual(
            run_args,
            ('/usr/bin/rlwrap', 'sqlplus', '-L', connection._connect_string()),
        )
        self.assertEqual(
            run_kwargs,
            {'check': True, 'input': b'testdata'},
        )

    def test_exec(self):
        client = DatabaseClient(connection)
        run_result = client.runshell(input=b'SELECT * FROM user_tables;', stdout=PIPE, stderr=PIPE)
        self.assertTrue(run_result.stdout)
        self.assertFalse(run_result.stderr)

    def test_fail_exec(self):
        # The sqlplus Oracle client does not fail on invalid SQL queries. Mock login fail instead.
        client = DatabaseClient(connection)
        with mock.patch('django.db.backends.oracle.base.DatabaseWrapper._connect_string') as mock_connect_string:
            mock_connect_string.return_value = 'invalid'
            self.assertRaises(CalledProcessError, client.runshell, input=b'SELECT * FROM user_tables;', stdout=PIPE, stderr=PIPE)
            mock_connect_string.assert_called_once()
