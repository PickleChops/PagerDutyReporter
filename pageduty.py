from datetime import datetime

import requests
import json


class Pagerduty:
    TZ = "UTC"
    BASE_URL = "https://api.pagerduty.com"
    PAGE_LIMIT = 25

    def __init__(self, api_key, team_id, service_id):
        self.team_id = team_id
        self.service_id = service_id

        self.headers = {
            "Authorization": f"Token token={api_key}",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Content-Type": "application/json",
        }

    def _get(self, url_path, params=None):
        default_get_params = {
            "total": "false",
            "time_zone": self.TZ,
            "limit": self.PAGE_LIMIT
        }

        params = {**default_get_params, **params}

        return requests.get(f"{self.BASE_URL}{url_path}", params, headers=self.headers)

    def fetch_incident_notes(self, incident_ref) -> []:

        notes = []
        try:
            j = self._process_json_response(
                self._get(f"/incidents/{incident_ref}/notes", {}))
        except Exception:
            raise

        notes += j['notes']

        return notes

    def fetch_incident_log(self, incident_ref) -> []:

        log = []
        offset = 0

        while True:
            try:
                j = self._process_json_response(
                    self._get(f"/incidents/{incident_ref}/log_entries",
                              {
                                  "offset": offset,
                                  "is_overview": "false",
                              }))
            except Exception:
                raise

            log += j['log_entries']

            if j['more']:
                offset += self.PAGE_LIMIT
            else:
                break

        return log

    def fetch_incidents(self, start_date: datetime, end_date: datetime) -> []:

        date_format = '%Y-%m-%d'

        incidents = []
        offset = 0

        while True:
            try:
                j = self._process_json_response(
                    self._get("/incidents",
                              {
                                  "service_ids[]": self.service_id,
                                  "team_ids[]": self.team_id,
                                  "offset": offset,
                                  "sort_by": "incident_number",
                                  "since": start_date.strftime(date_format),
                                  "until": end_date.strftime(date_format)
                              }))
            except Exception:
                raise

            incidents += j['incidents']

            if j['more']:
                offset += self.PAGE_LIMIT
            else:
                break

        return incidents

    @staticmethod
    def _process_json_response(response):
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                raise json.JSONDecodeError
        else:
            raise RuntimeError(f"Non 200 response code: {response.status_code}")
