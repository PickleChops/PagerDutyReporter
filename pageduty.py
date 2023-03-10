import json
from datetime import datetime

import requests


class Pagerduty:
    TZ = "UTC"
    BASE_URL = "https://api.pagerduty.com"
    PAGE_LIMIT = 25
    SHORT_DATE_FORMAT = '%Y-%m-%d'
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

    def __init__(self, api_key, team_ids, service_ids):
        self.team_ids = team_ids
        self.service_ids = service_ids

        self.default_headers = {
            "Authorization": f"Token token={api_key}",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Content-Type": "application/json",
        }

        self.default_get_params = {
            "time_zone": self.TZ,
            "limit": self.PAGE_LIMIT
        }

    def _get(self, url_path, params=None, headers=None):

        params = {} if params is None else params
        params = {**self.default_get_params, **params}

        headers = {} if headers is None else headers
        headers = {**self.default_headers, **headers}

        return requests.get(f"{self.BASE_URL}{url_path}", params=params, headers=headers)

    def _post(self, url_path, json_data=None, headers=None):

        json_data = {} if json_data is None else json_data

        headers = {} if headers is None else headers
        headers = {**self.default_headers, **headers}

        return requests.post(f"{self.BASE_URL}{url_path}", json=json_data, headers=headers)

    def fetch_incident_notes(self, incident_ref) -> []:

        notes = []
        try:
            j = self._process_json_response(
                self._get(f"/incidents/{incident_ref}/notes", {"total": "false"}))
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
                                  "total": "false",
                              }))
            except Exception:
                raise

            log += j['log_entries']

            if j['more']:
                offset += self.PAGE_LIMIT
            else:
                break

        return log

    def fetch_raw_incidents(self, start_date: datetime, end_date: datetime) -> []:

        incidents = []
        offset = None

        while True:
            try:
                j = self._process_json_response(
                    self._post("/analytics/raw/incidents",
                               json_data={
                                   "filters": {
                                       "created_at_start": start_date.strftime(self.DATE_FORMAT),
                                       "created_at_end": end_date.strftime(self.DATE_FORMAT),
                                       "service_ids": self.service_ids,
                                       "team_ids": self.team_ids,
                                   },
                                   "limit": self.PAGE_LIMIT,
                                   "order": "asc",
                                   "time_zone": self.TZ,
                                   "order_by": "created_at",
                                   "starting_after": offset
                               },
                               headers={
                                   "X-EARLY-ACCESS": "analytics-v2"
                               }))
            except Exception:
                raise

            incidents += j['data']

            if j['more']:
                offset = j['last']
            else:
                break

        return incidents

    def fetch_incidents(self, start_date: datetime, end_date: datetime) -> []:

        incidents = []
        offset = 0

        while True:
            try:
                j = self._process_json_response(
                    self._get("/incidents",
                              {
                                  # TODO these arrays probably need flattening, but this method not current used so...
                                  "service_ids[]": self.service_ids,
                                  "team_ids[]": self.team_ids,
                                  "offset": offset,
                                  "total": "false",
                                  "sort_by": "incident_number",
                                  "since": start_date.strftime(self.SHORT_DATE_FORMAT),
                                  "until": end_date.strftime(self.SHORT_DATE_FORMAT)
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

            if response.content:
                response_error_details = response.content.decode('utf-8')
            else:
                response_error_details = ""

            raise RuntimeError(f"Non 200 response code: {response.status_code} {response_error_details}")
