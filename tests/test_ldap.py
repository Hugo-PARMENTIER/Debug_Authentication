from utils.ldap_utils import get_mock_ldap_connection
from ldap3 import SUBTREE

def test_mock_ldap_users():
    conn = get_mock_ldap_connection()
    
    # Search all users
    conn.search(
        search_base='ou=users,dc=example,dc=com',
        search_filter='(uid=*)',
        search_scope=SUBTREE,
        attributes=['uid', 'mail', 'memberOf', 'groups']
    )
    
    # Verify at least 50 users
    assert len(conn.entries) >= 50
    
    # Verify attributes and absence of real/sensitive data
    for entry in conn.entries:
        # Check that required attributes exist
        assert entry.uid
        assert entry.mail
        assert entry.memberOf
        assert entry.groups
        
        uid_val = str(entry.uid.value)
        mail_val = str(entry.mail.value)
        
        # Check that it uses the expected fake pattern
        assert uid_val.startswith("mockuser")
        assert mail_val.endswith("@mock.local")
        
        # Ensure no real or sensitive data patterns are present
        assert "gmail" not in mail_val.lower()
        assert "password" not in str(entry.entry_to_json()).lower()
        assert "secret" not in str(entry.entry_to_json()).lower()
