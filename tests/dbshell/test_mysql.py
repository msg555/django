from subprocess import CalledProcessError, PIPE
from unittest import skipUnless

from django.db import connection
from django.db.backends.mysql.client import DatabaseClient
from django.test import TestCase


class MySqlDbshellCommandTestCase(TestCase):

    def test_fails_with_keyerror_on_incomplete_config(self):
        with self.assertRaises(KeyError):
            self.get_command_line_arguments({})

    def test_basic_params_specified_in_settings(self):
        self.assertEqual(
            ['mysql', '--user=someuser', '--password=somepassword',
             '--host=somehost', '--port=444', 'somedbname'],
            self.get_command_line_arguments({
                'NAME': 'somedbname',
                'USER': 'someuser',
                'PASSWORD': 'somepassword',
                'HOST': 'somehost',
                'PORT': 444,
                'OPTIONS': {},
            }))

    def test_options_override_settings_proper_values(self):
        settings_port = 444
        options_port = 555
        self.assertNotEqual(settings_port, options_port, 'test pre-req')
        self.assertEqual(
            ['mysql', '--user=optionuser', '--password=optionpassword',
             '--host=optionhost', '--port={}'.format(options_port), 'optiondbname'],
            self.get_command_line_arguments({
                'NAME': 'settingdbname',
                'USER': 'settinguser',
                'PASSWORD': 'settingpassword',
                'HOST': 'settinghost',
                'PORT': settings_port,
                'OPTIONS': {
                    'db': 'optiondbname',
                    'user': 'optionuser',
                    'passwd': 'optionpassword',
                    'host': 'optionhost',
                    'port': options_port,
                },
            }))

    def test_can_connect_using_sockets(self):
        self.assertEqual(
            ['mysql', '--user=someuser', '--password=somepassword',
             '--socket=/path/to/mysql.socket.file', 'somedbname'],
            self.get_command_line_arguments({
                'NAME': 'somedbname',
                'USER': 'someuser',
                'PASSWORD': 'somepassword',
                'HOST': '/path/to/mysql.socket.file',
                'PORT': None,
                'OPTIONS': {},
            }))

    def test_ssl_certificate_is_added(self):
        self.assertEqual(
            ['mysql', '--user=someuser', '--password=somepassword',
             '--host=somehost', '--port=444', '--ssl-ca=sslca',
             '--ssl-cert=sslcert', '--ssl-key=sslkey', 'somedbname'],
            self.get_command_line_arguments({
                'NAME': 'somedbname',
                'USER': 'someuser',
                'PASSWORD': 'somepassword',
                'HOST': 'somehost',
                'PORT': 444,
                'OPTIONS': {
                    'ssl': {
                        'ca': 'sslca',
                        'cert': 'sslcert',
                        'key': 'sslkey',
                    },
                },
            }))

    @skipUnless(connection.vendor == 'mysql', 'MySQL tests')
    def test_exec(self):
        client = DatabaseClient(connection)
        run_result = client.runshell(input=b'SHOW VARIABLES', stdout=PIPE, stderr=PIPE)
        self.assertTrue(run_result.stdout)
        self.assertFalse(run_result.stderr)

    @skipUnless(connection.vendor == 'mysql', 'MySQL tests')
    def test_exec(self):
        client = DatabaseClient(connection)
        self.assertRaises(CalledProcessError, client.runshell, input=b'invalid', stdout=PIPE, stderr=PIPE)

    def get_command_line_arguments(self, connection_settings):
        return DatabaseClient.settings_to_cmd_args(connection_settings)
