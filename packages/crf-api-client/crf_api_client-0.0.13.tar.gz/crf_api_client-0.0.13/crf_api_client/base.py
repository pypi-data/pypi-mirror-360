from typing import Dict, List

import requests


class BaseAPIClient:
    """Base class containing common API functionality"""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers with authorization and content type"""
        return {"Authorization": f"Token {self.token}", "Content-Type": "application/json"}

    def _get_headers_without_content_type(self) -> Dict[str, str]:
        """Get headers without content type (for file uploads)"""
        return {"Authorization": f"Token {self.token}"}

    def _get_paginated_data(self, url: str, params: dict = {}) -> List[dict]:
        """Get all paginated data from an endpoint"""
        next_url = url
        data = []
        use_https = url.startswith("https://")
        is_first_call = True

        while next_url:
            # Ensure HTTPS consistency if base URL uses HTTPS
            if use_https and next_url.startswith("http://"):
                next_url = next_url.replace("http://", "https://")
            if is_first_call:
                response = requests.get(next_url, headers=self._get_headers(), params=params)
                is_first_call = False
            else:
                response = requests.get(next_url, headers=self._get_headers())
            response.raise_for_status()
            response_data = response.json()
            data.extend(response_data["results"])
            next_url = response_data.get("next")

        return data
