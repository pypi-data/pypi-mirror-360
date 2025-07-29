"""Keyring utilities for secure storage and retrieval of secrets.

This module provides utility functions for working with keyring,
including getting and creating secrets and fernets.
These utilities help with secure storage and retrieval of secrets.
"""

import keyring
from cryptography.fernet import Fernet


def get_or_create_secret(service_name: str, username: str) -> str:
    """Get the app secret using keyring.

    If it does not exist, create it with a Fernet.
    """
    secret = keyring.get_password(service_name, username)
    if secret is None:
        secret = Fernet.generate_key().decode()
        keyring.set_password(service_name, username, secret)
    return secret


def get_or_create_fernet(service_name: str, username: str) -> Fernet:
    """Get the app fernet using keyring.

    If it does not exist, create it with a Fernet.
    """
    secret = get_or_create_secret(service_name, username)
    return Fernet(secret.encode())
