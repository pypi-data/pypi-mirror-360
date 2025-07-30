import os
from .app_config import AppConfig, AppConfigError
from .secrets import SecretRetriever, SecretNotFound
from .dependencies import bake_deployment_image


def deploy_validations(app_config: AppConfig, cache_dir: str, logger):

    # First check if the secrets for the app exist.
    app_secrets = app_config.get("secrets", [])
    secret_retriever = SecretRetriever()
    for secret in app_secrets:
        try:
            secret_retriever.get_secret_as_dict(secret)
        except SecretNotFound:
            raise AppConfigError(f"Secret not found: {secret}")

    # TODO: Next check if the compute pool exists.


def run_validations(app_config: AppConfig):
    pass
