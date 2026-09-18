from .models import AuditLog

def log_event(action, object_type=None, object_id=None, message="", metadata=None, user=None):
    AuditLog.objects.create(
        action=action,
        object_type=object_type,
        object_id=object_id,
        message=message,
        metadata=metadata,
        user=user
    )
