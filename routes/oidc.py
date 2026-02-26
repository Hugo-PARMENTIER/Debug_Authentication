from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import os
import json
from utils.token_utils import parse_id_token, get_mock_oidc_token

router = APIRouter()

@router.get("/login")
async def oidc_login(request: Request):
    """Initiates the OIDC Authorization Code Flow."""
    if os.getenv("MOCK_MODE", "false").lower() == "true":
         return RedirectResponse(url="/oidc/callback?mock=true")
         
    oauth = request.app.state.oauth
    if not oauth.okta:
        return request.app.state.templates.TemplateResponse(
             "error.html", {"request": request, "error": "Client OIDC Okta non configuré (vérifiez le .env)."}
        )
        
    redirect_uri = os.getenv("REDIRECT_URI")
    if not redirect_uri:
        redirect_uri = str(request.url_for('oidc_callback'))
        
    return await oauth.okta.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def oidc_callback(request: Request):
    """Handles the callback from Okta and exchanges the code for tokens."""
    is_mock = request.query_params.get('mock') == 'true' or os.getenv("MOCK_MODE", "false").lower() == "true"
    
    if is_mock:
        token_str = get_mock_oidc_token()
        token = {"id_token": token_str, "access_token": "mock_access_token"}
    else:
        try:
            oauth = request.app.state.oauth
            token = await oauth.okta.authorize_access_token(request)
        except Exception as e:
            return request.app.state.templates.TemplateResponse(
                "error.html", {"request": request, "error": f"Erreur d'autorisation OIDC: {e}"}
            )
            
    id_token = token.get('id_token')
    if not id_token:
         return request.app.state.templates.TemplateResponse(
                "error.html", {"request": request, "error": "Aucun ID Token retourné par l'Identity Provider."}
            )
            
    try:
        header, payload = parse_id_token(id_token)
        return request.app.state.templates.TemplateResponse(
            "results.html", {
                "request": request,
                "type": "OIDC",
                "raw_token": id_token,
                "header": header,
                "payload": payload,
                "header_json": json.dumps(header, indent=2),
                "payload_json": json.dumps(payload, indent=2)
            }
        )
    except Exception as e:
        return request.app.state.templates.TemplateResponse(
                "error.html", {"request": request, "error": f"Erreur de parsing du token: {e}"}
            )
