#  python-jose
import re
from jose import jwt
import time
import json
import requests

### Need to create a JWT token to continue.
def get_zoom_jwt_token():

  production ={ 
      'jwt_api_key' : "nbvz6J0ST6WJceF-y4ADKA",
      'jwt_api_sec' : "zbNtup4snM2B2LPGKSDDk8PcOSsTU76dsbpv"
  }

  jwt_payload = {
    "iss": production['jwt_api_key'],
    "exp": (time.time() + 60) 
  }

  token = jwt.encode(jwt_payload, production['jwt_api_sec'], 'HS256')
  return token

## requests test check user email exist
def check_user(email, token):
  
  license = None
  
  url = f'https://api.zoom.us/v2/users/{email}'
  payload = {}
  headers = {
      'Authorization': f'Bearer {token}',
      'Conent-Type' : 'application/json'
  }
  
  response = requests.get(url, headers=headers, data=payload)
  data = response.json()

  # if user is not found status returns a 404
  if response.status_code == 404:
    return 0

  elif response.status_code == 200 and 'type' in data:
    #print(response.status_code)
    #print(email)
    #print(data['type'])
    license = data['type']
    return license

def update_user(email, token):
  url = f'https://api.zoom.us/v2/users/{email}'
  params = {'login_type': 101,
  }
  json = {
    'type': 2
  }
  headers = {
      'Authorization': f'Bearer {token}',
      'Conent-Type' : 'application/json'
  }
  
  response = requests.patch(url, headers=headers, params=params, json=json)

  if response.status_code !=204:
    print(response.status_code)
    print(response.content)
    return None

  
  print(response.status_code)
  print(email)
  print(response.content)
  return None

### data returned for email that is basic or licensed
'''
{
    'id': 'I1hNCf_rTfOOhwhS5uAmJA',
    'first_name': 'Khristopher',
    'last_name': 'Chireno',
    'email': 'chirenok@mskcc.org',
    'type': 2,
    'role_name': 'Admin',
    'pmi': 6752058323,
    'use_pmi': False,
    'vanity_url': 'https://meetmsk.zoom.us/my/joinchireno',
    'personal_meeting_url': 'https://meetmsk.zoom.us/j/6752058323',
    'timezone': 'America/New_York',
    'verified': 0,
    'dept': '',
    'created_at': '2018-03-07T18:23:47Z',
    'last_login_time': '2021-01-21T13:54:44Z',
    'last_client_version': '5.4.59296.1207(win)',
    'host_key': '329534',
    'cms_user_id': '',
    'jid': 'i1hncf_rtfoohwhs5uamja@xmpp.zoom.us',
    'group_ids': [],
    'im_group_ids': [],
    'account_id': 'pOA0WdjnQBeISaKhZnehDw',
    'language': '',
    'phone_country': 'US',
    'phone_number': '+1 6468880726',
    'status': 'active',
    'job_title': '',
    'company': 'MSK',
    'location': '',
    'login_types': [100, 101],
    'role_id': '1'
}
'''
### data for email that doesn't exist
'''
{ 
  'code': 1001,
  'message': 'User does not exist: fake@email.org.'
}
'''
def del_user(email, token):
  
  headers = {'Authorization': f'Bearer {token}'}
  url = f"https://api.zoom.us/v2/users/{email}?action=disassociate"
  remove = requests.delete(url=url, headers=headers)
  print(remove.text)
  return remove


### Relevant data 'type'
# type 0 -> Does Not exist
# type 1 -> basic
# type 2 -> Licensed
# type 3 -> On-Prem

def list_users(token):
  # https://api.zoom.us/v2/users?status=active&page_size=30&role_id=<string>&page_number=<string>&include_fields=<string>&next_page_token=<string>
  page_number = 1
  user_list = []
  headers = {'Authorization': f'Bearer {token}'}
  page_count = None

  while page_count is None or page_number <= page_count:
    url = f"https://api.zoom.us/v2/users?status=active&page_size=300&page_number={page_number}"

    users =  requests.get(url=url, headers=headers)
    users = users.json()
    page_count = int(users['page_count'])
    
    for i in users['users']:
      user_list.append(i['email'])
      #print(i['email'])

    page_number += 1

  print(len(user_list))
  result_dict = {'emails': user_list}
  
  with open('All_zoom_users.json', 'w') as fp:
    json.dump(result_dict, fp)
  
  return result_dict

if __name__ == '__main__':

  new_token = get_zoom_jwt_token()
  
  email = 'chirenok@mskcc.org'
  current_user_status = check_user(email, new_token)
  print(current_user_status)
  if current_user_status == 0:
    print('New User has to be made')
  elif current_user_status == 1:
    print('User is being upgraded')
  elif current_user_status == 2:
    print('Already upgraded')

  #update_user(email, new_token)
  #current_user_status = check_user(email, new_token)
  
  ### gets list of users
  #users = list_users(new_token)
  #print(len(users['emails']))
  #print(users)

  ### Deletes user
  #print(del_user(email, new_token))