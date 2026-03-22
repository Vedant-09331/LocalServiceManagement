"""
One-shot script to apply pending Django migrations.
Run this ONCE from the project root:
  python apply_migrations.py
"""
import os
import sys
import django

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LocalServiceManagement.settings')

django.setup()

from django.core.management import call_command

print("Running makemigrations...")
call_command('makemigrations', '--check', verbosity=0)

print("Applying migrations...")
call_command('migrate', verbosity=2)

print("\nDone! All migrations applied.")
