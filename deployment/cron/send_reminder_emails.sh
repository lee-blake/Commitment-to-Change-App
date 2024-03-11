#!/bin/bash
if [[ ! -v CMECTCENVSET ]]; then
    source `dirname $0`/setup_environment.sh
fi
python "$CMECTCREPOROOT/Commitment_to_Change_App/manage.py" "send_reminder_emails"