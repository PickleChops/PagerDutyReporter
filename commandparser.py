import sys
from distutils.fancy_getopt import FancyGetopt
from datetime import datetime, timedelta
import distutils.errors

import logger


class CommandParser:
    """Read the command line options"""

    FORMAT_PRETTY = 'pretty'
    FORMAT_CSV = 'csv'
    FORMAT_CONFLUENCE = 'confluence'

    OPTIONS = [
        ('help', 'h', 'Show this help message'),
        ('teams=', 't', 'Pagerduty Team IDs, comma separated'),
        ('services=', 's', 'Pagerduty Service IDs, comma separated'),
        ('logs', 'l', 'Read log entries for each incident'),
        ('notes', 'n', 'Read notes for each incident'),
        ('key=', 'k', 'PagerDuty API key, defaults to looking for a ~/.pd.toml file'),
        ('format=', 'o', f"Output [{FORMAT_PRETTY}|{FORMAT_CSV}|{FORMAT_CONFLUENCE}], default {FORMAT_PRETTY}"),
        ('group=', 'g', 'Group by field, e.g. --group="description"'),
        ('fuzz', 'z', 'Fuzz matching on grouping'),
        ('fuzz-score=', 'm', 'Fuzz matching threshold - default is 90%'),
        ('full', 'f', 'Full descriptions, default is to shorten'),
        ('report', 'r', 'Output full report'),
        ('debug', 'x', 'Debug output'),
    ]

    def __init__(self):
        self.help = False
        self.teams = None
        self.services = None
        self.start = None
        self.end = None
        self.logs = False
        self.notes = False
        self.key = None
        self.format = self.FORMAT_PRETTY
        self.group = None
        self.fuzz = False
        self.fuzz_match = 90
        self.full = False
        self.debug = False
        self.report = False
        self.confluence = False
        self.args = None

        self.parser = FancyGetopt(option_table=self.OPTIONS)

        try:
            self.args = self.parser.getopt(object=self)
            self._parse_args()
        except distutils.errors.DistutilsArgError:
            self.show_help()
            sys.exit(1)

    def show_help(self):
        self.parser.print_help(
            """
pd
----
 
Fetch incidents from Pagerduty services and output them in a few different ways

pd <flags> [start date] [end date]

Example:
       
  pd -t PSXXXXX -s P1YYYYY --group="Description" 2022-10-25
    
  Output incidents from 2022-10-25 until today, grouped by the "Description" column
    
Supported Fields:

  "Service", "Team", "Incident", "Created", "Description", "Ack", "Urgency", "Resolution Tine"

Flags
-----
""")

    def _parse_args(self):

        date_format = '%Y-%m-%d'

        if self.help:
            self.show_help()
            sys.exit(0)

        if self.teams is None:
            logger.fatal("You need to specify at least one Pagerduty Team ID")

        # Split by comma, trim whitespace, and remove any empty list items
        self.teams = list(filter(None, [i.strip() for i in self.teams.split(",")]))

        if self.services is None:
            logger.fatal("You need to specify at least one Pagerduty Service ID")

        # Split by comma, trim whitespace, and remove any empty list items
        self.services = list(filter(None, [i.strip() for i in self.services.split(",")]))

        if len(self.args) == 0:
            self.start = datetime.today()
            self.end = datetime.today() + timedelta(days=1)
            logger.info("No dates specified - defaulting to today")
        else:
            start_date_string = self.args[0]
            self.start = datetime.strptime(start_date_string, date_format)

            if len(self.args) > 1:
                end_date_string = self.args[1]
                self.end = datetime.strptime(end_date_string, date_format)
            else:
                self.end = datetime.today() + timedelta(days=1)
                logger.info("No end date specified, defaulting to end date of today")

        if self.format.lower() not in [self.FORMAT_PRETTY,self.FORMAT_CSV,self.FORMAT_CONFLUENCE]:
            logger.fatal(f"Format must be one of [{self.FORMAT_PRETTY}|{self.FORMAT_CSV}|{self.FORMAT_CONFLUENCE}]")

        if self.logs:
            logger.info("Will read incident logs (slow and just provides Ack info)")

        if self.group == "":
            logger.fatal("When using the group flag it can not be empty")

        if self.fuzz and self.group != "":
            logger.info("Fuzzy grouping enabled. Beware incorrect grouping")

        if self.report:
            logger.info("Full report output requested")
