import ldap, ldap.sasl
import cmd
from Msk_secrets import *

addresses = [
    'here@blubb.com',
    'foo@bar.com',
    'whatever@wherever.org',
]
def find_ldap_users(uname):

    ldap_uri = 'ldap://140.163.18.225:389'
    base = 'DC=MSKCC,DC=ROOT,DC=MSKCC,DC=ORG'
    sAMAccountName = dev_account
    paswd = dev_pass
    trace_level = 0

    l = ldap.initialize(ldap_uri, trace_level=trace_level)
    l.set_option(ldap.OPT_REFERRALS, 0)
    l.simple_bind_s(sAMAccountName,paswd)

    result = l.search_s(
        base, ldap.SCOPE_SUBTREE, f'(mailNickname={uname}*)', ['*']
    )
    result.pop()
    
    for item in result:
        print(item[1]['mail'][0].decode("utf-8"))

    for item in result:
        for group in item[1]['memberOf']:
            group = group.decode("utf-8")
            group = group.split(',')
            print(group[0].split('=')[1])

    l.unbind_s()

find_ldap_users('chirenok')

