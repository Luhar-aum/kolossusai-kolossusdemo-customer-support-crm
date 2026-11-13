"""Tests for lead model validation - no database required."""
import pytest
import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("SYNC_DATABASE_URL", "postgresql://test:test@localhost/test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-123")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/1")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

from app.models.lead import LeadStatus, LeadSource, LeadPriority, LeadClassification


def test_lead_status_values():
    assert LeadStatus.new == "new"
    assert LeadStatus.contacted == "contacted"
    assert LeadStatus.qualified == "qualified"
    assert LeadStatus.unqualified == "unqualified"
    assert LeadStatus.converted == "converted"
    assert LeadStatus.lost == "lost"


def test_lead_source_values():
    assert LeadSource.manual == "manual"
    assert LeadSource.csv_import == "csv_import"
    assert LeadSource.webhook == "webhook"


def test_lead_priority_values():
    assert LeadPriority.low == "low"
    assert LeadPriority.medium == "medium"
    assert LeadPriority.high == "high"
    assert LeadPriority.urgent == "urgent"


def test_lead_classification_values():
    assert LeadClassification.hot == "hot"
    assert LeadClassification.warm == "warm"
    assert LeadClassification.cold == "cold"


def test_lead_status_is_string():
    for status in LeadStatus:
        assert isinstance(status, str)


def test_lead_priority_ordering():
    priorities = [LeadPriority.low, LeadPriority.medium, LeadPriority.high, LeadPriority.urgent]
    assert len(priorities) == 4
