#!/usr/bin/python3

import os
import requests

# URL and login data
login_url = 'https://****.*****.***/login'
data_url = 'https://****.*****.***/api/datasources/proxy/****'
username = os.environ.get('GRAFANA_USERNAME')
password = os.environ.get('GRAFANA_PASSWORD')

zabbix_api_login = '******'
zabbix_api_psw_exposed = '********************************'

# Item data from Zabbix GTD
zabbix_itemid_lidice_int = "*****"
zabbix_itemid_lidice_nac = "*****"
zabbix_itemid_aguilucho_int = "*****"
zabbix_itemid_aguilucho_nac = "*****"

itemids = [
    zabbix_itemid_lidice_int,
    zabbix_itemid_lidice_nac,
    zabbix_itemid_aguilucho_int,
    zabbix_itemid_aguilucho_nac
]

zabbix_values_per_item = 4

# Login Request
login_data = {
    'user': username,
    'password': password
}

session = requests.Session()

try:
    login_response = session.post(login_url, json=login_data)
    login_response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error en inicio de sesión: {e}")
    exit()

# Auth Request
auth_payload = {
    'jsonrpc': '2.0',
    'method': 'user.login',
    'params': {
        'user': zabbix_api_login,
        'password': zabbix_api_psw_exposed
    },
    'id': 1
}

auth_headers = {
    'Cookie': login_response.headers['Set-Cookie']
}

try:
    auth_response = session.post(data_url, json=auth_payload, headers=auth_headers)
    auth_response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error al obtener el valor de auth: {e}")
    exit()

auth_json = auth_response.json()
auth_value = auth_json.get('result')

if not auth_value:
    print("No se pudo obtener el valor de auth.")
    exit()

# Data Request
data_payload = {
    "jsonrpc": "2.0",
    "method": "history.get",
    "params": {
        "output": "extend",
        "history": "3",
        "itemids": itemids,
        "sortfield": "clock",
        "sortorder": "DESC",
        "limit": zabbix_values_per_item * len(itemids)
    },
    "id": 1,
    "auth": auth_value
}

data_headers = {
    'Cookie': f'grafana_session={login_response.cookies["grafana_session"]}'
}

try:
    data_response = session.post(data_url, json=data_payload, headers=data_headers)
    data_response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error en la solicitud de datos: {e}")
    exit()

data_json = data_response.json()
print(data_json)
