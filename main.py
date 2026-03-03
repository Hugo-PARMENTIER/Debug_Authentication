from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import google.generativeai as genai

import routes.oidc
import routes.saml

# Tenter d'importer le parser SAML Okta si présent
try:
    from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser
except ImportError as e:
    OneLogin_Saml2_IdPMetadataParser = None
    print(f"Warning: OneLogin_Saml2_IdPMetadataParser could not be imported. This might be due to missing xmlsec dependencies. Error: {e}")

# Diagnostic supplémentaire pour python3-saml
try:
    import onelogin.saml2.auth
    print("SAML: OneLogin_Saml2_Auth imported successfully.")
except ImportError as e:
    print(f"CRITICAL: Failed to import python3-saml! Error: {e}")
    import traceback
    traceback.print_exc()

# Charger l'environnement
load_dotenv()

app = FastAPI(title="Okta Debug Auth App")

# Middleware pour les sessions (nécessaire pour Authlib OAuth / state CSRF)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "UNE-CLÉ-SECRÈTE-POUR-LE-DÉVELOPPEMENT-LOCAL")
)

# Configuration des templates Jinja2
# On s'assure de l'existence du dossier (utile si lancé et dossier pas encore créé)
os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")
app.state.templates = templates

# --- Configuration OIDC (Authlib) ---
oauth = OAuth()
domain = os.getenv("OKTA_DOMAIN", "")
auth_server = os.getenv("OKTA_AUTH_SERVER_ID", "default")
client_id = os.getenv("OKTA_CLIENT_ID", "")
client_secret = os.getenv("OKTA_CLIENT_SECRET", "")

if domain and client_id:
    # URL de découverte OpenID (Well-Known)
    if auth_server and auth_server.lower() != "default" and auth_server.lower() != "":
        server_metadata_url = f"{domain}/oauth2/{auth_server}/.well-known/openid-configuration"
    else:
        # Si c'est le 'default' de l'org ou vide
        if auth_server == "default":
             server_metadata_url = f"{domain}/oauth2/{auth_server}/.well-known/openid-configuration"
        else:
             server_metadata_url = f"{domain}/.well-known/openid-configuration"
             
    oauth.register(
        name='okta',
        server_metadata_url=server_metadata_url,
        client_id=client_id,
        client_secret=client_secret,
        client_kwargs={'scope': 'openid profile email groups'}
    )
app.state.oauth = oauth

# --- Configuration SAML (python3-saml) ---
saml_settings = {}
metadata_url = os.getenv("OKTA_SAML_METADATA_XML", "")
if metadata_url and OneLogin_Saml2_IdPMetadataParser:
    if metadata_url.startswith("http"):
        try:
            idp_data = OneLogin_Saml2_IdPMetadataParser.parse_remote(metadata_url)
            saml_settings = idp_data.get('idp', {})
            print("SAML IDP Metadata chargée depuis l'URL dynamique avec succès.")
        except Exception as e:
            print(f"Warning: Impossible de parser la metadata SAML URL: {e}")
    else:
        # Fichier local
        if os.path.exists(metadata_url):
            try:
                with open(metadata_url, "r", encoding="utf-8") as f:
                    xml_content = f.read()
                    idp_data = OneLogin_Saml2_IdPMetadataParser.parse(xml_content)
                    saml_settings = idp_data.get('idp', {})
                    print("SAML IDP Metadata chargée depuis le fichier local avec succès.")
            except Exception as e:
                print(f"Warning: Impossible de parser la metadata SAML Fichier: {e}")

app.state.saml_idp_settings = saml_settings

@app.post("/config")
async def update_config(request: Request, oidc_metadata_url: str = Form(None), saml_metadata_url: str = Form(None)):
    if oidc_metadata_url:
        request.session['oidc_metadata_url'] = oidc_metadata_url
    if saml_metadata_url:
        request.session['saml_metadata_url'] = saml_metadata_url
    return RedirectResponse(url="/", status_code=303)

# --- Routes et Mounts ---
app.include_router(routes.oidc.router, prefix="/oidc", tags=["OIDC"])
app.include_router(routes.saml.router, prefix="/saml", tags=["SAML"])

# Monter le dossier static s'il existe (pour css, js)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health():
    """Health check endpoint."""
    gemini_status = "Not available via API"
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            await model.count_tokens_async("")
            gemini_status = "Accessible"
        except Exception as e:
            gemini_status = f"Error: {e}"

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gemini_quotas": {
            "status": gemini_status,
            "documentation": "https://ai.google.dev/gemini-api/docs/rate-limits"
        }
    }

@app.get("/")
async def home(request: Request):
    """Page d'accueil de l'application de debug."""
    # Re-evaluate settings based on session
    oidc_ready = bool(request.session.get('oidc_metadata_url') or (os.getenv("OKTA_DOMAIN") and os.getenv("OKTA_CLIENT_ID")))
    saml_ready = bool(request.session.get('saml_metadata_url') or os.getenv("OKTA_SAML_METADATA_XML"))

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "mock_mode": os.getenv("MOCK_MODE", "false").lower() == "true",
        "oidc_ready": oidc_ready,
        "saml_ready": saml_ready
    })
