#!/bin/bash
# Tasks that cron will run daily should be included here. Comment them out in
# deployment if you wish to disable them.
`dirname $0`/expire_commitments.sh
`dirname $0`/send_reminder_emails.sh