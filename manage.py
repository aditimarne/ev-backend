#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
        from django.core.management import execute_from_command_line
except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

if __name__ == "__main__":
    try:
        from open_react import open_react
        open_react()
    except Exception as e:
        print("Could not open React automatically:", e)
    execute_from_command_line(sys.argv)

execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
