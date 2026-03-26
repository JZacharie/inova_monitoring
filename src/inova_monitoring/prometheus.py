import json
import time
import httpx
from typing import List, Dict, Any
from prometheus_client.parser import text_string_to_metric_families
from .config import settings


class PrometheusMetricsFetcher:
    def __init__(self):
        self.endpoints = self._parse_endpoints()
        self.cache = {}
        self.cache_ttl = settings.metrics_refresh_interval

    def _parse_endpoints(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(settings.prometheus_endpoints)
        except (json.JSONDecodeError, TypeError):
            return []

    async def fetch_metrics(self) -> Dict[str, Any]:
        self.endpoints = self._parse_endpoints()
        self.cache_ttl = settings.metrics_refresh_interval
        results = {}
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint in self.endpoints:
                name = endpoint.get("name", endpoint.get("url"))

                # Check cache
                cached_data = self.cache.get(name)
                if cached_data and (
                    time.time() - cached_data["timestamp"] < self.cache_ttl
                ):
                    results[name] = cached_data["data"]
                    continue

                url = endpoint.get("url")
                auth_type = endpoint.get("auth_type")

                headers = {}
                auth = None

                if auth_type == "basic":
                    auth = (endpoint.get("user"), endpoint.get("pass"))
                elif auth_type == "bearer":
                    headers["Authorization"] = f"Bearer {endpoint.get('token')}"

                try:
                    response = await client.get(url, headers=headers, auth=auth)
                    response.raise_for_status()

                    metrics = self._parse_prometheus_text(response.text)

                    # Update cache
                    self.cache[name] = {
                        "timestamp": time.time(),
                        "data": {"status": "online", "metrics": metrics},
                    }
                    results[name] = self.cache[name]["data"]
                except Exception as e:
                    results[name] = {
                        "status": "offline",
                        "error": str(e),
                        "metrics": [],
                    }
        return results

    def _parse_prometheus_text(self, text: str) -> List[Dict[str, Any]]:
        metrics = []
        try:
            for family in text_string_to_metric_families(text):
                family_data = {
                    "name": family.name,
                    "help": family.documentation,
                    "type": family.type,
                    "samples": [],
                }
                for sample in family.samples:
                    family_data["samples"].append(
                        {
                            "name": sample.name,
                            "labels": sample.labels,
                            "value": sample.value,
                            "timestamp": sample.timestamp,
                        }
                    )
                metrics.append(family_data)
        except Exception:
            # If parsing fails, return empty
            pass
        return metrics


# Singleton instance
metrics_fetcher = PrometheusMetricsFetcher()
