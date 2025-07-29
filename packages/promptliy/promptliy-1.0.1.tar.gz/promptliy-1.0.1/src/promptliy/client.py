import threading
import time
import requests
from typing import Dict, Union, List, Optional
from dataclasses import dataclass
import sys

try:
    import cachetools
    from cachetools import TTLCache
except ImportError:
    TTLCache = None


@dataclass
class Prompt:
    prompt: str
    variables: Union[str, List[str]]

    def format(self, values: Dict[str, str]) -> str:
        formatted = self.prompt

        required = (
            self.variables if isinstance(self.variables, list)
            else [v.strip() for v in self.variables.split(",") if v.strip()]
        )

        missing = [v for v in required if v not in values]
        if missing:
            raise ValueError(f"Missing required variables: {', '.join(missing)}")

        for key, val in values.items():
            formatted = formatted.replace(f"{{{{{key}}}}}", val)

        return formatted


class PromptliyClient:
    def __init__(
        self,
        project_key: str,
        base_url: str = "https://api.promptliy.ai",
        refresh_interval: int = 30
    ):
        self.project_key = project_key
        self.base_url = base_url.rstrip("/")
        self.refresh_interval = refresh_interval
        self.is_ready = False

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Determine environment
        self.is_node = hasattr(sys, 'ps1') is False and hasattr(sys, 'stdout')

        # Cache setup
        if self.is_node and TTLCache:
            self.prompt_cache = TTLCache(maxsize=1000, ttl=3600)
        else:
            self.prompt_cache = {}

        self._start_background_refresh()
        self.is_ready = True

    def _start_background_refresh(self):
        def _loop():
            while not self._stop_event.is_set():
                time.sleep(self.refresh_interval)
                keys = list(self.prompt_cache.keys())
                for key in keys:
                    try:
                        self._fetch_prompt_from_server(key, force_update=True)
                    except Exception:
                        pass

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def _fetch_prompt_from_server(self, prompt_key: str, force_update: bool = False) -> Prompt:
        if not force_update and prompt_key in self.prompt_cache:
            cached = self.prompt_cache[prompt_key]
            if not isinstance(self.prompt_cache, dict):  # TTLCache already handles expiry
                return cached

        url = f"{self.base_url}/api/v1/prompt/client/{self.project_key}/{prompt_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        prompt = Prompt(prompt=data['prompt'], variables=data['variables'])
        self.prompt_cache[prompt_key] = prompt
        return prompt

    def get_prompt(self, prompt_key: str) -> Prompt:
        return self._fetch_prompt_from_server(prompt_key)

    def format(self, prompt_key: str, values: Dict[str, str]) -> str:
        prompt = self.get_prompt(prompt_key)
        return prompt.format(values)

    def dispose(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        if hasattr(self.prompt_cache, 'clear'):
            self.prompt_cache.clear()
