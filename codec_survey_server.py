#! /home/chirenok/Survey_System/Survey_server/bin/python3
from flask import Flask, json, request
from flask_restful import Api #Resource, Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from the_spot_secret import *
import requests
from pathlib import Path
import smtplib
from email.message import EmailMessage


# Attempting to set up WSGI server though this may not be needed as it is not going out to the internet
from waitress import serve
import datetime
import openpyxl


loc = Path(__file__).with_name('Survey_response.xlsx')

## limiting access by ip  https://stackoverflow.com/questions/22251038/how-to-limit-access-to-flask-for-a-single-ip-address
## get mac address https://stackoverflow.com/questions/22188020/how-can-i-find-the-mac-address-of-a-client-on-the-same-network-using-python-fla

## https://realpython.com/token-based-authentication-with-flask/
## https://auth0.com/blog/developing-restful-apis-with-python-and-flask/

## Starting the Flask app to setup the API server
app = Flask(__name__)
CORS(app)

# Limiter will allow a device to only receive one api call from a specific device per minute
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1 per second"]#, "1 per minute"]
)
#api = Api(app, prefix="/api/v1")

# Function used to write data from codec to spreadsheet
def write_to_xsl(codec_info_list):
  wb = openpyxl.load_workbook(loc)
  ws = wb['Codecs']
  ws.append(codec_info_list)
  wb.save(filename=loc)
  wb.close()


# Function used to Make tickets in Service now from server
def create_incident(data_dict):

    #base_dev_url = "https://devspot.mskcc.org/api/now/import/u_msk_create_incident_api"
    #base_test_url = "https://testspot.mskcc.org/api/now/import/u_msk_create_incident_api"
    base_prod_url = "https://thespot.mskcc.org/api/now/import/u_msk_create_incident_api"
    
    # Setting the appropriate base url
    base_url = base_prod_url
    user = spot_survey_user
    pwd = spot_survey_pass

    '''
    data_dict['codec_name'], data_dict['product'], data_dict['version'], data_dict['protocol'], data_dict['meeting_type'], data_dict['remote_uri'],
    data_dict['cause_type'], int(data_dict['duration']), data_dict['date'], data_dict['time'], data_dict['video'], data_dict['audio'], data_dict['content'],
    data_dict['disconnecting'], data_dict['username'], data_dict['feature_req']
    '''
    
    # This will show up in the description of the ticket
    description = (f"user: {data_dict['username']}\ncodec type : {data_dict['product']}\ncodec version : {data_dict['version']}\nip_address: {data_dict['IP_Address']}"
                  f"\nCall information: {data_dict['protocol']}\n Meeting Type: {data_dict['meeting_type']}\nRemote URI: {data_dict['remote_uri']}\n"
                  f"Disconnect Reason:{data_dict['cause_type']}\nduration (seconds): {int(data_dict['duration'])}\nDate {data_dict['date']} {data_dict['time']}\n"
                  f"Video issues: {data_dict['video']}\nAudio issues: {data_dict['audio']}\n"
                  f"Clickshare issues: {data_dict['clickshare']}\nLaptop issues:{data_dict['laptop']}\nPC issues:{data_dict['pc']}\n"
                  f"Disconnecting: {data_dict['disconnecting']}\nOptional issue details: {data_dict['feature_req']}\n")
    
    #print(description)

    # Necessary Headers for the Post API to thespot
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    request_body = {
                    "u_assignment_group":"WAN-Video Design",
                    "u_caller":f"{data_dict['username']}",
                    "u_category":"Inquiry / Help",
                    "u_subcategory":"Operations",
                    "u_description":description,
                    "u_short_description":f"Issue with {data_dict['codec_name']} conference room ",
                    "u_impact":"3",
                    "u_urgency":"3"
                }
    
    response = requests.post(base_url, auth=(user, pwd), headers=headers, json=request_body)

    # Debug statements to be used if necessary
    #print(response)
    print(f'ServiceNow - {response.status_code}')
    if response.status_code == 401:
      print(response.json())

    #print(response.json())

    try:
      json_data = response.json()['result'][0]
      inc_number = json_data['display_value']

    except:
      ## Make the exception work with generic id if user enters id incorrectly
      ## Generic ID found it has been added to the response below

      request_body = {
                    "u_assignment_group":"WAN-Video Design",
                    "u_caller":"svc_restapi_codecsurvey",
                    "u_category":"Inquiry / Help",
                    "u_subcategory":"Operations",
                    "u_description":description,
                    "u_short_description":f"Issue with {data_dict['codec_name']} conference room ",
                    "u_impact":"3",
                    "u_urgency":"3"
                    }
      '''
      {'import_set': 'ISET0035389', 'staging_table': 'u_msk_create_incident_api', 
      'result': [{'transform_map': 'MSK create incident', 'table': 'incident', 'status': 'error',
                'error_message': 'Reference field value for incident.caller_id rejected: Test; Target record not found',
                'status_message': 'Reference field value for incident.caller_id rejected: Test'}]}
      '''
      
      response = requests.post(base_url, auth=(user, pwd), headers=headers, json=request_body)

      inc_number = response.json()['result'][0]['display_value']

      if response.status_code == 401:
        inc_number = "Error in ServiceNow "

        print(response)
        print(response.json())

    ### below is for wrong username
    
    ## Check username credentials with AD


    # Below is the response from above need to grab display and add it to outlook
    # {'import_set': 'ISET0031935', 'staging_table': 'u_msk_create_incident_api', 
    # 'result': [{'transform_map': 'MSK create incident', 'table': 'incident', 'display_name': 'number',
    # 'display_value': 'INC0133707', 
    # 'record_link': 'https://devspot.mskcc.org/api/now/table/incident/47679debdbde8dd0636a0e85ca961929',
    #  'status': 'inserted', 'sys_id': '47679debdbde8dd0636a0e85ca961929'}]}
   
    # print(f'{process.memory_info().rss/1000000} MB')
    return str(inc_number)

