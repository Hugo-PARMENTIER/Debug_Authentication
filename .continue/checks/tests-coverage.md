Règles tests :
- Minimum 80% coverage pytest sur flows OIDC/SAML
- Tester parsing claims / XML avec mock data
- Pas de test qui expose secrets ou données sensibles
Action : lancer pytest et commenter si <80% ou si fail