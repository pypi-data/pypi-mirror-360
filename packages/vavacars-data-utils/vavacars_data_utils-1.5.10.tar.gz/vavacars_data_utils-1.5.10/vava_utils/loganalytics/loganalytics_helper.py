import logging
import pandas as pd
from azure.identity import ClientSecretCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.core.exceptions import HttpResponseError
import datetime


class UnknownQueryStatusError(Exception):
    """Custom exception for unknown query status"""

    pass


class LogAnalyticsHelper:

    def __init__(
        self,
        service_principal_id: str,
        service_principal_password: str,
        tenant_id: str,
        workspace_id: str = "58ca4766-72b7-4610-8d1c-4b6a88a49a01",
    ):
        self.client = LogsQueryClient(
            ClientSecretCredential(tenant_id, service_principal_id, service_principal_password)
        )
        self.workspace_id = workspace_id

    def query(self, query: str, start: datetime.datetime = None, end: datetime.datetime = None, **kwargs):

        timespan = None if start is None or end is None else (start, end)
        response = self.client.query_workspace(workspace_id=self.workspace_id, query=query, timespan=timespan, **kwargs)

        if response.status == LogsQueryStatus.SUCCESS:
            data = response.tables
        elif response.status == LogsQueryStatus.PARTIAL:
            logging.warning(f"Partial query success. Error: {response.partial_error.message}")
            data = response.partial_data
        else:
            logging.error(f"Unknown query status: {response.status}")
            raise UnknownQueryStatusError(f"Received an unknown query status: {response.status}")

        dataframes = [pd.DataFrame(t.rows, columns=t.columns) for t in data]

        if len(dataframes) == 1:
            return dataframes[0]
        elif len(dataframes) > 1:
            return dataframes
        else:
            logging.warning("No data found in the query result")
            return None
