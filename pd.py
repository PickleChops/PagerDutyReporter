#!/usr/bin/env python3

import sys
from beautifultable import BeautifulTable
from commandparser import CommandParser
from incident import Incident
from pageduty import Pagerduty
from logger import info


def main():
    date_format = '%Y-%m-%d'

    options = CommandParser()

    key = options.key
    if options.key is None:
        key = fetch_key_from_file()

        info(f"Using Pagerduty Service ID {options.service} with Team ID {options.team}")

    info(
        f"Searching for incidents >= {options.start.strftime(date_format)} 00:00:00 < {options.end.strftime(date_format)} 00:00:00")

    incidents = fetch_incidents(Pagerduty(key,options.team, options.service), options)

    if len(incidents) == 0:
        return

    if options.report:
        full_report(incidents, options)
    else:
        single_report(incidents, options)


def full_report(incidents, options):
    output(transform_flat(incidents, options), options.csv)
    options.group = "Description"
    output(transform_grouped(incidents, options), options.csv)
    options.group = "Ack"
    output(transform_grouped(incidents, options), options.csv)


def single_report(incidents, options):
    if options.group is None:
        output(transform_flat(incidents, options), options.csv)
    else:
        output(transform_grouped(incidents, options), options.csv)


def output(data, csv):
    if csv:
        output_csv(data)
    else:
        output_pretty(data)


def fetch_key_from_file():
    from os.path import expanduser
    api_key_file = f"{expanduser('~')}/.pd"
    key = None

    try:
        f = open(api_key_file)
        key = f.read().strip()
        f.close()
    except:
        error_exit(f"No api key found in {api_key_file}")

    return key


def escape_quotes(s):
    return s.replace('"', '\\"')


def error_exit(h):
    print(h)
    sys.exit(1)


def output_pretty(flat_data):
    table = BeautifulTable(maxwidth=160)
    table.set_style(BeautifulTable.STYLE_BOX_ROUNDED)
    table.columns.header = flat_data[0]

    for row in flat_data[1:]:
        table.rows.append(row)

    print(table)


def output_csv(data):
    for row in data:
        line = ""
        for item in row:
            line += f"\"{escape_quotes(str(item))}\","
        print(line.rstrip(","))


def transform_flat(incidents, options):
    flat = [["Incident", "Created", "Description", "Ack", "Status", "Urgency", "Html_url"]]

    for i in incidents:
        flat.append([
            i.incident_number(),
            i.created_at(),
            i.description() if options.full else i.short_description(),
            i.acknowledged_by(),
            i.status(),
            i.urgency(),
            i.html_url()
        ])

    return flat


def transform_grouped(incidents, options):
    flat = transform_flat(incidents, options)

    column_names = flat[0]

    if options.group not in column_names:
        raise RuntimeError(f"Unable to find column: {options.group}")

    # Case-insensitive match
    grouper_index = [col.lower() for col in column_names].index(options.group.lower())

    groups = {}

    for i in flat[1:]:
        key = i[grouper_index]

        if key in groups:
            groups[key] = groups[key] + 1
        else:
            groups[key] = 1

    grouped_flat = [[options.group.title(), "Count"]]

    for group, count in sorted(groups.items(), key=lambda item: item[1], reverse=True):
        grouped_flat.append([
            group,
            count
        ])

    return grouped_flat


def fetch_incidents(pg, options) -> []:
    """Fetch PagerDuty incidents, log_entries, notes"""

    # Incidents with log entries and notes
    full_incidents = []

    incidents = pg.fetch_incidents(options.start, options.end)
    info(f"Incidents found: {len(incidents)}")

    for i in incidents:
        log_entries = pg.fetch_incident_log(i['id'])
        notes = pg.fetch_incident_notes(i['id'])
        info(f"{len(log_entries):2} log_entries | {len(notes):2} notes for incident: {i['incident_number']}")
        full_incidents.append(Incident(i, log_entries, notes))

    return full_incidents


if __name__ == "__main__":
    main()
