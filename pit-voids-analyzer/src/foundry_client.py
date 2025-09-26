import os
import requests
from typing import Dict, List

class FoundryClient:
    """
    Minimal wrapper around the Azure OpenAI Chat Completions REST endpoint.
    """

    def __init__(self, api_key: str, endpoint: str, *, system_prompt: str | None = None):
        self.api_key = api_key
        # remove a trailing slash if present
        self.endpoint = endpoint.rstrip("/")
        self.system_prompt = system_prompt or "You are an AI assistant that analyses Pit-Void data."

    # ------------------------------------------------------------------
    # Internal helper – send a correctly-formatted chat-completion call
    # ------------------------------------------------------------------
    def _call_api(self, user_prompt: str) -> Dict:
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            # o3-mini expects `max_completion_tokens` instead of `max_tokens`
            "max_completion_tokens": 1024,
        }
        response = requests.post(self.endpoint, headers=headers, json=payload, timeout=300)
        if response.status_code != 200:
            # Print full error payload to help diagnose 400s
            print("Azure OpenAI returned:", response.status_code, response.text)
            response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Public convenience wrapper
    # ------------------------------------------------------------------
    def get_response(self, user_prompt: str) -> str:
        result = self._call_api(user_prompt)
        try:
            return result["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            return "Received unexpected response format from Azure OpenAI."