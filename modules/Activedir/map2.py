from impacket.ldap import ldap
from datetime import datetime
from pyasn1.codec.der import decoder, encoder
from impacket import version
from impacket.dcerpc.v5.samr import UF_ACCOUNTDISABLE, UF_TRUSTED_FOR_DELEGATION, \
    UF_TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION
from impacket.examples import logger
from impacket.examples.utils import parse_credentials
from impacket.krb5 import constants
from impacket.krb5.asn1 import TGS_REP
from impacket.krb5.ccache import CCache
from impacket.krb5.kerberosv5 import getKerberosTGT, getKerberosTGS
from impacket.krb5.types import Principal
from impacket.ldap import ldap, ldapasn1
from impacket.smbconnection import SMBConnection, SessionError
from impacket.ntlm import compute_lmhash, compute_nthash
from pyvis.network import Network
from pyvis.options import Options

      
global users
users = []
def getUnixTime(t):
        t -= 116444736000000000
        t /= 10000000
        return t

def processRecord_users(item):
        if isinstance(item, ldapasn1.SearchResultEntry) is not True:
            return
        sAMAccountName = ''
        pwdLastSet = ''
        mail = ''
        lastLogon = 'N/A'
        try:
            for attribute in item['attributes']:
                userAccountControl = 'None'
                security = 'None'
                groups = 'None'
                if str(attribute['type']) == 'sAMAccountName':
                    if attribute['vals'][0].asOctets().decode('utf-8').endswith('$') is False:
                        # User Account
                        if str(attribute['type']) == 'description':
                                description = str(attribute['vals'][0])
                        sAMAccountName = attribute['vals'][0].asOctets().decode('utf-8')
                        
                        
                elif str(attribute['type']) == 'pwdLastSet':
                    if str(attribute['vals'][0]) == '0':
                        pwdLastSet = '<never>'
                    else:
                        pwdLastSet = str(datetime.fromtimestamp(getUnixTime(int(str(attribute['vals'][0])))))
                elif str(attribute['type']) == 'lastLogon':
                    if str(attribute['vals'][0]) == '0':
                        lastLogon = '<never>'
                    else:
                        lastLogon = str(datetime.fromtimestamp(getUnixTime(int(str(attribute['vals'][0])))))
                elif str(attribute['type']) == 'memberOf':
                    groups = str(attribute['vals'][0])

                
                elif str(attribute['type']) == 'ntSecurityDescriptor':
                    security = str(attribute['vals'][0])
                    if not security:
                            security = 'None'
                elif str(attribute['type']) =='userAccountControl':
                        userAccountControl = str(attribute['vals'][0])
                    

            users.append({'user':sAMAccountName,'groups':groups,'permissions':security, 'accountControl':userAccountControl,'pwdLastSet':pwdLastSet})
        except Exception as e:
            print(e)
            pass



