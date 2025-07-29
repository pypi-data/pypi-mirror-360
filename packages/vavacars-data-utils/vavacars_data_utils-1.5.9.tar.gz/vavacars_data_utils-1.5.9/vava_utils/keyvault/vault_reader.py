from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret_from_key_vault(key_vault, secret):
    """
    Retrieve a secret value from Azure Key Vault.
    """
    key_vault_uri = f"https://{key_vault}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_uri, credential=credential)
    return client.get_secret(secret).value