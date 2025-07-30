from typing import Dict, List, Optional

import os
import base64
from io import BytesIO
from azure.communication.email import EmailClient
import pandas as pd


def get_file_attachment(file_path):
    with open(file_path, "rb") as f:
        file_bytes = base64.b64encode(f.read())
    file_extension = os.path.splitext(file_path)[1][1:]
    file_name = os.path.basename(file_path)
    return {"name": file_name, "contentType": file_extension, "contentInBase64": file_bytes.decode()}


def get_dataframe_attachment(file_name, df):
    buffer = BytesIO()
    file_extension = os.path.splitext(file_name)[1][1:]
    if file_extension == "xlsx":
        df.to_excel(buffer, index=False)
    else:
        file_extension = "csv" # csv as default 
        df.to_csv(buffer, index=False)
    return {
        "name": file_name,
        "contentType": file_extension,
        "contentInBase64": base64.b64encode(buffer.getvalue()).decode(),
    }


class EmailHelper:
    def __init__(self, resource_name: str, access_key: str, sender_address: str):
        """
        Email helper constructor.

        Parameters:
            resource_name: name of Email Communication Resource in Azure
            access_key: in b64 for communication resource.
            sender_address: email address to use as sender.
        """
        self.client = EmailClient.from_connection_string(
            f"endpoint=https://{resource_name}.communication.azure.com/;accessKey={access_key}"
        )
        self.sender_address = sender_address

    def send_email(
        self,
        subject: str,
        content_text: Optional[str] = None,
        content_html: Optional[str] = None,
        to: Optional[List[str]] = [],
        cc: Optional[List[str]] = [],
        bcc: Optional[List[str]] = [],
        files: Optional[List[str]] = [],
        dataframes: Optional[Dict[str, pd.DataFrame]] = {},
    ):
        """
        Send email using Azure Communication Email Service.

        Parameters:
            subject (str): email subject
            content_text (str): email content in plain text format
            content_html (str): email content in HTML format. Must pass either 'content_text' or 'content_html' as parameters.
            to (List[str]): list of emails for main recipients
            cc (List[str]): list of emails for carbon copy recipients
            bcc (List[str]): list of emails for blind carbon recipients
            files (List[str]): list of files to attach
            dataframes (Dict[str, pd.DataFrame]): Dataframes to attach as files. Filename as key and dataframe as value. 
                Admits both csv and Excel (xlsx) types, inferred from filename.
        """

        if len(to + bcc + cc) == 0:
            raise ValueError("Need to pass at least one recipient: to, cc, bcc")
        if not content_text and not content_html:
            raise ValueError("Need to pass at email body: content_text or content_html")

        message = {
            "content": {
                "subject": subject,
            },
            "recipients": {},
            "senderAddress": self.sender_address,
            "attachments": (
                [get_file_attachment(f) for f in files]
                + [get_dataframe_attachment(f, df) for f, df in dataframes.items()]
            ),
        }

        if content_text:
            message["content"]["plainText"] = content_text
        if content_html:
            message["content"]["html"] = content_html
        if to:
            message["recipients"]["to"] = [{"address": address} for address in to]
        if cc:
            message["recipients"]["cc"] = [{"address": address} for address in cc]
        if bcc:
            message["recipients"]["bcc"] = [{"address": address} for address in bcc]

        poller = self.client.begin_send(message)
        return poller.result()
