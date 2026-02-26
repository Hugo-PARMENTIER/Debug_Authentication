from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import os
import json
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from utils.saml_utils import decode_saml_response, parse_saml_xml, format_xml, get_mock_saml_response

router = APIRouter()

def prepare_saml_req(request: Request, form_data: dict = None):
    host = request.headers.get("x-forwarded-host", request.client.host)
    port = request.headers.get("x-forwarded-port", str(request.url.port))
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    return {
        'https': 'on' if scheme == 'https' else 'off',
        'http_host': host,
        'server_port': port,
        'script_name': request.url.path,
        'get_data': request.query_params,
        'post_data': form_data or {}
    }

def build_saml_settings(request: Request):
    sp_entity_id = "okta-debug-auth-sp"
    return {
        "strict": False,
        "debug": True,
        "sp": {
            "entityId": sp_entity_id,
            "assertionConsumerService": {
                "url": str(request.url_for('saml_acs')),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
        },
        "idp": getattr(request.app.state, 'saml_idp_settings', {})
    }

@router.get("/login")
async def saml_login(request: Request):
    """Initiates the SAML Login flow."""
    if os.getenv("MOCK_MODE", "false").lower() == "true":
         mock_assertion = get_mock_saml_response()
         html = f"""
         <html><body onload="document.forms[0].submit()">
            <form method="post" action="/saml/acs">
                <input type="hidden" name="SAMLResponse" value="{mock_assertion}"/>
                <input type="hidden" name="mock" value="true"/>
            </form>
         </body></html>
         """
         return HTMLResponse(content=html)
         
    req = prepare_saml_req(request)
    settings = build_saml_settings(request)
    
    if not settings.get('idp'):
         return request.app.state.templates.TemplateResponse(
                "error.html", {"request": request, "error": "IDP SAML non configuré. Assurez-vous d'avoir renseigné OKTA_SAML_METADATA_XML dans votre environnement."}
         )
         
    auth = OneLogin_Saml2_Auth(req, old_settings=settings)
    sso_built_url = auth.login()
    return RedirectResponse(url=sso_built_url)

@router.post("/acs")
async def saml_acs(request: Request):
    """Assertion Consumer Service: Receives and processes the SAML Response."""
    form_data = await request.form()
    is_mock = form_data.get('mock') == 'true' or os.getenv("MOCK_MODE", "false").lower() == "true"
    saml_response_b64 = form_data.get("SAMLResponse")
    
    if not saml_response_b64:
        return request.app.state.templates.TemplateResponse(
            "error.html", {"request": request, "error": "Aucune réponse SAML (SAMLResponse) trouvée dans la requête HTTP POST."}
        )

    try:
        xml_string = decode_saml_response(str(saml_response_b64))
        formatted_xml = format_xml(xml_string)
        parsed_data = parse_saml_xml(xml_string)
        
        validation_errors = []
        if not is_mock:
            req = prepare_saml_req(request, dict(form_data))
            settings = build_saml_settings(request)
            if settings.get('idp'):
                auth = OneLogin_Saml2_Auth(req, old_settings=settings)
                auth.process_response()
                errors = auth.get_errors()
                if errors:
                    validation_errors = errors
                    reason = auth.get_last_error_reason()
                    if reason:
                        validation_errors.append(reason)
            else:
                validation_errors.append("Le settings IDP SAML n'est pas configuré. La validation de la signature a été sautée.")
                    
        return request.app.state.templates.TemplateResponse(
            "results.html", {
                "request": request,
                "type": "SAML",
                "raw_xml": formatted_xml,
                "parsed_data": parsed_data,
                "parsed_data_json": json.dumps(parsed_data, indent=2, ensure_ascii=False),
                "validation_errors": validation_errors
            }
        )
            
    except Exception as e:
        return request.app.state.templates.TemplateResponse(
            "error.html", {"request": request, "error": f"Erreur lors du traitement de l'assertion SAML: {e}"}
        )
