import subprocess

from django.db.backends.base.client import BaseDatabaseClient


class DatabaseClient(BaseDatabaseClient):
    executable_name = 'sqlite3'

    def runshell(self, **run_kwargs):
        args = [self.executable_name,
                self.connection.settings_dict['NAME']]
        return subprocess.run(args, check=True, **run_kwargs)
