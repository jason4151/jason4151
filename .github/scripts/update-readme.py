#!/usr/bin/env python3
"""Fill templates/README.md.tpl from public GitHub APIs (no PAT required)."""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER = "jason4151"
META_REPO = f"{USER}/{USER}"
ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "templates" / "README.md.tpl"
OUTPUT = ROOT / "README.md"
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def humanize(iso: str) -> str:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    days = (datetime.now(timezone.utc) - dt).days
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 7:
        return f"{days} days ago"
    weeks = days // 7
    if days < 30:
        return "1 week ago" if weeks == 1 else f"{weeks} weeks ago"
    months = days // 30
    if days < 365:
        return "1 month ago" if months == 1 else f"{months} months ago"
    years = days // 365
    return "1 year ago" if years == 1 else f"{years} years ago"


def gh_get(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{USER}-readme",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def bullet(name: str, url: str, description: str, when: str) -> str:
    desc = (description or "").strip()
    if desc:
        return f"- [{name}]({url}) - {desc} ({when})"
    return f"- [{name}]({url}) ({when})"


def working_on(limit: int = 5) -> str:
    repos = gh_get(
        f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=20&type=owner"
    )
    lines = []
    for repo in repos:
        if repo.get("fork") or repo.get("full_name") == META_REPO:
            continue
        lines.append(
            bullet(
                repo["full_name"],
                repo["html_url"],
                repo.get("description") or "",
                humanize(repo["pushed_at"]),
            )
        )
        if len(lines) == limit:
            break
    return "\n".join(lines) if lines else "- No recent public repositories."


def recent_stars(limit: int = 5) -> str:
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/starred?sort=created&per_page={limit}",
        headers={
            "Accept": "application/vnd.github.star+json",
            "User-Agent": f"{USER}-readme",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req) as resp:
        items = json.load(resp)
    lines = []
    for item in items:
        repo = item.get("repo", item)
        starred = item.get("starred_at") or repo.get("created_at")
        lines.append(
            bullet(
                repo["full_name"],
                repo["html_url"],
                repo.get("description") or "",
                humanize(starred),
            )
        )
    return "\n".join(lines) if lines else "- No recent stars."


def main() -> None:
    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace("{{WORKING_ON}}", working_on())
    text = text.replace("{{STARS}}", recent_stars())
    if "{{" in text:
        raise SystemExit("unexpanded template placeholders remain")
    OUTPUT.write_text(text.rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
