import os
from dotenv import load_dotenv

# External providers
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import hvac  # HashiCorp Vault

load_dotenv()

# Configure once for reuse
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AZURE_KEY_VAULT_URL = os.getenv("AZURE_KEY_VAULT_URL")
VAULT_URL = os.getenv("VAULT_URL")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")

def get_secret(key: str, default=None, required=False, source=None):
    """
    Load secrets from multiple backends in the following priority:
    1. source="env" -> .env file / os.environ
    2. source="vault" -> HashiCorp Vault
    3. source="aws" -> AWS Secrets Manager
    4. source="azure" -> Azure Key Vault
    If source is None, fallback to env first, then try all.
    """

    # ✅ .env or system environment
    if source in (None, "env"):
        value = os.getenv(key)
        if value:
            return value

    # ✅ HashiCorp Vault
    if source in (None, "vault"):
        try:
            client = hvac.Client(url=VAULT_URL, token=VAULT_TOKEN)
            if client.is_authenticated():
                vault_response = client.secrets.kv.v2.read_secret_version(path=key)
                return vault_response["data"]["data"].get("value")
        except Exception as e:
            if source == "vault":
                raise RuntimeError(f"Vault error for key '{key}': {e}")

    # ✅ AWS Secrets Manager
    if source in (None, "aws"):
        try:
            client = boto3.client("secretsmanager", region_name=AWS_REGION)
            response = client.get_secret_value(SecretId=key)
            return response.get("SecretString")
        except (BotoCoreError, ClientError) as e:
            if source == "aws":
                raise RuntimeError(f"AWS Secrets Manager error for key '{key}': {e}")

    # ✅ Azure Key Vault
    if source in (None, "azure"):
        try:
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=AZURE_KEY_VAULT_URL, credential=credential)
            secret = client.get_secret(key)
            return secret.value
        except Exception as e:
            if source == "azure":
                raise RuntimeError(f"Azure Key Vault error for key '{key}': {e}")

    if required:
        raise ValueError(f"Missing required secret: {key}")

    return default

def get_smtp_config(source=None):
    """
    Load SMTP config from selected source. Can be env, vault, aws, or azure.
    """
    return {
        "host": get_secret("SMTP_HOST", required=True, source=source),
        "port": int(get_secret("SMTP_PORT", default=587, source=source)),
        "username": get_secret("SMTP_USERNAME", required=True, source=source),
        "password": get_secret("SMTP_PASSWORD", required=True, source=source),
        "use_tls": get_secret("SMTP_USE_TLS", "true", source=source).lower() == "true",
        "rate_limit": int(get_secret("SMTP_RATE_LIMIT", 20, source=source))
    }
