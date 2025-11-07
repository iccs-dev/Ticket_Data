#!/bin/bash

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Variables
SOURCE_FILE="/home/iccsadmin/Ticket_Data/sql_dump.sql"   # Destination on local machine
REMOTE_HOST="iccsadmin@172.20.122.101"
REMOTE_PASS="Xs0a0@bdpkgo"
REMOTE_SQL="/home/iccsadmin/sql_dump/tck_db.sql"
PYTHON_SCRIPT="/home/iccsadmin/Ticket_Data/tck_data.py"
VENV_PYTHON="/home/iccsadmin/Ticket_Data/venv/bin/python3"

# MySQL credentials
DB_USER="root"
DB_PASS="root123!"
DB_NAME="tck_data"   # <- change this to the DB Grafana will read from

# Ensure destination directory exists
DEST_DIR=$(dirname "$SOURCE_FILE")
mkdir -p "$DEST_DIR"

# Copy the SQL dump from remote to local
sshpass -p "$REMOTE_PASS" scp -o StrictHostKeyChecking=no "${REMOTE_HOST}:${REMOTE_SQL}" "${SOURCE_FILE}"

# Check result
if [ $? -eq 0 ]; then
    log "✅ SQL dump successfully transferred to $SOURCE_FILE"

    # Flash the dump into MySQL
    log "⚡ Restoring SQL dump into database: $DB_NAME"
    mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$SOURCE_FILE"

    if [ $? -eq 0 ]; then
        log "✅ Successfully restored SQL dump into $DB_NAME"
    else
        log "❌ Failed to restore SQL dump"
        exit 1
    fi

    # Run Python script using virtualenv
    if [ -f "$PYTHON_SCRIPT" ]; then
        log "🚀 Running Python script: $PYTHON_SCRIPT"
        "$VENV_PYTHON" "$PYTHON_SCRIPT"
        log "✅ Successfully ran Python script: $PYTHON_SCRIPT"
    else
        log "❌ Python script not found: $PYTHON_SCRIPT"
        exit 1
    fi

else
    log "❌ Error occurred during transfer"
    exit 1
fi
