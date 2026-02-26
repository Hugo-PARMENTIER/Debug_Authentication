import pytest
from utils.token_utils import parse_id_token, get_mock_oidc_token

def test_get_mock_oidc_token():
    token = get_mock_oidc_token()
    assert isinstance(token, str)
    assert len(token.split('.')) == 3

def test_parse_id_token():
    token = get_mock_oidc_token()
    header, payload = parse_id_token(token)
    
    assert header['alg'] == 'RS256'
    assert payload['sub'] == 'mock_user_123'
    assert payload['email'] == 'jean.dupont@mock.com'
    assert 'groups' in payload
    assert 'Admins' in payload['groups']
