import json
import base64

import requests


class Confluence:
    BASE_URL = "https://algolia.atlassian.net"

    def __init__(self, user_email, api_token):

        encoded_creds = base64.b64encode(f"{user_email}:{api_token}".encode('utf-8'))

        self.default_headers = {
            "Authorization": f"Basic {encoded_creds.decode()}",
            "Content-Type": "application/json"
        }

    def _post(self, url_path, json_data=None, headers=None):
        json_data = {} if json_data is None else json_data

        headers = {} if headers is None else headers
        headers = {**self.default_headers, **headers}

        return requests.post(f"{self.BASE_URL}{url_path}", json=json_data, headers=headers)

    def create_page(self, space_key, title, body) -> []:
        try:
            return self._process_json_response(
                self._post("/wiki/rest/api/content/",
                           json_data={
                               "type": "page",
                               "title": title,
                               "space": {
                                   "key": space_key
                               },
                               "body": {
                                   "storage":
                                       {
                                           "value": body,
                                           "representation": "wiki"}}
                           }))
        except Exception:
            raise

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
