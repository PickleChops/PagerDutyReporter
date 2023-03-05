import requests
import json


class Incident:
    SHORTER_DESCRIPTION_LENGTH = 58

    def __init__(self, incident_data, log_entries, notes):
        self.data = incident_data
        self.log_entries = log_entries
        self.notes = notes

    def acknowledged_by(self):
        for l in self.log_entries:
            if l['type'] == 'acknowledge_log_entry':
                return l['agent']['summary']

        return '-'

    def _get(self, key):
        return self.data.get(key, "-")

    def incident_number(self):
        return self._get('incident_number')

    def created_at(self):
        return self._get('created_at')

    def description(self):
        return self._get('description').rstrip()

    def short_description(self):
        d = self.description()
        if len(d) > self.SHORTER_DESCRIPTION_LENGTH:
            return f"{d[:self.SHORTER_DESCRIPTION_LENGTH]}..."
        else:
            return d

    def status(self):
        return self._get('status')

    def html_url(self):
        return self._get('html_url')

    def urgency(self):
        return self._get('urgency')

    def resolution_time(self):
        return self._get('seconds_to_resolve')
