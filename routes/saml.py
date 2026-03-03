from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
from utils.saml_utils import decode_saml_response, parse_saml_xml, format_xml, get_mock_saml_response

router = APIRouter()

@router.get("/login")
async def saml_login(request: Request):
    """Initiates the SAML Login flow."""
    if os.getenv("MOCK_MODE", "false").lower() == "true":
        try:
            mock_assertion = get_mock_saml_response()
            xml_string = decode_saml_response(mock_assertion)
            formatted_xml = format_xml(xml_string)
            parsed_data = parse_saml_xml(xml_string)
            return JSONResponse({
                "type": "SAML",
                "raw_xml": formatted_xml,
                "parsed_data": parsed_data
            })
        except Exception as e:
            return JSONResponse({"type": "error", "message": f"Erreur lors du traitement de l'assertion SAML: {e}"}, status_code=500)

    # ... (le reste de la logique non-mock reste inchangée)