class MapV2:
        def __init__(self, domain, dc, username, password,lmhash='',nthash=''):
                self.username = username
                self.domain = domain
                self.password = password
                self.dc = dc
                self.lmhash = lmhash
                self.nthash = nthash
                data = self.domain.split('.')
                self.root = ''
                for d in data:
                        if self.root == '':
                                self.root = 'DC='+d
                        else:
                                self.root = self.root + ',DC=' + d
                print(self.root)
                self.ldapConnection = ldap.LDAPConnection('ldap://%s' % self.dc, baseDN=self.root, dstIp=dc)
                print(self.ldapConnection.kerberosLogin(username, password, domain=domain, kdcHost=dc))
                self.network = Network(height='82vh', directed=True, bgcolor='#222222', heading=domain,font_color='white',select_menu=True, neighborhood_highlight=True, notebook=False, cdn_resources='local')
                self.network.repulsion(node_distance=400, spring_length=300)
                self.network.barnes_hut(gravity=-4000, central_gravity=0.05, spring_length=100)
  
        
        
        def MAP(self):
                """
SCRIPT 	0x0001 	1
ACCOUNTDISABLE 	0x0002 	2
HOMEDIR_REQUIRED 	0x0008 	8
LOCKOUT 	0x0010 	16
PASSWD_NOTREQD 	0x0020 	32
PASSWD_CANT_CHANGE      64

You can't assign this permission by directly modifying the UserAccountControl attribute. For information about how to set the permission programmatically, see the Property flag descriptions section. 	0x0040 	64
ENCRYPTED_TEXT_PWD_ALLOWED 	0x0080 	128
TEMP_DUPLICATE_ACCOUNT 	0x0100 	256
NORMAL_ACCOUNT 	0x0200 	512
INTERDOMAIN_TRUST_ACCOUNT 	0x0800 	2048
WORKSTATION_TRUST_ACCOUNT 	0x1000 	4096
SERVER_TRUST_ACCOUNT 	0x2000 	8192
DONT_EXPIRE_PASSWORD 	0x10000 	65536
MNS_LOGON_ACCOUNT 	0x20000 	131072
SMARTCARD_REQUIRED 	0x40000 	262144
TRUSTED_FOR_DELEGATION 	0x80000 	524288
NOT_DELEGATED 	0x100000 	1048576
USE_DES_KEY_ONLY 	0x200000 	2097152
DONT_REQ_PREAUTH 	0x400000 	4194304
PASSWORD_EXPIRED 	0x800000 	8388608
TRUSTED_TO_AUTH_FOR_DELEGATION 	0x1000000 	16777216
PARTIAL_SECRETS_ACCOUNT 	0x04000000 	67108864
"""
                entries = self.ldapConnection.search(searchFilter='(objectClass=*)', typesOnly=False)
                #self.network.font_color = 'lightgrey'
                self.network.set_edge_smooth('continuous')
                self.network.toggle_hide_edges_on_drag(True)
                self.network.inherit_edge_colors(True)
                self.network.filter_menu = True
                self.network.select_menu = True
                self.network.toggle_drag_nodes(True)
                account_security = {'1':"SCRIPT",'2':"ACCOUNTDISABLE",'8':"HOMEDIR_REQUIRED",'16':"LOCKOUT",'32':"PASSWD NOTREQD",'64':"PASSWD_CANT_CHANGE"
                                    ,'128':'ENCRYPTED_TEXT_PWD_ALLOWED','256':'TEMP_DUPLICATE_ACCOUNT','512':'NORMAL_ACCOUNT','2048':'INTERDOMAIN_TRUST_ACCOUNT',
                                    '4096':'WORKSTATION_TRUST_ACCOUNT','8192':'SERVER_TRUST_ACCOUNT','65536':'DONT_EXPIRE_PASSWORD','131072':'MNS_LOGON_ACCOUNT',
                                    '262144':'SMARTCARD_REQUIRED','524288':'TRUSTED_FOR_DELEGATION','1048576':'NOT_DELEGATED','2097152':'USE_DES_KEY_ONLY',
                                    '4194304':'DONT_REQ_PREAUTH','8388608':'PASSWORD_EXPIRED','67108864':'TRUSTED_TO_AUTH_FOR_DELEGATION'}
                for entry in entries:
                        try:
                                for attributes in entry['attributes']:
                                        if str(attributes['type']) == 'description':
                                                description = str(attributes['vals'][0])
                                                self.network.add_node(description, color='black', label=description, title='description')


                                        
                                        if str(attributes['type']) == 'distinguishedName':
                                                if attributes['vals'][0].asOctets().decode('utf-8').endswith('$') is False:
                                                        # User Account
                                                        distinguishedName = attributes['vals'][0].asOctets().decode('utf-8')
                                                        self.network.add_node(distinguishedName, color='purple', label=distinguishedName, title='DN')
                                                        self.network.add_edge(to=description, source=distinguishedName, color='cyan', title='description')


                                        
                                        if str(attributes['type']) == 'sAMAccountName':
                                                if attributes['vals'][0].asOctets().decode('utf-8').endswith('$') is False:
                                                        # User Account
                                                        sAMAccountName = attributes['vals'][0].asOctets().decode('utf-8')
                                                        
                                                        self.network.add_node(sAMAccountName, color='lime', label=sAMAccountName, title='User')
                                                        self.network.add_edge(distinguishedName, sAMAccountName, color='lightgrey', title='username')

                                        if str(attributes['type']) == 'ntSecurityDescriptor':
                                                security = str(attributes['vals'][0])
                                                self.network.add_node(security, color='grey', label=security, title='security permissions')
                                                self.network.add_edge(distinguishedName, security, color='green', title='ntSecurityDescriptor')
                                                
                                        if str(attributes['type']) == 'memberOf':
                                                groups = str(attributes['vals'][0])
                                                self.network.add_node(groups, color='grey', label=groups, title='groups')
                                                self.network.add_edge(distinguishedName, groups, color='blue', title='groups')
                                                
                                        if str(attributes['type']) == 'userAccountControl':
                                                userAccountControl = str(attributes['vals'][0])
                                                userAccountControl = account_security[userAccountControl]
                                                self.network.add_node(userAccountControl, color='grey', label=userAccountControl, title='userAccountControl')
                                                self.network.add_edge(distinguishedName, userAccountControl, color='white', title='userAccountControl')
                                        
                        
                        
                        except Exception as e:
                                print(e)
                save_file = self.domain.replace('.', '')
                self.network.write_html(save_file + '.html')
                
                
                                
                        


m = MapV2(domain='absolute.htb', dc='dc.absolute.htb', username='d.klay', password='Darkmoonsky248girl')
m.MAP()
