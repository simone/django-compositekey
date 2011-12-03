__author__ = 'aldaran'

from django.conf import settings
from django.db import connection
from django.core.management import call_command

class ShowSQL:
    def __init__(self, name=None):
        self.name = name
        self.enable = True

    def __enter__(self):
        if self.enable:
            settings.DEBUG = True
            connection.queries = []

    def __exit__(self, *exc_info):
        if self.enable:
            for i, query in enumerate(connection.queries):
                print " %s)\n%s\n\n" % (i, query['sql'])
            connection.queries = []
            settings.DEBUG = False
            if self.name:
                call_command("sqlall", self.name)