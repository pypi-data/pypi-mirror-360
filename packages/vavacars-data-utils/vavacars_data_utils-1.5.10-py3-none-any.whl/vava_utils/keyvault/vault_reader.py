from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
import os

def get_secret_from_key_vault(key_vault, secret):
    """
    Retrieve a secret value from Azure Key Vault.
    """
    key_vault_uri = f"https://{key_vault}.vault.azure.net"
    client_id = os.getenv("MANAGED_IDENTITY_CLIENT_ID")
    if client_id is not None:
        credential = ManagedIdentityCredential(client_id=client_id)
    else:
        credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_uri, credential=credential)
    return client.get_secret(secret).value