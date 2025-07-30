import os
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

class BigQueryHelper(bigquery.Client):
    
    def __init__(self, project_name: str, credentials_file: str):
        """
        BigQueryHelper constructor. Actually it just a subclass of bigquery.Client 
            to automatically Auth from credentials json file and get query results
            to pandas DataFrame.

        Parameters:
            project_name (str): Google Cloud Project name
            credentials_file (str): Service Account credentials json file (client_secret.json)
        """
        if not os.path.exists(credentials_file):
            raise FileNotFoundError(f'File {credentials_file} not found')
        credentials = service_account.Credentials.from_service_account_file(credentials_file)
        super(BigQueryHelper, self).__init__(project=project_name, credentials=credentials)
        
    def query_to_df(self, query: str) -> pd.DataFrame:
        """
        Run query to BigQuery and return DataFrame

        Parameters:
            query (str): query in SQL-like for BigQuery
        """
        return self.query(query).to_dataframe()