import requests
import pandas as pd
import logging

MAX_ATTEMPTS = 2


class SalesForceHelper:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        url: str = "https://vavacarsturkey.my.salesforce.com/services/data/v57.0",
    ):
        self.url = url
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self._access_token = None
        self._token_expired = None

    @property
    def access_token(self):
        if self._access_token is None or self._token_expired:
            self._access_token = self.get_access_token()
            self._token_expired = False
        return self._access_token

    def get_access_token(self):
        url = "https://login.salesforce.com/services/oauth2/token"
        payload = f"grant_type=password&client_id={self.client_id}&client_secret={self.client_secret}&username={self.username}&password={self.password}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()["access_token"]

    def query(self, query_str: str, as_frame: bool = True, attempt: int = 1):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        url = self.url + f"/query/?q={query_str}"
        response = requests.request("GET", url, headers=headers)

        if response.status_code == 200:
            if as_frame:
                return pd.DataFrame(response.json()["records"])
            else:
                return response.json()
        elif response.status_code in (401, 403) and attempt < MAX_ATTEMPTS:
            self._token_expired = True
            return self.query(query_str, as_frame=as_frame, attempt=attempt + 1)
        else:
            logging.error(response.text)
            response.raise_for_status()
