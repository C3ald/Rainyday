import json
from ldap3 import Server, Connection, ALL, SUBTREE, NTLM, KERBEROS, SASL, DIGEST_MD5
from impacket import version
import networkx as nx
import sys
from py2neo import Graph, Node, Relationship
from pyvis.network import Network

class ADMap:
        """ domain should only be the domain name and not ldap:// and same with domain controller ip"""
        def __init__(self, username, domain,password, domain_ip, nthash=None, lmhash=None):
                self.username = f'{domain}\{username}'
                self.kerob_user = username
                #username = f'{domain}\{username}'
                self.password = password
                self.domain_ip = domain_ip
                self.domain = domain
                root_dn = ''
                data = self.domain.split('.')
                for d in data:
                        if len(root_dn) < 1:
                                root_dn = root_dn + f'DC={d}'
                        else:
                                root_dn = root_dn + f',DC={d}'
                self.root_dn = root_dn
                self.server = Server(host=domain_ip, get_info=ALL)
                self.graph = nx.DiGraph()
                self.processed_objects = set()
                self.final = []
                self.i = 1
                try:
                        self.connection = Connection(server=self.server,user=username, password=password, authentication=NTLM, auto_bind=True)
                except:
                        self.connection = Connection(server=self.server,user=username, password=password, authentication=SASL, sasl_mechanism=DIGEST_MD5)
                        self.connection.bind()
        #         self.authentication_methods = [
        #     (SIMPLE, "Simple Bind"),
        #     (SASL, "SASL (Kerberos)"),
        #     (NTLM, "NTLM (Windows Integrated Authentication)"),
        #     (SIMPLE, "SSL/TLS Client Certificate"),
        #     (ANONYMOUS, "Anonymous Bind")
        # ]
        
        #         self.try_authentication_methods()
    
        # def try_authentication_methods(self):
        #         server =self.server
        
        #         for auth_method, method_name in self.authentication_methods:
        #                 try:
        #                         if auth_method != SASL:
                                        
        #                                 connection = Connection(server, user=self.username, password=self.password, authentication=auth_method)
        #                         else:
        #                                 connection = Connection(server, authentication=SASL, user=self.username, password=self.password, sasl_mechanism=)
        #                         if connection.bind():
        #                                 print("Successful authentication using", method_name)
        #                                 self.connection = connection
        #                                 break
        #                 except Exception as e:
        #                         print(e)
        #         return sys.exit(1)
        #         # print("Failed authentication using", method_name)
        #         # print("Error:", str(e))
    
        # def is_authenticated(self):
        #         return self.connection is not None
        #         # try:
        #         #         self.connection = Connection(server=server,user=username, password=password, authentication=NTLM, auto_bind=True)
        #         # except:
        #         #         try:
        #         #                 self.connection = Connection(server=server, user=username, password=password,auto_bind=True, authentication=SASL, sasl_mechanism=PLAIN, sasl_credentials=(self.domain,username, password))
        #         #         except:
        #         #                 self.connection = Connection(server=server, user=username, password=password, auto_bind=True, authentication=PLAIN)
        #         #self.connection.bind()

                
        
        def print_objs(self):
                """ prints all the objects in the connection """
                self.connection.search(search_base=self.root_dn, search_filter='(objectClass=*)', search_scope=SUBTREE)
                print(self.connection.entries)
                
                
        def get_objs(self):
                self.connection.search(search_base=self.root_dn, search_filter='(objectClass=*)',search_scope=SUBTREE, attributes=['distinguishedName', 'memberOf', 'mail', 'givenName', 'ntSecurityDescriptor', 'sAMAccountName', 'objectGUID', 'userAccountControl'])
                #print(self.connection.entries)
                num_of_entries = len(self.connection.entries)
                
                for entry in self.connection.entries:
                        print(f'Scanning: {self.i}/{num_of_entries}                    ', end='\r')
                        dn = entry.distinguishedName.value
                        name = entry.givenName.value
                        mail = entry.mail.value
                        user = entry.sAMAccountName.value
                        #group = entry.group.value
                        
                        
                        if dn != None and dn not in self.processed_objects:
                                self.graph.add_node(dn, color="grey", title=f"mail: {mail} given name: {name} user: {user}")
                                self.processed_objects.add(dn)
                        
                        else:
                                continue
                        if 'memberOf' in entry:
                                memberof = entry.memberOf.values
                                for group in memberof:
                                        self.graph.add_node(group, title=f'group: {group}', color='yellow')
                                        if dn:
                                                self.graph.add_edge(dn, group, color="yellow", title='member of')
                                        if name:
                                                self.graph.add_edge(name, group,title='member of',color='yellow')
                                        if user:
                                                self.graph.add_edge(user, group, title='member of',color='yellow')
                                                
                        if 'ntSecurityDescriptor' in entry:
                                perm = entry.ntSecurityDescriptor.values
                                for per in perm:
                                        self.graph.add_node(per, title=f'permission: {per}', color='blue')
                                        if dn:
                                                self.graph.add_edge(dn, per, color='blue', title='permissions')
                                        if name:
                                                self.graph.add_edge(name, per, color='blue', title='permissions')
                                        if user:
                                                self.graph.add_edge(user, per, color='blue', title='permissions')
                        if 'userAccountControl' in entry:
                                ps = entry.userAccountControl.values
                                
                                for p in ps:
                                        self.graph.add_node(p, color='lime', title=f'Account Control: {p}')
                                        if user:
                                                self.graph.add_edge(user, p, color='lime', title='control')
                                        if group:
                                                self.graph.add_edge(group, p, color='lime', title='control')
                                        if dn:
                                                self.graph.add_edge(dn, p, color='lime', title='control')
                        # if 'userRights' in entry:
                        #         rights = entry.userRights.values
                        #         for right in rights:
                        #                 if dn:
                        #                         self.graph.add_edge(dn, right, color='yellow')
                        
                        if dn.startswith('OU='):
                                self.get_objs()
        
        
        def convert_graph(self):
                """ saves all the data collected after running and outputs graphtml file that can be read with matplotlib or pyvis.network and outputs html file that can be viewed in browser """
                #nx.write_graphml(self.graph, f'{self.domain}-graphx.graphtml')
                net = Network(notebook=True,height='82.8vh', bgcolor="#000000", font_color="#ffffff", filter_menu=True, directed=True, select_menu=True, neighborhood_highlight=True)
                net.from_nx(self.graph)
                net.toggle_hide_nodes_on_drag(True)
                
                net.show(f'{self.domain}.html')





        


def collect(domain_controller_ip,username,domain, password=None, nthash='', lmhash=''):
        mapps  = ADMap(domain_ip=domain_controller_ip, username=username, password=password, domain=domain)
        mapps.get_objs()
        mapps.convert_graph()
        

if __name__ == '__main__':
        try:
                op = sys.argv[1]
                mapps = ADMap(username='s.blade', domain='coder.htb', password='AmcwNO60Zg3vca3o0HDrTC6D', domain_ip='10.10.11.207')
                mapps.print_objs()
                
        except Exception as e:
                #print(e)
                collect(domain_controller_ip='10.10.11.207', domain='coder.htb', username='s.blade', password='AmcwNO60Zg3vca3o0HDrTC6D')
        