from turtle import update
from the_spot_secret import *
import requests
from Zoom_token import *


def get_zoom_tickets():

    user = spot_zoom_user
    pwd = spot_zoom_pass

    base_dev_url = 'https://devspot.mskcc.org/api/now/table/sc_task?'
    base_test_url = 'https://testspot.mskcc.org/api/now/table/incident?'
    ## Zoom support = 'sysparm_query%3Dassignment_group%253Da9c2b014dbe11090892ce02b13961906'
    
    ## below with special characters
    query_criteria = 'sysparm_query=active%3Dtrue%5Eassignment_group%3Da9c2b014dbe11090892ce02b13961906&'

    field_display = 'sysparam_display_value=true&'

    response_fields = 'sysparm_fields=number,short_description,state,variables.first_name,variables.department,variables.requested_for_email'

    url = base_dev_url + query_criteria + field_display + response_fields

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

    return response.json()

def update_zoom_task(number, zoom_response, completed):
    
    user = spot_zoom_user
    pwd = spot_zoom_pass

    url = 'https://devspot.mskcc.org/api/now/import/u_update_catalog_task_api'

    ## Completion Status - Open (1), Pending (-5), Work In Progress (2), Closed Complete (3), Closed Skipped (7), Closed Incomplete (4)

    body = {
        'u_number'              : f'{number}',
        'u_comments'            : f'{zoom_response}'
    }
    
    if completed == 3:
        body['u_assigned_to_email'] = 'chirenok@mskcc.org'
        body['u_state'] =  f'{completed}'
    
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    response = requests.post(url, auth=(user, pwd), headers=headers, json=body)
    
    print(response)
    if response != 201:
        print()
        print(number)
        print('Status:', response.status_code, 'Headers:',
            response.headers, 'Error Response:', response.json())

    print(response.json())
    return response.json()

def main():
    zm_token = get_zoom_jwt_token()
    
    pass
if __name__ == '__main__':
    #tickets = get_zoom_tickets()['result']
    #print(len(tickets))

    updated = update_zoom_task('SCTASK0287804', "Bot Comment testing assignment", "Open")
    
    #for tic in tickets:
    """
        check username in Zoom
        if user exist and licensed
            update zoom task with :
                It looks like you already have a zoom account. Please login using SSO with the domain meetmsk.zoom.us.
                Please let me know if you have any questions.

                Thanks
                Khris

        elif user exist and basic:
            upgrade to licensed update task with:
            a new Zoom host account has been provisioned and is ready for use. Please search for Zoom activation email to activate your licensed account and login using SSO on your zoom app using the domain meetmsk.zoom.us
        
        elif user doesn't exit
            create licensed user and provision update task with:
            Zoom host account has been provisioned and is ready for use. Please login using SSO on your zoom app using the domain meetmsk.zoom.us



        
    """


    '''
        if 'SCTASK' in tic["number"]:
            print(tic)
        else:
            print(tic["number"])
    '''
