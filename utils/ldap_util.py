from ldap3 import Server, Connection, ALL, SUBTREE


class LdapUtils:
    def __init__(self):
        self.server_address = 'ldap://172.16.0.7'
        self.ldap_username = 'joinad@lvivkholod.int'
        self.ldap_password = 'Qq123456'
        self.base_dn = 'OU=LKHUsers,DC=lvivkholod,DC=int'
        self.base_dn_rk = 'OU=Rukavichky,DC=lvivkholod,DC=int'
        self.server = Server(self.server_address, get_info=ALL)
        self.conn = Connection(self.server, user=self.ldap_username, password=self.ldap_password, auto_bind=True)

    def __enter__(self):
        self.server = Server(self.server_address, get_info=ALL)
        self.conn = Connection(self.server, user=self.ldap_username, password=self.ldap_password, auto_bind=True)
        return self
 
    def __exit__(self, *args):
        self.conn.unbind()
        
    def get_sips_by_email(self,email):
        """Search sips by email of user"""
        search_filter = f'(mail={email})'
        self.conn.search(search_base=self.base_dn, search_filter=search_filter, attributes=['ipPhone'])

        sips = []
        for entry in self.conn.entries:
            if 'ipPhone' in entry:
                sips.extend(entry['ipPhone'].value.split(','))

        sips = [sip.strip() for sip in sips if sip]
        sips.sort()
        return sips
    
    def _get_all_sip(self):
        search_filter = f'(ipPhone=*)'
        self.conn.search(search_base=self.base_dn, search_filter=search_filter, attributes=['ipPhone', 'sAMAccountName'])
        result = []
        for entry in self.conn.entries:
            result.append(
                {"mail": entry.sAMAccountName.value,
                 "sips": entry.ipPhone.value.split(',')
                 }
            )
        print(result)
        return result

    def get_email_by_sip(self, sip):

        for tmp in self._get_all_sip():
            if sip in tmp["sips"]:
                return tmp['mail'] + "@lvivkholod.com"  
        return None
        
    def clouse(self):
        self.conn.unbind()

    def authenticate_user(self,username, password):
        server = Server(self.server_address, get_info=ALL)
        conn = Connection(server, user=username, password=password)
        if username == '' or password == '':
            return False
        
        if conn.bind():
            conn.unbind()
            return True
        else:
            conn.unbind()
            return False
        
    def get_shops_ad(self):
        search_filter = '(title=Директор магазину)'
        attributes = ['displayName', 'sAMAccountName', 'description', 'department']

        self.conn.search(self.base_dn_rk, search_filter, SUBTREE, attributes=attributes)

        director_info = []

        for entry in self.conn.entries:
            email = entry['sAMAccountName'].value + "@lvivkholod.com"
            if 'department' in entry and entry['department']:
                director_info.append({
                    "id_shop": int(entry['department'][0]),
                    "email": email
                })



        return director_info
