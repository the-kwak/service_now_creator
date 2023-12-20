from flask_limiter.util import get_remote_address
from the_spot_secret import *
import requests
from pathlib import Path
#  pyjwts
import jwt
import time
import requests
# Attempting to set up WSGI server though this may not be needed as it is not going out to the internet
from waitress import serve
import datetime
#import openpyxl


# Create as dictonary to store mute on entry value meetingid : mute_on_entry_bool
ZOOM_MEETINGS = {}

#loc = Path(__file__).with_name('Survey_response.xlsx')

app = Flask(__name__)

# Limiter will allow a device to only receive one api call from a specific device per minute
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1 per second"]#, "1 per minute"]
)

def get_jwt_token():
  '''
  jwt_header = {
    "alg": "HS256",
    "typ": "JWT"
  }'''

  production ={ 
      'jwt_api_key' : "nbvz6J0ST6WJceF-y4ADKA",
      'jwt_api_sec' : "zbNtup4snM2B2LPGKSDDk8PcOSsTU76dsbpv"
  }

  # exp is the current time in epoc + 60 seconds
  # will be decreased onces we know how well it funcions 
  # most likely to 2-6 seconds depending on execution time

  jwt_payload = {
    "iss": production['jwt_api_key'],
    "exp": (time.time() + 60) 
  }

  token = jwt.encode(jwt_payload, production['jwt_api_sec'], 'HS256')
  return token


# Function used to Make tickets in Service now from server
def get_zoom_meeting_info(meeting);
    
    zoom_meeting_url = f"https://api.zoom.us/v2/meetings/{meeting}"
    
    ## Check if meeting id is stored and if not
    if meeting in ZOOM_MEETINGS.keys():
        return ZOOM_MEETINGS[meeting]
    
    JWT = get_jwt_token()
    # Necessary Headers for the Post API to thespot
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {JWT}"}
    
    response = requests.get(zoom_meeting_url, headers=headers)
    print(response)
    
    if response.status_code == 404:
      print(response.json())
      return 'meeting invalid'
      
    try:
      json_data = response.json()
 

@app.route('/survey', methods=['POST'])
@limiter.limit("1/second")
def post_from_codecs():
  #global debounce
  data = request.data
  #client_ip = request.remote_addr

  #print(debounce)
  '''  
  if client_ip in request_dictionary.keys():
    # Compare to current time increment debounce
    check_time = request_dictionary[client_ip] + datetime.timedelta(seconds=15)
    current_time = datetime.datetime.now()
    
    if check_time > current_time:
      debounce = True

  else:
    request_dictionary[client_ip] = datetime.datetime.now()
    debounce = False
  '''
  #if debounce == False:
  data_dict = json.loads(data.decode())
  #print(f'dictonary:\n{data_dict}\n')
  print(data_dict)

  inc_number = str(create_incident(data_dict))

  print(inc_number)

  xlsx_list = [data_dict['codec_name'], data_dict['product'], data_dict['version'],data_dict['IP_Address'], data_dict['protocol'], data_dict['meeting_type'], data_dict['remote_uri'],
                data_dict['cause_type'], int(data_dict['duration']), data_dict['date'], data_dict['time'], data_dict['video'], data_dict['audio'],
                data_dict['disconnecting'], data_dict['clickshare'], data_dict['laptop'], data_dict['pc'], data_dict['username'], data_dict['feature_req'],inc_number
              ]
  try:
    write_to_xsl(xlsx_list)
  except:
    print('could not print to xsl')

  #print(f'{process.memory_info().rss/1000000} MB')
  return json.dumps({"Post_success": True, "ticket":  inc_number}), 201

if __name__ == '__main__':
  
    #serve(app, host="0.0.0.0", port=5050)
    print(get_zoom_meeting_info())
