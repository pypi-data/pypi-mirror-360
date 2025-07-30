import json

import requests
import urllib3
from pathlib import Path
import logging

  
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_credentials(key):
  try:
    with open(f'{Path.home()}/.dereberus/user_credentials.json', 'r') as openfile:
      return json.load(openfile).get(key)
  except (FileNotFoundError, json.JSONDecodeError):
      return

def get_Dereberus_host():
  
  envir = get_credentials('env')
  if envir == 'dev':
    return 'http://127.0.0.1:5858'
  deployed_domain = "io" if envir == 'prod' else 'dev'
  return f"https://keypoint.delium.{deployed_domain}/dereberus/"  


class DereberusClient:
  def __init__(self):
    return
  
  def get(self, auth_token, endpoint, headers=None, data=None):
    Dereberus_url = get_Dereberus_host()
    headers = self.create_headers(auth_token, headers)
    res = requests.get(f"{Dereberus_url}/{endpoint}", data=json.dumps(data), verify=False, headers=headers)
    return res

  def post(self, auth_token, endpoint, headers=None, data=None):
    Dereberus_url = get_Dereberus_host()
    headers = self.create_headers(auth_token, headers)
    res = requests.post(f"{Dereberus_url}/{endpoint}", data=json.dumps(data), verify=False, headers=headers)
    return res

  def create_headers(self, auth_token, headers):
    final_headers = {}
    if headers is not None:
      for k, v in headers.items():
        final_headers[k] = v
    final_headers['X-API-TOKEN'] = auth_token
    final_headers['Content-Type'] = "application/json"
    return final_headers


DereberusApi = DereberusClient()

