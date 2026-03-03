from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import os
from utils.token_utils import parse_id_token, get_mock_oidc_token

router = APIRouter()

@router.get("/login")
async def oidc_login(request: Request):
    """Initiates the OIDC Authorization Code Flow."""
    if os.getenv("MOCK_MODE", "false").lower() == "true":
        try:
            token_str = get_mock_oidc_token()
            header, payload = parse_id_token(token_str)
            return JSONResponse({
                "type": "OIDC",
                "raw_token": token_str,
                "header": header,
                "payload": payload,
            })
        except Exception as e:
            return JSONResponse({"type": "error", "message": f"Erreur de génération du token mock OIDC: {e}"}, status_code=500)
    
    oauth = request.app.state.oauth
    client_name = 'okta'
    
    oidc_metadata_url = request.session.get('oidc_metadata_url')
    if oidc_metadata_url:
        client_name = 'okta_dynamic'
        oauth.register(
            name=client_name,
            server_metadata_url=oidc_metadata_url,
            client_id=os.getenv("OKTA_CLIENT_ID"),
            client_secret=os.getenv("OKTA_CLIENT_SECRET"),
            client_kwargs={'scope': 'openid profile email groups'}
        )

    if not getattr(oauth, client_name):
        return JSONResponse({"type": "error", "message": "Client OIDC Okta non configuré."}, status_code=500)
        
    redirect_uri = os.getenv("REDIRECT_URI")
    if not redirect_uri:
        redirect_uri = str(request.url_for('oidc_callback'))
        
    response = await getattr(oauth, client_name).authorize_redirect(request, redirect_uri)
    return JSONResponse({'url': response.headers['location']})

@router.get("/callback")
async def oidc_callback(request: Request):
    """Handles the callback from Okta and exchanges the code for tokens."""
    try:
        oauth = request.app.state.oauth
        client_name = 'okta_dynamic' if 'oidc_metadata_url' in request.session else 'okta'
        token = await getattr(oauth, client_name).authorize_access_token(request)
    except Exception as e:
        return JSONResponse({"type": "error", "message": f"Erreur d'autorisation OIDC: {e}"}, status_code=500)
            
    id_token = token.get('id_token')
    if not id_token:
        return JSONResponse({"type": "error", "message": "Aucun ID Token retourné par l'Identity Provider."}, status_code=500)
            
    try:
        header, payload = parse_id_token(id_token)
        return JSONResponse({
            "type": "OIDC",
            "raw_token": id_token,
            "header": header,
            "payload": payload,
        })
    except Exception as e:
        return JSONResponse({"type": "error", "message": f"Erreur de parsing du token: {e}"}, status_code=500)
