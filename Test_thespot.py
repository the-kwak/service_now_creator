from re import L
from the_spot_secret import *
import requests

def receive():

    user = spot_zoom_user
    pwd = spot_zoom_pass

    base_dev_url = 'https://devspot.mskcc.org/api/now/table/incident?'
    base_test_url = 'https://testspot.mskcc.org/api/now/table/incident?'
    ## Zoom support = 'sysparm_query%3Dassignment_group%253Da9c2b014dbe11090892ce02b13961906'
    
    ## below with special characters in hex
    query_criteria_hex = 'sysparm_query%3Dactive%253Dtrue%255Eassignment_group%253Da9c2b014dbe11090892ce02b13961906&'
    
    ## below with special characters
    query_criteria = 'sysparm_query=active%3Dtrue%5Eassignment_group%3Da9c2b014dbe11090892ce02b13961906&'

    query_criteria_all = 'sysparm_query=assignment_group%3Da9c2b014dbe11090892ce02b13961906&'

    field_display = 'sysparam_display_value=true&'

    response_fields = 'sysparm_fields=number%2Cshort_description%2Cdescription%2Cstate'

    url = base_dev_url + query_criteria_all + field_display + response_fields

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    response = requests.get(url, auth=(user, pwd), headers=headers)
    print(url)
    print(response)
    print('\n')

    if response.status_code != 200:
        print()
        print('Status:', response.status_code, 'Headers:',
            response.headers, 'Error Response:', response.json())
        exit()

    #print(response.json())
    return response.json()

def task_query():
    user = spot_zoom_user
    pwd = spot_zoom_pass
    
    base_dev_url = 'https://devspot.mskcc.org/api/now/table/sc_task?'
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    sys_param = 'sysparm_query=active%3Dtrue%5Eassignment_group.name%3DZoom%20Support&'
    sys_values = 'sysparm_fields=number,short_description,description,state,variables.first_name'

    url = base_dev_url + sys_param + sys_values

    response = requests.get(url, auth=(user, pwd), headers=headers)
    print(url)
    print(response)
    print('\n')

    if response.status_code != 200:
        print()
        print('Status:', response.status_code, 'Headers:',
            response.headers, 'Error Response:', response.json())
        exit()

    print(response.json())
    return response.json()

def create_incident(username):

    user = spot_survey_user
    pwd = spot_survey_pass

    '''
    data_dict['codec_name'], data_dict['product'], data_dict['version'], data_dict['protocol'], data_dict['meeting_type'], data_dict['remote_uri'],
    data_dict['cause_type'], int(data_dict['duration']), data_dict['date'], data_dict['time'], data_dict['video'], data_dict['audio'], data_dict['content'],
    data_dict['disconnecting'], data_dict['username'], data_dict['feature_req']
    '''

    caller = username

    base_dev_url = "https://devspot.mskcc.org/api/now/import/u_msk_create_incident_api"

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    request_body = {
                    "u_assignment_group":"WAN-Video Design",
                    "u_caller":"chirenok@mskcc.org",
                    "u_category":"Inquiry / Help",
                    "u_subcategory":"Operations",
                    "u_description":"Python test",
                    "u_short_description":"Short Desc - Python test",
                    "u_impact":"3",
                    "u_urgency":"3"
                }
    response = requests.post(base_dev_url, auth=(user, pwd), headers=headers, json=request_body)
    print(response)
    print(response.status_code)
    json_data = response.json()['result'][0]
    inc_number = json_data['display_value']

    print(inc_number)

    # Below is the response from above need to grab display and add it to outlook
    # {'import_set': 'ISET0031935', 'staging_table': 'u_msk_create_incident_api', 
    # 'result': [{'transform_map': 'MSK create incident', 'table': 'incident', 'display_name': 'number',
    # 'display_value': 'INC0133707', 
    # 'record_link': 'https://devspot.mskcc.org/api/now/table/incident/47679debdbde8dd0636a0e85ca961929',
    #  'status': 'inserted', 'sys_id': '47679debdbde8dd0636a0e85ca961929'}]}

    return inc_number

def check_tickets():
    tickets = receive()['result']
    print(len(tickets))
    print(len(tickets[0]))
    for key,val in tickets[0].items():
        print(f'{key}: {val}')
    return 0

def check_task():
    tickets = task_query()['result']
    print(len(tickets))
    print(len(tickets[0]))
    print(tickets[0]['number'])
    print(tickets[0]['short_description'])
    for key,val in tickets[0].items():
        print(f'{key}: {val}')
    return 0


if __name__ == '__main__':

    #check_tickets()
    #check_task()
    create_incident('chirenok')
