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

    def _get_from_data(self, key):
        if key in self.data:
            return self.data[key]
        else:
            return "-"

    def _get_from_data_nested_1(self, parent, child):
        if parent in self.data:
            if child in self.data[parent]:
                return self.data[parent][child]
        else:
            return "-"

    def incident_number(self):
        return self._get_from_data('incident_number')

    def created_at(self):
        return self._get_from_data('created_at')

    def description(self):
        return self._get_from_data('description').rstrip()

    def short_description(self):
        d = self.description()
        if len(d) > self.SHORTER_DESCRIPTION_LENGTH:
            return f"{d[:self.SHORTER_DESCRIPTION_LENGTH]}..."
        else:
            return d

    def status(self):
        return self._get_from_data('status')

    def html_url(self):
        return self._get_from_data('html_url')

    def urgency(self):
        return self._get_from_data('urgency')

    def escalation(self):
        return self._get_from_data_nested_1('escalation_policy', 'summary')
