from typing import Any


def _clean_text(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip()[:1000]


def transform_records(records: list[dict[str, Any]], target: int = 125) -> list[dict[str, Any]]:
    seen: set[int] = set()
    transformed: list[dict[str, Any]] = []

    for item in records:
        repo_id = item.get("id")
        if not repo_id or repo_id in seen:
            continue
        seen.add(repo_id)
        owner = item.get("owner") or {}
        transformed.append(
            {
                "github_id": repo_id,
                "name": item.get("name"),
                "full_name": item.get("full_name"),
                "owner_login": owner.get("login"),
                "html_url": item.get("html_url"),
                "description": _clean_text(item.get("description")),
                "language": item.get("language") or item.get("searched_language"),
                "stars": item.get("stargazers_count", 0) or 0,
                "forks": item.get("forks_count", 0) or 0,
                "open_issues": item.get("open_issues_count", 0) or 0,
                "watchers": item.get("watchers_count", 0) or 0,
                "default_branch": item.get("default_branch"),
                "is_archived": bool(item.get("archived", False)),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "pushed_at": item.get("pushed_at"),
            }
        )
        if len(transformed) >= target:
            break

    return transformed