@app.route('/verifyChange', methods=['POST'])
@limiter.limit("10/second")
def verify_change():
    client_ip = request.remote_addr
    print(client_ip)
    change_data = request.get_json()
    change = change_data['change']
    # use servicenow to find
    #print(change)
    return json.dumps({"Post_success": True,'Change':change ,  "associatedTickets":  ['test','this', 'inident']}), 201


@app.route('/submitOT', methods=['POST'])
@limiter.limit("10/second")
def submit_ot():
    data = request.get_json()
    associated_tickets = data['associatedTickets']
    change = data['change']
    change_type = data['changeType']
    description = data['description']
    hours = data['hours']
    users = [user.strip() for user in  data['usernames'].split(',')]

    print(data)
    print(f'associated:{associated_tickets}')
    print(f'change:{change}')
    print(f'change_type:{change_type}')
    print(f'description:{description}')
    print(f'hours:{hours}')
    print(f'users:{users}')
    new_ticket_dict = {}
    for indx, user in enumerate(users):
        new_ticket_dict[user]={'ticketNum': f'ticket{indx}','ticketUrl':'ticket_url'}


    
    return json.dumps({"Post_success": True, "user_tickets": new_ticket_dict}), 201

def send_email():

    text = 'Good Morning,\n Here is the weekly zoom removal report.'
    msg = EmailMessage()
    msg['From'] = 'codec_survey_report@mskcc.org'
    msg['To'] = 'Rojash@mskcc.org'
    msg['Subject'] = 'Weekly Survey report'
    msg.set_content(text)

    server = 'exchange2007.mskcc.org'
    port = 25
    excel_file = 'Zoom removal list.xlsx'
    file_data = open(excel_file, 'rb').read()
    msg.add_attachment(file_data, maintype='application', subtype='xlsx', filename=excel_file)
    smtp = smtplib.SMTP(server, port)
    smtp.send_message(msg)
    smtp.quit()



@app.route('/survey', methods=['POST'])
@limiter.limit("1/second")
def post_from_codecs():
  #global debounce
  data = request.data
  #client_ip = request.remote_addr
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
    print('issues logging to xlsx')

#  print(f'{process.memory_info().rss/1000000} MB')
  return json.dumps({"Post_success": True, "ticket":  inc_number}), 201

if __name__ == '__main__':
  #app.run(host="0.0.0.0", ssl_context='adhoc')
  
  #print("Server started") 
  #serve(app, host="172.21.251.54", port=5000)
  
  serve(app, host="0.0.0.0", port=5000)
  #serve(app, host="0.0.0.0", port=5000, url_scheme='https')
