from typing import Any

from .models import AuditEvent


def log_event(
    *,
    action: str,
    object_type: str,
    object_id: str,
    message: str = "",
    actor=None,
    metadata: dict[str, Any] | None = None,
) -> None:
    AuditEvent.objects.create(
        actor=actor,
        action=action,
        object_type=object_type,
        object_id=object_id,
        message=message,
        metadata=metadata or {},
    )
