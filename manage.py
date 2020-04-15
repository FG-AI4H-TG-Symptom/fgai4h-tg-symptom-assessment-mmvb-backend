#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    project_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "mmvb_backend"
    )

    if project_root not in sys.path:
        sys.path.append(project_root)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mmvb_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
