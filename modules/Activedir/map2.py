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
import networkx as nx
import random
import json
import py4cytoscape as p4c
import plotly.graph_objects as go
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
                
  
        
        async def query_description(self, dn,**options):
                """Queries the description for a given DN"""
                results = self.ldapConnection.search(searchFilter='(distinguishedName={})'.format(dn))
                if results:
                        for result in results:
                                try:
                                        for entry in result['attributes']:
                                                if str(entry['type']) == 'description':
                                                        description = str(entry['vals'][0])
#node_size = 0.05 * len(description)*size
                                                        self.network.add_node(description, title=description, color='white', label=description, group=dn)#node_size, id='description')
                                                        self.add_edge(description, dn, **options)
                                except:
                                        None
                        
                return None
        
        def add_edge(self, to, source, **options):
                self.network.add_edge(source, to,**options,group=source)
        
        
        def MAP(self):
                """ Maps the ad domain """
                entries = self.ldapConnection.search(searchFilter='(objectClass=*)', typesOnly=False, searchBase=self.root)
                account_security = {'1':"SCRIPT",'2':"ACCOUNTDISABLE",'8':"HOMEDIR_REQUIRED",'16':"LOCKOUT",'32':"PASSWORD NOT REQUIRED (DANGEROUS)",'64':"PASSWD_CANT_CHANGE"
                                    ,'128':'ENCRYPTED_TEXT_PWD_ALLOWED','256':'TEMP_DUPLICATE_ACCOUNT (RISK)','512':'NORMAL_ACCOUNT','2048':'INTERNAL DOMAIN_TRUST ACCOUNT (RISK',
                                    '4096':'WORKSTATION_TRUST_ACCOUNT','8192':'SERVER_TRUST_ACCOUNT','65536':'DONT_EXPIRE_PASSWORD (DANGEROUS)','131072':'MNS_LOGON_ACCOUNT',
                                    '262144':'SMARTCARD_REQUIRED (RISK)','524288':'TRUSTED_FOR_DELEGATION (DANGEROUS)','1048576':'NOT_DELEGATED','2097152':'USE_DES_KEY_ONLY',
                                    '4194304':'DONT_REQ_PREAUTH','8388608':'PASSWORD_EXPIRED','67108864':'TRUSTED_TO_AUTH_FOR_DELEGATION (DCSync, DANGEROUS)','66048':"Enabled, Password Doesn't Expire (RISK)",
                                    '514':"Disabled Account", '66082':"Disabled, Password Doesn't Expire & Not Required",'532480':'Domain controller','4260352':"Enabled - Password Does Not Expire - PreAuthorization Not Required (RISK)",
                                    "66080":"Disabled, Password Doesn’t Expire & Not Required",'546':'Disabled, Password Not Required'}
                description=None
                sAMAccountName=None
                for entry in entries:
                        try:
                                for attributes in entry['attributes']:
                        
                                        # else:
                                        #         description = None


                                        
                                        if str(attributes['type']) == 'distinguishedName':
                                                if attributes['vals'][0].asOctets().decode('utf-8').endswith('$') is False:
                                                        # User Account
                                                        
                                                        distinguishedName = attributes['vals'][0].asOctets().decode('utf-8')
#node_size = 0.05 * len(distinguishedName)*size
                                                        self.network.add_node(distinguishedName, color='purple', label=distinguishedName, title=distinguishedName, group=distinguishedName)#node_size, id='distinguishedName')
                                                        description = asyncio.run(self.query_description(distinguishedName,color='purple', title='description', label='description'))
                                                        
                                                                # self.network.add_edge(to=description, source=distinguishedName, color='lime', title='description')


                                        
                                        if str(attributes['type']) == 'sAMAccountName':
                                                if attributes['vals'][0].asOctets().decode('utf-8').endswith('$') is False:
                                                        # User Account
                                                        sAMAccountName = attributes['vals'][0].asOctets().decode('utf-8')
                                                        print(f'Found user: {sAMAccountName}')
#node_size = 0.5 * len(sAMAccountName)*size
                                                #node_size)
                                                        self.network.add_node(sAMAccountName, color='lime', label=sAMAccountName, title=sAMAccountName, group=distinguishedName)#node_size, id='sAMAccountName')
                                                        self.network.add_edge(distinguishedName, sAMAccountName, color='lime', title='user', label='user', group=distinguishedName)
                                                        # if description:
                                                        #         self.network.add_edge(to=description, source=sAMAccountName, color='lime', title='description')

                                        if str(attributes['type']) == 'ntSecurityDescriptor':
                                                security = str(attributes['vals'][0])#node_size = 0.05*len(security)*size
                                        #node_size)
                                                self.network.add_node(security, color='orange', label=security, title=security, group=distinguishedName)#node_size, id='ntSecurityDescriptor')
                                                if sAMAccountName:
                                                        self.network.add_edge(sAMAccountName, security, color='orange', title='ntSecurityDescriptor', label='ntSecurityDescriptor', group=distinguishedName)
                                                else:
                                                        self.network.add_edge(distinguishedName,security, color='orange', title='ntSecurityDescriptor', label='ntSecurityDescriptor', group=distinguishedName)
                                                # if description:
                                                #         self.network.add_edge(to=description, source=security, color='lime', title='description')
                                                
                                        if str(attributes['type']) == 'memberOf':
                                                groups = str(attributes['vals'][0])
                                                all_groups = groups.split(',')
                                                for group in all_groups:
                                                        group = group[3:]
                                                        self.network.add_node(group, color='lightgrey', label=group, title=group, group=distinguishedName)#node_size, id='group')

                                                        
