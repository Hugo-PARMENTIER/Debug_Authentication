from ldap3 import Server, Connection, MOCK_SYNC

def get_mock_ldap_connection() -> Connection:
    """
    Creates and returns a mock LDAP connection using ldap3's MOCK_SYNC strategy.
    Populates it with over 50 mock users. No real or sensitive data is used.
    """
    server = Server('my_fake_ldap_server')
    # Using MOCK_SYNC strategy to create an offline mock connection
    conn = Connection(server, client_strategy=MOCK_SYNC)
    conn.bind()

    # Add 55 mock users to ensure we have at least 50
    for i in range(1, 56):
        dn = f"uid=mockuser{i},ou=users,dc=example,dc=com"
        attributes = {
            "uid": [f"mockuser{i}"],
            "mail": [f"mockuser{i}@mock.local"],
            "memberOf": ["cn=mock_group,ou=groups,dc=example,dc=com"],
            "groups": ["mock_group", "mock_users"]
        }
        conn.strategy.add_entry(dn, attributes)
        
    return conn
