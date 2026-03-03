Règles obligatoires OIDC :
- OKTA_ISSUER doit commencer par https://
- redirect_uri validé strictement (pas de wildcard *, pas de http)
- client_secret jamais hardcodé, logué ou commité
- Utiliser authlib avec authorize_redirect + token exchange + signature validation
- Pas d'appel httpx sans scheme explicite (http:// ou https://)
Action : commenter le code + proposer fix si violation