#!/usr/bin/env python
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
except ImportError:
    pass

def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "housing.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "لا يمكن استيراد Django. تأكد من تثبيت المتطلبات ثم أعد المحاولة."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
