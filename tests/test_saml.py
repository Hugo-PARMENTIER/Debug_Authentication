import pytest
import base64
from utils.saml_utils import decode_saml_response, parse_saml_xml, get_mock_saml_response

def test_get_mock_saml_response():
    saml_b64 = get_mock_saml_response()
    assert isinstance(saml_b64, str)
    # Check if it's base64
    decoded = base64.b64decode(saml_b64)
    assert b'samlp:Response' in decoded

def test_parse_saml_xml():
    saml_b64 = get_mock_saml_response()
    xml_string = decode_saml_response(saml_b64)
    parsed_data = parse_saml_xml(xml_string)
    
    assert parsed_data['issuer'] == 'http://www.okta.com/mock-idp'
    assert parsed_data['name_id'] == 'mock.user@example.com'
    assert parsed_data['attributes']['firstName'] == 'Mock'
    assert 'Admin' in parsed_data['attributes']['groups']
    assert 'Developer' in parsed_data['attributes']['groups']
