Règles SAML :
- Metadata URL ou XML inline commence par https://
- Parsing avec xmlsec + validation signature
- Pas de parsing unsafe (éviter xml.etree sans secure parser)
- Extraction sécurisée des attributs sensibles (groups, roles, custom claims)
Action : alerte + suggestion de fix