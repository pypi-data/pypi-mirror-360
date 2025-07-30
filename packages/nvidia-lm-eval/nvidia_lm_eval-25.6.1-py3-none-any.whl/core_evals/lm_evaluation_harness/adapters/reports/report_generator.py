import html
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from ..caching.diskcaching import Cache
from .templates.simple_template import SIMPLE_TEMPLATE


class ReportGenerator:
    """Generates HTML reports of cached requests and responses."""

    def __init__(self, cache_dir: str, api_url: str):
        self.cache_dir = Path(cache_dir)
        self.api_url = api_url

        # Create cache directories if they don't exist
        responses_dir = self.cache_dir / "responses"
        requests_dir = self.cache_dir / "requests"
        headers_dir = self.cache_dir / "headers"

        # Initialize caches with directory paths
        self.responses_cache = Cache(directory=str(responses_dir))
        self.requests_cache = Cache(directory=str(requests_dir))
        self.headers_cache = Cache(directory=str(headers_dir))

        # Initialize Jinja2 environment
        self.env = Environment(
            undefined=StrictUndefined,
            autoescape=select_autoescape(["html", "xml"]),
        )
        self.env.filters["tojson_utf8"] = self._tojson_utf8
        self.template = self.env.from_string(SIMPLE_TEMPLATE)

    def _tojson_utf8(self, data: Any) -> str:
        """Format JSON data for HTML display with UTF-8 support."""
        return html.escape(json.dumps(data, indent=2, ensure_ascii=False))

    def _get_request_content(self, request_data: Any) -> Any:
        """Extract content from request data."""
        try:
            if isinstance(request_data, bytes):
                request_data = request_data.decode("utf-8")

            if isinstance(request_data, str):
                try:
                    parsed = json.loads(request_data)
                    return parsed  # Return the parsed dict
                except json.JSONDecodeError:
                    return request_data

            # If it's already a dict or other type, return as is
            return request_data
        except Exception as e:
            return request_data

    def _get_response_content(self, response_data: Any) -> Any:
        """Extract content from response data."""
        try:
            if isinstance(response_data, bytes):
                response_data = response_data.decode("utf-8")

            if isinstance(response_data, str):
                try:
                    parsed = json.loads(response_data)
                    return parsed  # Return the parsed dict
                except json.JSONDecodeError:
                    return response_data

            # If it's already a dict or other type, return as is
            return response_data
        except Exception as e:
            return str(response_data)

    def _determine_model_type(self, request_data: dict) -> str:
        """Determine if the request is for chat or completion."""
        if "messages" in request_data:
            return "chat"
        elif "prompt" in request_data:
            return "completion"
        return "unknown"

    def _collect_entries(self) -> list:
        """Collect all request-response entries from cache."""
        entries = []

        # Get all cache keys from both caches
        response_keys = [key for key in self.responses_cache.iterkeys()]
        request_keys = [key for key in self.requests_cache.iterkeys()]

        # Use request keys as primary since they should match response keys
        cache_keys = request_keys if request_keys else response_keys

        if not cache_keys:
            return []

        # Collect all cache entries
        for cache_key in cache_keys:
            try:
                # Get request data first
                request_content = None
                if cache_key in self.requests_cache:
                    request_data = self.requests_cache[cache_key]
                    request_content = self._get_request_content(request_data)
                else:
                    continue

                # Get response data
                response_content = None
                if cache_key in self.responses_cache:
                    response_data = self.responses_cache[cache_key]
                    response_content = self._get_response_content(response_data)

                # Add entry data
                entries.append(
                    {
                        "request_data": request_content,
                        "display_request": request_content,  # Already processed by _get_request_content
                        "response": response_content,
                        "endpoint": self.api_url,
                        "cache_key": cache_key,
                    }
                )
            except Exception as e:
                continue

        return entries

    def generate_report(self, output_path: str | None = None) -> str:
        """Generate HTML report of cached requests and responses."""
        entries = self._collect_entries()

        if not entries:
            return ""

        # Use the template to generate the report
        html_content = self.template.render(entries=entries)

        if output_path:
            # Save HTML
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Save JSON
            json_output_path = output_path.with_suffix(".json")
            with open(json_output_path, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)

            return str(output_path)

        return html_content
