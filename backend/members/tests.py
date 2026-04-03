from django.db import IntegrityError
from django.test import TestCase
from .models import Member


class MemberModelTests(TestCase):
    def test_member_unique_membership(self) -> None:
        Member.objects.create(membership_no="1001", full_name="أحمد علي")
        with self.assertRaises(IntegrityError):
            Member.objects.create(membership_no="1001", full_name="محمد حسن")

    def test_member_str(self) -> None:
        member = Member.objects.create(membership_no="1002", full_name="مريم السيد")
        self.assertIn("1002", str(member))
