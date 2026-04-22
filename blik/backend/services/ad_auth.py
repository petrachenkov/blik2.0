import ldap3
from ldap3 import Server, Connection, ALL, NTLM
from backend.config.settings import settings


class ADAuthService:
    """Active Directory Authentication Service"""
    
    def __init__(self):
        self.server = settings.AD_SERVER
        self.base_dn = settings.AD_BASE_DN
        self.bind_dn = settings.AD_BIND_DN
        self.bind_password = settings.AD_BIND_PASSWORD
        self.search_filter = settings.AD_USER_SEARCH_FILTER
    
    def authenticate(self, username: str, password: str) -> dict | None:
        """
        Authenticate user against Active Directory
        Returns user info if successful, None otherwise
        """
        try:
            server = Server(self.server, get_info=ALL)
            
            # Create connection with service account
            conn = Connection(
                server,
                user=self.bind_dn,
                password=self.bind_password,
                authentication=NTLM
            )
            
            if not conn.bind():
                return None
            
            # Search for user
            search_filter = self.search_filter.format(username=username)
            conn.search(
                search_base=self.base_dn,
                search_filter=search_filter,
                attributes=['sAMAccountName', 'cn', 'mail', 'department', 'displayName']
            )
            
            if len(conn.entries) == 0:
                return None
            
            user_entry = conn.entries[0]
            user_dn = user_entry.entry_dn
            
            # Try to bind with user credentials to verify password
            user_conn = Connection(
                server,
                user=user_dn,
                password=password,
                authentication=NTLM
            )
            
            if not user_conn.bind():
                return None
            
            user_conn.unbind()
            conn.unbind()
            
            # Return user information
            return {
                'username': str(user_entry.sAMAccountName),
                'full_name': str(user_entry.displayName or user_entry.cn),
                'email': str(user_entry.mail) if user_entry.mail else None,
                'department': str(user_entry.department) if user_entry.department else None,
            }
            
        except Exception as e:
            print(f"AD Authentication error: {e}")
            return None
    
    def get_user_info(self, username: str) -> dict | None:
        """Get user information from AD without authentication"""
        try:
            server = Server(self.server, get_info=ALL)
            
            conn = Connection(
                server,
                user=self.bind_dn,
                password=self.bind_password,
                authentication=NTLM
            )
            
            if not conn.bind():
                return None
            
            search_filter = self.search_filter.format(username=username)
            conn.search(
                search_base=self.base_dn,
                search_filter=search_filter,
                attributes=['sAMAccountName', 'cn', 'mail', 'department', 'displayName']
            )
            
            if len(conn.entries) == 0:
                return None
            
            user_entry = conn.entries[0]
            conn.unbind()
            
            return {
                'username': str(user_entry.sAMAccountName),
                'full_name': str(user_entry.displayName or user_entry.cn),
                'email': str(user_entry.mail) if user_entry.mail else None,
                'department': str(user_entry.department) if user_entry.department else None,
            }
            
        except Exception as e:
            print(f"AD Get User Info error: {e}")
            return None


ad_auth_service = ADAuthService()
