import requests
import os
import json
import time
import getpass
import datetime
from typing import Optional, Dict, Any
import jwt  # pyjwt


class Client:
    """
    Client for interacting with the Tilantra Model Swap Router API.
    Usage:
        guidera_client = Client()
        response = guidera_client.generate(prompt, prefs, cp_tradeoff_parameter)
        suggestions = guidera_client.get_suggestions(prompt)
    """

    def __init__(
        self,
        auth_token: Optional[str] = None,
        api_base_url: str = "http://localhost:8000",
    ):
        self.auth_token = auth_token or self._load_jwt()
        self.api_base_url = api_base_url.rstrip("/")

    def _jwt_file_path(self):
        return os.path.expanduser("~/.guidera_jwt.json")

    def _load_jwt(self):
        try:
            with open(self._jwt_file_path(), "r") as f:
                data = json.load(f)
                token = data.get("token")
                if not token:
                    return None
                # Decode the JWT without verifying signature (for expiry check only)
                try:
                    payload = jwt.decode(token, options={"verify_signature": False})
                    exp = payload.get("exp")
                    if exp and exp > time.time():
                        return token
                except Exception:
                    pass
        except Exception:
            pass
        return None

    def _save_jwt(self, token, exp):
        with open(self._jwt_file_path(), "w") as f:
            json.dump({"token": token, "exp": exp}, f)

    def _login_prompt(self):
        email = input("Enter your email: ")
        password = getpass.getpass("Enter your password: ")
        return email, password

    def login(self):
        email, password = self._login_prompt()
        url = f"{self.api_base_url}/users/login"
        payload = {"email": email, "password": password}
        try:
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            token = data["token"]
            exp = data.get("exp", int(time.time()) + 2 * 3600)
            self._save_jwt(token, exp)
            self.auth_token = token
        except requests.RequestException as e:
            print("Login failed:", e)
            raise

    @staticmethod
    def register_user(
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        company: Optional[str] = None,
        api_base_url: str = "http://localhost:8000",
    ) -> Dict[str, Any]:
        url = f"{api_base_url.rstrip('/')}/register"
        payload = {
            "username": username,
            "email": email,
            "password": password,
        }
        if full_name:
            payload["full_name"] = full_name
        if company:
            payload["company"] = company
        try:
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "response": getattr(e, "response", None)}

    def _ensure_auth(self):
        if not self.auth_token:
            self.auth_token = self._load_jwt()
            if not self.auth_token:
                self.login()

    def generate(
        self,
        prompt: str,
        prefs: Optional[Dict[str, Any]] = None,
        cp_tradeoff_parameter: float = 0.7,
        compliance_enabled: bool = False,
    ) -> Dict[str, Any]:
        self._ensure_auth()
        url = f"{self.api_base_url}/generate"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {
            "prompt": prompt,
            "prefs": prefs or {},
            "cp_tradeoff_parameter": cp_tradeoff_parameter,
            "compliance_enabled": compliance_enabled,
        }
        try:
            resp = requests.post(url, json=payload, headers=headers)
            if resp.status_code == 401:
                # Token invalid/expired, prompt for login and retry once
                self.login()
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "response": getattr(e, "response", None)}

    def get_suggestions(self, prompt: str) -> Dict[str, Any]:
        self._ensure_auth()
        url = f"{self.api_base_url}/suggestion"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {"prompt": prompt}
        try:
            resp = requests.post(url, json=payload, headers=headers)
            if resp.status_code == 401:
                # Token invalid/expired, prompt for login and retry once
                self.login()
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "response": getattr(e, "response", None)}