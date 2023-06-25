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
from networkx import Graph, spring_layout, ego_graph, graph
from pyvis.options import Options
from networkx import nx_agraph
import asyncio
import random

size = 150/3
class MapV2:
        def __init__(self, domain, dc, username, password,lmhash='',nthash='', kerberos=False):
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
                if kerberos == True:
                        self.ldapConnection.kerberosLogin(username, password, domain=domain, kdcHost=dc)
                
                else:
                        self.ldapConnection.login(user=username, password=password, domain=domain, lmhash=lmhash, nthash=nthash)
                self.network = Graph()
                
                #self.network.repulsion(node_distance=400, spring_length=300)
                #self.network.barnes_hut(gravity=-4000, central_gravity=0.05, spring_length=100)
  
        
        async def query_description(self, dn,**options):
                """Queries the description for a given DN"""
                results = self.ldapConnection.search(searchFilter='(distinguishedName={})'.format(dn))
                if results:
                        for result in results:
                                try:
                                        for entry in result['attributes']:
                                                if str(entry['type']) == 'description':
                                                        description = str(entry['vals'][0])
                                                        node_size = 0.05 * len(description)*size
                                                        self.network.add_node(description, title=description, color='white', label=description, size=node_size, id='description')
                                                        self.add_edge(description, dn, **options)
                                except:
                                        None
                        # entry = result[0]
                        # if 'attributes' in entry:
                        #         attributes = entry['attributes']
                        #         for attribute in attributes:
                        #                 if attribute['type'] == 'description':
                        #                         description = attribute['vals'][0]
                        #                         self.add_edge(to=str(description), source=dn, **kwargs)
                        #                         return str(description)
                        
                return None
        
        def add_edge(self, to, source, **options):
                self.network.add_edge(source, to,**options)
        
        
        def MAP(self):
                """ Maps the ad domain """
                entries = self.ldapConnection.search(searchFilter='(objectClass=*)', typesOnly=False, searchBase=self.root)
                #self.network.font_color = 'lightgrey'
                #self.network.set_edge_smooth('continuous')
                #self.network.toggle_hide_edges_on_drag(True)
                #self.network.inherit_edge_colors(True)
                #self.network.filter_menu = True
                #self.network.select_menu = True
                #self.network.toggle_drag_nodes(True)
                account_security = {'1':"SCRIPT",'2':"ACCOUNTDISABLE",'8':"HOMEDIR_REQUIRED",'16':"LOCKOUT",'32':"PASSWORD NOT REQUIRED (DANGEROUS)",'64':"PASSWD_CANT_CHANGE"
                                    ,'128':'ENCRYPTED_TEXT_PWD_ALLOWED','256':'TEMP_DUPLICATE_ACCOUNT (RISK)','512':'NORMAL_ACCOUNT','2048':'INTERNAL DOMAIN_TRUST ACCOUNT (RISK',
                                    '4096':'WORKSTATION_TRUST_ACCOUNT','8192':'SERVER_TRUST_ACCOUNT','65536':'DONT_EXPIRE_PASSWORD (DANGEROUS)','131072':'MNS_LOGON_ACCOUNT',
                                    '262144':'SMARTCARD_REQUIRED (RISK)','524288':'TRUSTED_FOR_DELEGATION (DANGEROUS)','1048576':'NOT_DELEGATED','2097152':'USE_DES_KEY_ONLY',
                                    '4194304':'DONT_REQ_PREAUTH','8388608':'PASSWORD_EXPIRED','67108864':'TRUSTED_TO_AUTH_FOR_DELEGATION (DCSync, DANGEROUS)','66048':"Enabled, Password Doesn't Expire (RISK)",
                                    '514':"Disabled Account", '66082':"Disabled, Password Doesn't Expire & Not Required",'532480':'Domain controller','4260352':"Enabled - Password Does Not Expire - PreAuthorization Not Required (RISK)",
                                    "66080":"Disabled, Password Doesn’t Expire & Not Required",'546':'Disabled, Password Not Required'}
                description=None
                for entry in entries:
                        try:
                                for attributes in entry['attributes']:
                                       
                                        # else:
                                        #         description = None


                                        
                                        if str(attributes['type']) == 'distinguishedName':
                                                if attributes['vals'][0].asOctets().decode('utf-8').endswith('$') is False:
                                                        # User Account
                                                        
                                                        distinguishedName = attributes['vals'][0].asOctets().decode('utf-8')
                                                        node_size = 0.05 * len(distinguishedName)*size
                                                        self.network.add_node(distinguishedName, color='purple', label=distinguishedName, title=distinguishedName, size=node_size, id='distinguishedName')
                                                        description = asyncio.run(self.query_description(distinguishedName,color='purple', title='description', label='description', weight=node_size*.3*2))
                                                        
                                                                # self.network.add_edge(to=description, source=distinguishedName, color='lime', title='description')


                                        
                                        if str(attributes['type']) == 'sAMAccountName':
                                                if attributes['vals'][0].asOctets().decode('utf-8').endswith('$') is False:
                                                        # User Account
                                                        sAMAccountName = attributes['vals'][0].asOctets().decode('utf-8')
                                                        print(f'Found user: {sAMAccountName}')
                                                        node_size = 0.5 * len(sAMAccountName)*size
                                                        print(node_size)
                                                        self.network.add_node(sAMAccountName, color='lime', label=sAMAccountName, title=sAMAccountName, size=node_size, id='sAMAccountName')
                                                        self.network.add_edge(distinguishedName, sAMAccountName, color='lime', title='user', weight=node_size*.3, label='user')
                                                        # if description:
                                                        #         self.network.add_edge(to=description, source=sAMAccountName, color='lime', title='description')

                                        if str(attributes['type']) == 'ntSecurityDescriptor':
                                                security = str(attributes['vals'][0])
                                                node_size = 0.05*len(security)*size
                                                print(node_size)
                                                self.network.add_node(security, color='orange', label=security, title=security, size=node_size, id='ntSecurityDescriptor')
                                                
                                                self.network.add_edge(distinguishedName, security, color='orange', title='ntSecurityDescriptor', weight=node_size*.3*2, label='ntSecurityDescriptor')
                                                # if description:
                                                #         self.network.add_edge(to=description, source=security, color='lime', title='description')
                                                
                                        if str(attributes['type']) == 'memberOf':
                                                groups = str(attributes['vals'][0])
                                                node_size = 0.05 * len(groups)*size
                                                self.network.add_node(groups, color='lightgrey', label=groups, title=groups, size=node_size, id='groups')
                                                self.network.add_edge(distinguishedName, groups, color='lightgrey', title='groups', weight=node_size*.3*2, label='groups')
                                                # if description:
                                                #         self.network.add_edge(to=description, source=groups, color='lime', title='description')
                                                
                                        if str(attributes['type']) == 'userAccountControl':
                                                userAccountControlnum = str(attributes['vals'][0].asOctets().decode('utf-8'))
                                                #print(userAccountControlnum)
                                                userAccountControl = account_security[userAccountControlnum]
                                                node_size = 0.05 * len(userAccountControl)*size
                                                self.network.add_node(userAccountControlnum, color='red', label=userAccountControlnum, title=userAccountControl, size=node_size, id="userAccountControlnum")
                                                self.network.add_edge(distinguishedName, userAccountControlnum, color='red', title=userAccountControl, label='userAccountControl', weight=node_size*.3*2)
                                                # if description:
                                                #         self.network.add_edge(to=description, source=userAccountControlnum, color='lime', title='description')
                                        
                                        if str(attributes['type']) == 'allowedAttributesEffective':
                                                perm = str(attributes['vals'][0])
                                                node_size = 0.05 * len(perm)*size
                                                self.network.add_edge(distinguishedName,sAMAccountName, title=perm,label=perm, weight=node_size*.3*2, color='yellow')
                                        
                                        if str(attributes['type']) == 'allowedChildClassesEffective':
                                                childperm = str(attributes['vals'][0])
                                                self.network.add_edge(distinguishedName, sAMAccountName, title=childperm,label=childperm, weight=node_size*.3*2, color='yellow')


                        
                        except Exception as e:
                                print(e)
                k = 0.15
                iterations = 20
                #l = spring_layout(self.network,k=k, iterations=iterations)
                l = nx_agraph.graphviz_layout(self.network, prog='neato')
                save_file = self.domain.replace('.', '')
                network_graph = Network(height='82.2vh', directed=True, bgcolor='#222222',font_color='white',select_menu=True, neighborhood_highlight=True, notebook=True, cdn_resources='local')
                network_graph.barnes_hut(overlap=1)
                #self.network.add_node(self.domain, color='gold', size=25)
                #ego = ego_graph(G=self.network, n=self.domain)
                network_graph.from_nx(self.network)
                network_graph.filter_menu = True
                network_graph.toggle_physics(True)
                network_graph.write_html(save_file + '.html')
                
                
                                
                        


m = MapV2(domain='megacorp.local', dc='10.10.10.179', username='sbauer', password="D3veL0pM3nT!", kerberos=False)
m.MAP()
