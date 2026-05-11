"""Compatibility import for the missing-person pipeline."""

from app.pipelines.missing_person_pipeline import AuditEvent, EntityCard, MissingPersonPipeline

__all__ = ["AuditEvent", "EntityCard", "MissingPersonPipeline"]
