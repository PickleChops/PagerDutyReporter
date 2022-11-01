import sys
from distutils.fancy_getopt import FancyGetopt
from datetime import datetime, timedelta, timezone
import distutils.errors

import logger


class CommandParser:
    """Read the command line options"""

    OPTIONS = [
        ('help', 'h', 'Show this help message'),
        ('team=', 't', 'Pagerduty Team ID'),
        ('service=', 's', 'Pagerduty Service ID'),
        ('key=', 'k', 'PagerDuty API key - defaults to looking for a ~/.pd file'),
        ('csv', 'c', 'Output as csv'),
        ('group=', 'g', 'Group by field, e.g. --group="description"'),
        ('full', 'f', 'Full descriptions, default is to shorten'),
        ('debug', 'x', 'Debug output'),
        ('report', 'r', 'Output full report')
    ]

    def __init__(self):
        self.help = False
        self.team = None
        self.service = None
        self.start = None
        self.end = None
        self.key = None
        self.csv = False
        self.group = None
        self.full = False
        self.debug = False
        self.report = False
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
 
Fetch incidents from the Support Operations Pagerduty service

pd <flags> [start date] [end date]

Example:
       
  pd -t PSYEN6X -s P2APASH --group="Description" 2022-10-25
    
  Output incidents from 2022-10-25 until today, grouped by the "Description" column
    
Supported Fields:

  "Incident", "Created", "Description", "Ack", "Status", "Urgency", "Html_url"

Flags
-----
""")

    def _parse_args(self):

        date_format = '%Y-%m-%d'

        if self.help:
            self.show_help()
            sys.exit(0)

        if self.team is None:
            logger.info("You need to specify a Pagerduty Team ID")
            sys.exit(0)

        if self.service is None:
            logger.info("You need to specify a Pagerduty Service ID")
            sys.exit(0)

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

        if self.group == "":
            print("Group by field required")
            sys.exit(1)

        if self.report:
            logger.info("Full report output requested")
