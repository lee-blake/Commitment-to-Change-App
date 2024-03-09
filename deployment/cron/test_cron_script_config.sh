#!/bin/bash
source `dirname $0`/../setup_environment.sh
python "$CMECTCREPOROOT/Commitment_to_Change_App/manage.py" "check"