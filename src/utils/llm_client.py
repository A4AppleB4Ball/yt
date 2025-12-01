"""
LLM Client for OpenAI-compatible API (localhost:8439)
Simple wrapper for chat completions with retry logic
"""

import json
import time
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path


class LLMClient:
    """Simple LLM client for OpenAI-compatible API."""

    def __init__(self, endpoint: str, model: Optional[str] = None, timeout: int = 300, max_retries: int = 3):
        self.endpoint = endpoint.rstrip('/') or "http://localhost:8439/v1"
        self.model = model or "claude-4.5"
        self.timeout = timeout
        self.max_retries = max_retries

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })

    def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        Send a chat completion request.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens to generate
            response_format: Optional response format (e.g., {"type": "json_object"})

        Returns:
            Response text from the model
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        if response_format:
            payload["response_format"] = response_format

        # Retry logic
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.post(
                    f"{self.endpoint}/chat/completions",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()

                result = response.json()
                return result['choices'][0]['message']['content']

            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    wait_time = 5 * attempt
                    print(f"    ⚠️  LLM timeout, retrying in {wait_time}s... (attempt {attempt}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"LLM request timed out after {self.max_retries} attempts")

            except requests.exceptions.HTTPError as e:
                if attempt < self.max_retries and 500 <= e.response.status_code < 600:
                    wait_time = 5 * attempt
                    print(f"    ⚠️  LLM server error, retrying in {wait_time}s... (attempt {attempt}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"LLM HTTP error: {e}")

            except Exception as e:
                raise Exception(f"LLM request failed: {e}")

        raise Exception("LLM request failed after all retries")

    def chat_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send a chat request and parse JSON response.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Parsed JSON response as dictionary
        """
        response = self.chat(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Try to extract JSON from response if wrapped in markdown
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
                return json.loads(json_str)
            raise Exception(f"Failed to parse JSON response: {e}")
