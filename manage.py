#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'steroid_plan.settings')
    # Если команда — runserver и порт не указан, добавляем 0.0.0.0:58778
    if len(sys.argv) >= 2 and sys.argv[1] == 'runserver':
        if len(sys.argv) == 2:
            sys.argv.append('0.0.0.0:58778')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