#node_size = 0.05 * len(group)*size
                                                        
                                                        if sAMAccountName:
                                                                self.network.add_edge(sAMAccountName, group, color='lightgrey', title='group', label='group', group=sAMAccountName)
                                                        else:
                                                                if distinguishedName:
                                                                        self.network.add_edge(distinguishedName, group, color='lightgrey', title='group', label='group', group=distinguishedName)
                                                # if description:
                                                #         self.network.add_edge(to=description, source=groups, color='lime', title='description')
                                                
                                        if str(attributes['type']) == 'userAccountControl':
                                                userAccountControlnum = str(attributes['vals'][0].asOctets().decode('utf-8'))
                                                #print(userAccountControlnum)
                                                userAccountControl = account_security[userAccountControlnum]#node_size = 0.05 * len(userAccountControl)*size
                                                self.network.add_node(userAccountControl, color='red', label=userAccountControlnum, title=userAccountControl, group=distinguishedName)#node_size, id="userAccountControlnum")
                
                                                self.network.add_edge(distinguishedName, userAccountControlnum, color='red', title=userAccountControl, label='userAccountControl', group=distinguishedName)
                                                # if description:
                                                #         self.network.add_edge(to=description, source=userAccountControlnum, color='lime', title='description')
                                        
                                        if str(attributes['type']) == 'allowedAttributesEffective':
                                                perm = str(attributes['vals'][0])#node_size = 0.05 * len(perm)*size
                                                
                                                self.network.add_edge(distinguishedName,sAMAccountName, title=perm,label=perm, color='yellow')
                                        
                                        if str(attributes['type']) == 'allowedChildClassesEffective':
                                                childperm = str(attributes['vals'][0])
                                                self.network.add_edge(distinguishedName, sAMAccountName, title=childperm,label=childperm, color='yellow')


                        
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
                
                                
        def three_D(self):
                graph = self.network
                pos = nx.spring_layout(graph, dim=3, k=0.25)
                node_colors = []  # Create an empty list to store node colors
                group_colors = {}

                # Iterate over nodes
                for node in graph.nodes():
                        node_color = 'blue'  # Set a default node color
                        try:
                                group = graph.nodes[node]
                                group = group['group']
                        
                        # Assign a random color to each group if not already assigned
                                if group not in group_colors:
                                        group_colors[group] = f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"
                        
                                node_color = group_colors[group]
                        except Exception as e:
                                print(e)
                                print(group)
                                node_color = 'grey'
                        node_colors.append(node_color)

                edge_colors = []  # Create an empty list to store edge colors

                # Iterate over edges
                for node1, node2 in graph.edges():
                        edge_color = 'gray'  # Set a default edge color
                        
                        # Check if the edge has a specific color attribute
                        if 'color' in graph[node1][node2]:
                                edge_color = graph[node1][node2]['color']
                        edge_colors.append(edge_color)

                x = [pos[node][0] for node in graph.nodes()]
                y = [pos[node][1] for node in graph.nodes()]
                z = [pos[node][2] for node in graph.nodes()]

                edge_trace = go.Scatter3d(
                        x=[pos[node1][0] for node1, node2 in graph.edges()] + [None],
                        y=[pos[node1][1] for node1, node2 in graph.edges()] + [None],
                        z=[pos[node1][2] for node1, node2 in graph.edges()] + [None],
                        mode='lines',
                        line=dict(
                        color=edge_colors,  # Use the individual edge colors
                        width=1
                        ),
                        hoverinfo='none'
                )

                node_trace = go.Scatter3d(
                        x=x,
                        y=y,
                        z=z,
                        mode='markers',
                        marker=dict(
                        size=10,
                        color=node_colors,  # Use the individual node colors
                        symbol='circle'
                        ),
                        text=[str(node) for node in graph.nodes()],
                        hovertemplate='Node: %{text}<br>Node ID: %{marker.symbol}',
                )

                layout = go.Layout(
                        title='Directed Graph',
                        showlegend=False,
                        scene=dict(
                        xaxis=dict(title='X', showgrid=False, showticklabels=False, visible=False),
                        yaxis=dict(title='Y', showgrid=False, showticklabels=False, visible=False),
                        zaxis=dict(title='Z', showgrid=False, showticklabels=False, visible=False),
                        bgcolor='#222222'
                        ),
                        clickmode='event+select'
                )
                fig = go.Figure(data=[node_trace, edge_trace],layout=layout)
                fig.write_html('graph.html',auto_open=True,default_width='100%',default_height='100%')



