import base64
from lxml import etree
from bs4 import BeautifulSoup
from typing import Dict, Any

def decode_saml_response(saml_response_b64: str) -> str:
    """Decodes a base64 encoded SAMLResponse to a string (XML)."""
    try:
        decoded_bytes = base64.b64decode(saml_response_b64)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to decode SAML Response: {e}")

def parse_saml_xml(xml_string: str) -> Dict[str, Any]:
    """Parses SAML XML to extract useful information for debugging."""
    try:
        # Use lxml for robust parsing with namespaces
        root = etree.fromstring(xml_string.encode('utf-8'))
        
        # Define common SAML namespaces
        namespaces = {
            'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
            'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
            'ds': 'http://www.w3.org/2000/09/xmldsig#'
        }

        result = {
            "issuer": None,
            "name_id": None,
            "attributes": {},
            "status_code": None,
            "destination": root.get('Destination'),
            "id": root.get('ID'),
            "in_response_to": root.get('InResponseTo'),
            "issue_instant": root.get('IssueInstant')
        }

        # Status Code
        status_code_el = root.find('.//samlp:StatusCode', namespaces)
        if status_code_el is not None:
            result['status_code'] = status_code_el.get('Value')

        # Issuer (from Response or Assertion)
        issuer_el = root.find('.//saml:Issuer', namespaces)
        if issuer_el is not None:
            result['issuer'] = issuer_el.text

        # Assertion
        assertion_el = root.find('.//saml:Assertion', namespaces)
        if assertion_el is not None:
            # Subject NameID
            name_id_el = assertion_el.find('.//saml:Subject/saml:NameID', namespaces)
            if name_id_el is not None:
                result['name_id'] = name_id_el.text

            # Attributes
            for attr in assertion_el.findall('.//saml:AttributeStatement/saml:Attribute', namespaces):
                attr_name = attr.get('Name')
                attr_values = [v.text for v in attr.findall('saml:AttributeValue', namespaces)]
                
                # Exclude None values and strip texts
                attr_values = [v.strip() for v in attr_values if v is not None]

                if len(attr_values) == 1:
                    result['attributes'][attr_name] = attr_values[0]
                elif len(attr_values) > 1:
                    result['attributes'][attr_name] = attr_values
                else:
                    result['attributes'][attr_name] = None
                    
        return result
    except Exception as e:
        return {"error": f"Failed to parse XML: {e}"}

def format_xml(xml_string: str) -> str:
    """Formats XML string for pretty printing with indentations."""
    try:
        soup = BeautifulSoup(xml_string, 'xml')
        return soup.prettify()
    except:
        return xml_string

def get_mock_saml_response() -> str:
    """Generates a base64 encoded mock SAML Response."""
    mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="id-mock-123" InResponseTo="id-req-456" Version="2.0" IssueInstant="2024-01-01T12:00:00Z" Destination="http://localhost:8000/saml/acs">
    <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">http://www.okta.com/mock-idp</saml:Issuer>
    <samlp:Status>
        <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
    </samlp:Status>
    <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="id-assertion-mock-123" IssueInstant="2024-01-01T12:00:00Z" Version="2.0">
        <saml:Issuer>http://www.okta.com/mock-idp</saml:Issuer>
        <saml:Subject>
            <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified">mock.user@example.com</saml:NameID>
            <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
                <saml:SubjectConfirmationData InResponseTo="id-req-456" NotOnOrAfter="2024-01-01T12:05:00Z" Recipient="http://localhost:8000/saml/acs"/>
            </saml:SubjectConfirmation>
        </saml:Subject>
        <saml:Conditions NotBefore="2024-01-01T11:55:00Z" NotOnOrAfter="2024-01-01T12:05:00Z">
            <saml:AudienceRestriction>
                <saml:Audience>mock-audience-uri</saml:Audience>
            </saml:AudienceRestriction>
        </saml:Conditions>
        <saml:AuthnStatement AuthnInstant="2024-01-01T12:00:00Z" SessionIndex="id-session-mock-123">
            <saml:AuthnContext>
                <saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport</saml:AuthnContextClassRef>
            </saml:AuthnContext>
        </saml:AuthnStatement>
        <saml:AttributeStatement>
            <saml:Attribute Name="firstName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified">
                <saml:AttributeValue>Mock</saml:AttributeValue>
            </saml:Attribute>
            <saml:Attribute Name="lastName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified">
                <saml:AttributeValue>User</saml:AttributeValue>
            </saml:Attribute>
            <saml:Attribute Name="email" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified">
                <saml:AttributeValue>mock.user@example.com</saml:AttributeValue>
            </saml:Attribute>
            <saml:Attribute Name="groups" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:unspecified">
                <saml:AttributeValue>Admin</saml:AttributeValue>
                <saml:AttributeValue>Developer</saml:AttributeValue>
            </saml:Attribute>
        </saml:AttributeStatement>
    </saml:Assertion>
</samlp:Response>"""
    return base64.b64encode(mock_xml.encode('utf-8')).decode('utf-8')
