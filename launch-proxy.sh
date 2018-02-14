#!/bin/sh

set -e

jhub-vhost -c /etc/jhub-vhost.yml add \
           --hub-ip jupyterhub \
           --hub-port 8000 \
           --standalone \
           "${DOMAIN}"
echo "Launching nginx"
exec nginx -g "daemon off; pid /dev/null;"
