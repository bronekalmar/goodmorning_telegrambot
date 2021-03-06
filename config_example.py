# -*- coding: utf-8 -*-
import pymysql

#goodmorning_bot
token = 'token'

LIST_OF_ADMINS = ["enter ID of admin(s)"]

# DB to store chat IDs, wishes and other stuff on HEROKU
"""
db = pymysql.connect(host='uri',
                             user='user',
                             password='pass',
                             db='base',
                             use_unicode=True,
                             charset="utf8")
"""

# DB to store chat IDs, wishes and other stuff on VPS
db = pymysql.connect(host='host',
                             user='user',
                             password='pass',
                             db='base',
                             use_unicode=True,
                             charset="utf8")
# webhook section
WEBHOOK_HOST = 'host ip'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(token)
# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST
