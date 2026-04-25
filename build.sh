#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install and upgrade tools
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Enter the project directory
cd LocalServiceManagement

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

