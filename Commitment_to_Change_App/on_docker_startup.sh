#!/bin/bash
echo "Performing Docker container startup tasks before starting server..."
echo "Expiring commitments..."
python manage.py expire_commitments
echo "Sending reminder emails..."
python manage.py send_reminder_emails
echo "Startup tasks complete. Starting server..."