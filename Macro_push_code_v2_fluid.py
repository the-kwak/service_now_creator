from os import remove
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time
from xlrd import *
from xlutils.copy import copy
import xml.etree.ElementTree as ET
import traceback

# disable ssl warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# location of file
#loc = r'C:\Users\chirenok\Desktop\Msk_Mass_codec_upgrade\Working_Codecs_No_Crestron.xls'
loc = r'C:\Users\chirenok\Desktop\Msk_Mass_codec_upgrade\test_Jan_2021.xls'
# fix for some reason editor is adding \u202a stripping it to continue
#loc = loc.lstrip('\u202a')

'''
rwb = open_workbook(loc)
sheetr = rwb.sheet_by_index(0)
w = copy(open_workbook(loc))
max_rows = sheetr.nrows
'''

macros = {
    'MSK_Bundle_V5':'e3848f263afa4a13d1fd0dabb9ea64f67ea4b1ca28f0897ffcdc28cb7b71c810b6ee4aa1dfc12a724353fab7d312fd41c06c07069d3012c28213e0c1931300ed',
    'MSK_Bundle_V5_w-survey':'c61fad95c734f18181ddf7987587e3879e35d5273bb43f590d8987e2c6a2116c58aa3b53c212eb3e42dd133e65ba12a263318641f6f9fef068789c56fe3dacf8'
}

buttons ={
            'Teams': {
                    'PanelID':'teamsdialler',
                    'Macro_Name':'TeamsDialler'
                        },
            'Zoom': {
                    'PanelID':'zoomdialler',
                    'Macro_Name':'ZoomDialler'
                    },
            'Survey': {
                    'PanelID':'Survey',
                    'Macro_Name':'Survey_ticket'
                    },
            'ANR': {
                    'Macro_Name':'Auto_Noise_Removal'
                    },
        }

DEFAULT_PASSWORD = 'Basic YWRtaW46NzM2NjgzMjk='
DEFAULT_MACRO_LOC = f'http://172.21.251.54:8000/macro/MSK_Bundle_V5_w-survey.zip'
#HASH default is SHA512
DEFAULT_MACRO_HASH = macros['MSK_Bundle_V5_w-survey']

def push_buttons(ip, auth_val=DEFAULT_PASSWORD, macro_location=DEFAULT_MACRO_LOC, macro_hash=DEFAULT_MACRO_HASH):
    url = f"https://{ip}/putxml"

    payload = f"<Command>\r\n\t<Provisioning>\r\n\t\t<Service>\r\n\t\t\t<Fetch>\r\n\t\t\t<URL>{macro_location}</URL>\r\n\t\t\t<Checksum>{macro_hash}</Checksum>\r\n\t\t\t<Origin>Provisioning</Origin>  \r\n\t\t\t</Fetch>\r\n\t\t</Service> \r\n\t</Provisioning>\r\n</Command>"

    headers = {'Content-Type': 'text/xml','Authorization': auth_val}
    try:
        response = requests.request("POST", url, headers=headers, data = payload, verify=False)
    except:
        raise Exception(f'Unable to query device {ip}')

    print(response.text.encode('utf8'))
    print(response.status_code)
    tree = ET.fromstring(response.content)
    print(tree)
    result = [(f'{child.tag}:{child.attrib}') for child in tree]
    return result

# tested on roomkit mini/pro/sx80
fetch_result = push_buttons('172.20.228.45')
print(f'172.17.64.190:{fetch_result} \n')

# Buttons on line 22 are used in 
def remove_buttons(ip, remove, auth_val=DEFAULT_PASSWORD,):
    url = f"https://{ip}/putxml"

    payload=f"<Command>\r\n<Macros>\r\n <Macro>\r\n<Remove>\r\n<Name>{buttons[remove]['Macro_Name']}</Name>\r\n</Remove>\r\n</Macro>\r\n</Macros>\r\n<UserInterface>\r\n<Extensions>\r\n<Panel>\r\n<Remove>\r\n<PanelId>{buttons[remove]['PanelID']}</PanelId>\r\n</Remove>\r\n</Panel>\r\n</Extensions>\r\n</UserInterface>\r\n</Command>"

    headers = {'Content-Type': 'text/xml','Authorization': auth_val}
    try:
        response = requests.request("POST", url, headers=headers, data = payload, verify=False)
    except:
        raise Exception(f'Unable to query device {ip}')

    #print(response.text.encode('utf8'))
    tree = ET.fromstring(response.content)
    result = [(f'{child.tag}:{child.attrib}') for child in tree]
    print(result)
    return result

def remove_macros():
    remove_buttons(ip='172.20.228.45',remove='Zoom')
    remove_buttons(ip='172.20.228.45',remove='Teams')
    remove_buttons(ip='172.20.228.45',remove='Survey')

#remove_macros()


def main():
    f = open('log.txt', 'a')
    for i in range(1, max_rows):
        ip = sheetr.cell(i,1)
        print(ip.value)
        macro_key = 'MSK_Bundle_V5'
        macro_hash = macros[key]

        try:
            fetch_result = push_buttons(ip.value, macro_location=f'http://172.21.251.54:8000/{macro_key}.zip', macro_hash=macro_hash)
        except:
            f.write('\n')
            f.write(f'{ip}:\n')
            traceback.print_exc(file=f)
            f.write('\n')
            print(f'{ip}:{f}')
            continue  
        # request ServiceFetchResult status="OK"
        f.write(f'{ip}:{fetch_result} \n')

    f.close()

#main()