import json
import pytest
from unittest.mock import MagicMock, Mock

from app.models.task import TaskStatus
from app.services.priority_advisor import PriorityAdvisor


@pytest.fixture
def advisor():
    """Provide a PriorityAdvisor instance."""
    return PriorityAdvisor(timeout_seconds=1)


def test_suggest_local_pending(advisor):
    """Test local suggestion for PENDING status."""
    status = advisor._suggest_local("Buy groceries")
    assert status == TaskStatus.PENDING


def test_suggest_local_in_progress(advisor):
    """Test local suggestion for IN_PROGRESS status with urgent keywords."""
    status = advisor._suggest_local("Fix critical bug ASAP")
    assert status == TaskStatus.IN_PROGRESS


def test_suggest_local_completed(advisor):
    """Test local suggestion for COMPLETED status."""
    status = advisor._suggest_local("Task is done and completed")
    assert status == TaskStatus.COMPLETED


def test_suggest_priority_empty_text(advisor):
    """Test suggestion for empty text defaults to PENDING."""
    status = advisor.suggest_priority("", None)
    assert status == TaskStatus.PENDING


def test_suggest_priority_without_api_key(advisor, monkeypatch):
    """Test suggestion without API key uses local heuristics."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    status = advisor.suggest_priority("Urgent fix", "Critical issue")
    assert status == TaskStatus.IN_PROGRESS


def test_suggest_priority_with_api_key_success(advisor, monkeypatch):
    """Test suggestion with API key and successful LLM response."""
    monkeypatch.setenv("OPENAI_API_KEY", "fake_key")

    mock_response = Mock()
    mock_response.read.return_value = json.dumps({
        "choices": [{"message": {"content": "in_progress"}}]
    }).encode("utf-8")

    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_response
    mock_context.__exit__.return_value = None

    monkeypatch.setattr("urllib.request.urlopen", Mock(return_value=mock_context))

    status = advisor.suggest_priority("Test task", "Some description")
    assert status == TaskStatus.IN_PROGRESS


def test_suggest_priority_with_api_key_failure_fallback(advisor, monkeypatch):
    """Test suggestion with API key but failure falls back to local."""
    monkeypatch.setenv("OPENAI_API_KEY", "fake_key")

    monkeypatch.setattr("urllib.request.urlopen", Mock(side_effect=Exception("Network error")))

    status = advisor.suggest_priority("Completed task", "All done")
    assert status == TaskStatus.COMPLETED  # Local heuristic


def test_parse_status_completed(advisor):
    """Test parsing LLM response for COMPLETED."""
    body = {"choices": [{"message": {"content": "completed"}}]}
    status = advisor._parse_status(body)
    assert status == TaskStatus.COMPLETED


def test_parse_status_in_progress(advisor):
    """Test parsing LLM response for IN_PROGRESS."""
    body = {"choices": [{"message": {"content": "in progress"}}]}
    status = advisor._parse_status(body)
    assert status == TaskStatus.IN_PROGRESS


def test_parse_status_pending(advisor):
    """Test parsing LLM response for PENDING."""
    body = {"choices": [{"message": {"content": "pending"}}]}
    status = advisor._parse_status(body)
    assert status == TaskStatus.PENDING


def test_parse_status_invalid(advisor):
    """Test parsing invalid LLM response returns None."""
    body = {"choices": []}
    status = advisor._parse_status(body)
    assert status is None

    body = {"choices": [{"message": {"content": 123}}]}
    status = advisor._parse_status(body)
    assert status is None
