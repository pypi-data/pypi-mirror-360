import requests
import os
import json
import time
import tkinter as tk
from tkinter import simpledialog
from typing import Optional, Dict, Any, List

class Client:
    """
    Client for interacting with the Tilantra Model Swap Router API.
    Usage:
        guidera_client = Client(auth_token)
        response = guidera_client.generate(prompt, prefs, cp_tradeoff_parameter)
        suggestions = guidera_client.get_suggestions(prompt)
    """
    def __init__(self, auth_token: str, api_base_url: str = "http://localhost:8000"):
        """
        Initialize the client with an authentication token and API base URL.
        """
        self.auth_token = auth_token
        self.api_base_url = api_base_url.rstrip("/")

    def _jwt_file_path(self):
    return os.path.expanduser("~/.guidera_jwt.json")

    def _load_jwt(self):
        try:
            with open(self._jwt_file_path(), "r") as f:
                data = json.load(f)
                # Check expiry
                if data.get("exp", 0) > time.time():
                    return data["token"]
        except Exception:
            pass
        return None

    def _save_jwt(self, token, exp):
        with open(self._jwt_file_path(), "w") as f:
            json.dump({"token": token, "exp": exp}, f)

    def _login_dialog(self):
        root = tk.Tk()
        root.withdraw()
        email = simpledialog.askstring("Login", "Enter your email:")
        password = simpledialog.askstring("Login", "Enter your password:", show='*')
        root.destroy()
        return email, password

    def login(self):
        email, password = self._login_dialog()
        url = f"{self.api_base_url}/login"
        payload = {"email": email, "password": password}
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        token = data["token"]
        exp = data.get("exp", int(time.time()) + 2 * 3600)  # fallback: 2 hours from now
        self._save_jwt(token, exp)
        self.auth_token = token

    @staticmethod
    def register_user(username: str, email: str, password: str, full_name: Optional[str] = None, company: Optional[str] = None, api_base_url: str = "http://localhost:8000") -> Dict[str, Any]:
        """
        Register a new user. Returns the API response.
        """
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
            return {"error": str(e), "response": getattr(e, 'response', None)}

    @staticmethod
    def generate_token(username: str, email: str, force_new: bool = False, api_base_url: str = "http://localhost:8000") -> Dict[str, Any]:
        """
        Generate or retrieve a JWT token for a user. Returns the API response.
        """
        url = f"{api_base_url.rstrip('/')}/generate_token"
        payload = {
            "username": username,
            "email": email,
            "force_new": force_new
        }
        try:
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "response": getattr(e, 'response', None)}

    def generate(self, prompt: str, prefs: Optional[Dict[str, Any]] = None, cp_tradeoff_parameter: float = 0.7, compliance_enabled: bool = False) -> Dict[str, Any]:
        """
        Generate a response from the model router.
        Args:
            prompt (str): The prompt to send to the model.
            prefs (dict, optional): User preferences for the model.
            cp_tradeoff_parameter (float, optional): Tradeoff parameter for cost/performance. Defaults to 0.7.
            compliance_enabled (bool, optional): Whether to enable compliance checks. Defaults to False.
        Returns:
            dict: The API response, including possible error, issues, compliance_report, and user fields.
        """
        if not self.auth_token:
            self.auth_token = self._load_jwt()
            if not self.auth_token:
                self.login()
        url = f"{self.api_base_url}/generate"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {
            "prompt": prompt,
            "prefs": prefs or {},
            "cp_tradeoff_parameter": cp_tradeoff_parameter,
            "compliance_enabled": compliance_enabled
        }
        try:
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "response": getattr(e, 'response', None)}

    def get_suggestions(self, prompt: str) -> Dict[str, Any]:
        """
        Get prompt suggestions from the model router.
        """
        if not self.auth_token:
            self.auth_token = self._load_jwt()
            if not self.auth_token:
                self.login()
        url = f"{self.api_base_url}/suggestion"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        payload = {"prompt": prompt}
        try:
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "response": getattr(e, 'response', None)} 