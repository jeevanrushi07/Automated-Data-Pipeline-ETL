import os
import time
from typing import Any

import requests

BASE_URL = "https://api.github.com/search/repositories"
LANGUAGES = ["Python", "Java", "JavaScript", "C++", "Go"]
PER_PAGE = 30


def search_repositories(language: str, token: str | None = None, limit: int = PER_PAGE) -> list[dict[str, Any]]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    results: list[dict[str, Any]] = []
    page = 1
    while len(results) < limit:
        params = {
            "q": f"language:{language}",
            "sort": "stars",
            "order": "desc",
            "per_page": min(100, limit - len(results)),
            "page": page,
        }
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=30)
        if response.status_code == 403:
            reset = response.headers.get("X-RateLimit-Reset")
            wait = max(int(reset) - int(time.time()), 1) if reset and reset.isdigit() else 60
            raise RuntimeError(f"GitHub API rate limit reached. Retry after about {wait} seconds.")
        response.raise_for_status()
        payload = response.json()
        items = payload.get("items", [])
        if not items:
            break
        results.extend(items)
        if len(items) < params["per_page"]:
            break
        page += 1

    return results[:limit]


def extract_repositories(token: str | None = None, per_language: int = PER_PAGE) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for language in LANGUAGES:
        for item in search_repositories(language, token=token, limit=per_language):
            item["searched_language"] = language
            records.append(item)
    return records
