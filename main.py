from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
import os
from dotenv import load_dotenv

import routes.oidc
import routes.saml

# Tenter d'importer le parser SAML Okta si présent
try:
    from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser
except ImportError:
    OneLogin_Saml2_IdPMetadataParser = None

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

# --- Routes et Mounts ---
app.include_router(routes.oidc.router, prefix="/oidc", tags=["OIDC"])
app.include_router(routes.saml.router, prefix="/saml", tags=["SAML"])

# Monter le dossier static s'il existe (pour css, js)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home(request: Request):
    """Page d'accueil de l'application de debug."""
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "mock_mode": os.getenv("MOCK_MODE", "false").lower() == "true",
        "oidc_ready": bool(domain and client_id),
        "saml_ready": bool(saml_settings)
    })
