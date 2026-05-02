from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Optional

from app.models.task import TaskStatus


class PriorityAdvisor:
    """Suggests task status using local heuristics and optional OpenAI fallback."""

    def __init__(self, timeout_seconds: int = 3) -> None:
        self._timeout = timeout_seconds
        self._api_key = os.getenv("OPENAI_API_KEY")

    def suggest_priority(self, title: str, description: Optional[str]) -> TaskStatus:
        text = f"{title} {description or ''}".strip()
        if not text:
            return TaskStatus.PENDING

        if self._api_key:
            llm_status = self._suggest_with_llm(title, description)
            if llm_status is not None:
                return llm_status

        return self._suggest_local(text)

    def _suggest_local(self, text: str) -> TaskStatus:
        normalized = text.lower()
        if re.search(r"\b(done|completed|finished)\b", normalized):
            return TaskStatus.COMPLETED
        if re.search(
            r"\b(urgent|asap|critical|blocker|fix|bug|immediate|high priority|important)\b",
            normalized,
        ):
            return TaskStatus.IN_PROGRESS
        return TaskStatus.PENDING

    def _suggest_with_llm(
        self, title: str, description: Optional[str]
    ) -> Optional[TaskStatus]:
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helper that maps task title and description to one of "
                        "these statuses: pending, in_progress, completed."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Analyze the task below and return only one word: pending, "
                        "in_progress, or completed.\n\n"
                        f"Title: {title}\n"
                        f"Description: {description or ''}"
                    ),
                },
            ],
            "max_tokens": 10,
            "temperature": 0.0,
        }

        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError):
            return None

        return self._parse_status(body)

    def _parse_status(self, response_body: dict) -> Optional[TaskStatus]:
        choices = response_body.get("choices")
        if not choices or not isinstance(choices, list):
            return None

        message = choices[0].get("message", {})
        content = message.get("content", "")
        if not isinstance(content, str):
            return None

        normalized = content.strip().lower()
        if "completed" in normalized or "done" in normalized or "finished" in normalized:
            return TaskStatus.COMPLETED
        if "in_progress" in normalized or "in progress" in normalized or "ongoing" in normalized:
            return TaskStatus.IN_PROGRESS
        if "pending" in normalized or "todo" in normalized or "backlog" in normalized:
            return TaskStatus.PENDING
        return None