#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# VM Provisioning Script (Azure)
# Called by Terraform remote-exec provisioner.
#
# Usage: install.sh <db_fqdn> <db_name> <db_user> <db_password> <storage_account> <storage_key> <admin_user>
# ============================================================

DB_FQDN="$1"
DB_NAME="$2"
DB_USER="$3"
DB_PASSWORD="$4"
STORAGE_ACCOUNT="$5"
STORAGE_KEY="$6"
ADMIN_USER="$7"

export DEBIAN_FRONTEND=noninteractive

echo "========================================"
echo " [1/5] Updating system packages"
echo "========================================"
apt-get update -y
apt-get upgrade -y

echo "========================================"
echo " [2/5] Installing Python 3, pip, venv"
echo "========================================"
apt-get install -y python3 python3-pip python3-venv libpq-dev

echo "========================================"
echo " [3/5] Setting up Python virtual env"
echo "========================================"
cd /home/${ADMIN_USER}/app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "========================================"
echo " [4/5] Writing environment config"
echo "========================================"
cat > /home/${ADMIN_USER}/app/.env <<ENVEOF
DB_HOST=${DB_FQDN}
DB_PORT=5432
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
AZURE_STORAGE_ACCOUNT=${STORAGE_ACCOUNT}
AZURE_STORAGE_KEY=${STORAGE_KEY}
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
ENVEOF

chmod 600 /home/${ADMIN_USER}/app/.env

echo "========================================"
echo " [5/5] Creating systemd service"
echo "========================================"
cat > /etc/systemd/system/flaskapp.service <<SVCEOF
[Unit]
Description=Flask Cloud Application
After=network.target

[Service]
User=${ADMIN_USER}
Group=${ADMIN_USER}
WorkingDirectory=/home/${ADMIN_USER}/app
EnvironmentFile=/home/${ADMIN_USER}/app/.env
ExecStart=/home/${ADMIN_USER}/app/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 wsgi:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable flaskapp
systemctl start flaskapp

echo "========================================"
echo " Initializing database"
echo "========================================"
cd /home/${ADMIN_USER}/app
source venv/bin/activate
export DB_HOST="${DB_FQDN}"
export DB_PORT="5432"
export DB_NAME DB_USER DB_PASSWORD AZURE_STORAGE_ACCOUNT AZURE_STORAGE_KEY
python3 init_db.py --seed

echo "========================================"
echo " Deployment complete!"
echo " App running on port 5000"
echo "========================================"
