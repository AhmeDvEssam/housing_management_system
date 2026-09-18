from django.db import models

class DashboardPermissions(models.Model):
    """
    Dummy model to hold custom permissions for the dashboard.
    """
    class Meta:
        managed = False  # No table will be created in the DB
        permissions = [
            ("view_wallboard", "يمكنه عرض لوحة المتابعة"),
        ]
