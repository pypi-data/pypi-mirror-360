from .client import Client

def client(auth_token, api_base_url="http://localhost:8000"):
    """
    Returns a Client instance for interacting with the Tilantra Model Swap Router API.
    """
    return Client(auth_token, api_base_url) 