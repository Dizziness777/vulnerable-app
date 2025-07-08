#!/bin/bash

set -e
sudo apt update
sudo apt upgrade -y

sudo apt install -y python3-pip postgresql libpq-dev

sudo -u postgres psql -c "CREATE DATABASE vuln_db;"
sudo -u postgres psql -c "CREATE USER vuln_user WITH PASSWORD 'weakpassword';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vuln_db TO vuln_user;"

pip3 install --upgrade pip
pip3 install flask psycopg2-binary werkzeug

sudo -u postgres psql vuln_db <<EOF
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);
EOF

echo "ВМ готова"