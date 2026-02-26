# Okta Debug Authentication App

Une application web complète et sécurisée permettant de déboguer les flux d'authentification Okta (OIDC Authorization Code Flow & SAML 2.0).
Développée avec **Python 3.12**, **FastAPI**, **Jinja2** et **Bootstrap 5**.

## Fonctionnalités

*   **OIDC (OpenID Connect)**: Flow *Authorization Code*. Affichage détaillé du token JWT brut, en-tête décodé, payload avec coloration syntaxique, tableau des claims et vérification de la signature.
*   **SAML 2.0**: Parse et affiche l'assertion SAML brute en XML formaté, ainsi que les informations extraites (Issuer, Subject NameID, Attributes, Conditions, Signature status).
*   **Sécurisé**: Les secrets ne sont jamais logués ni affichés au client. Utilisation d'une gestion stricte des variables d'environnement. CSRF basic via cookies/sessions.
*   **Responsive & Dark Mode**: Interface propre et moderne via Bootstrap 5 avec la possibilité de basculer en thème sombre.
*   **Mode Mock**: Possibilité de tester l'UI et les fonctionnalités hors connexion en générant des fausses données.

## Pré-requis système (pour développement local)

La librairie `python3-saml` requiert l'installation de dépendances C sur votre système d'exploitation pour compiler `xmlsec1`.

*   **Ubuntu/Debian**: `sudo apt-get install pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl`
*   **macOS**: `brew install libxmlsec1`
*   **Windows**: Il est très fortement recommandé d'utiliser Docker ou WSL2 pour exécuter l'application sous Windows, la compilation de `xmlsec1` natif y étant hasardeuse.

## Configuration Okta (Setup)

### 1. Création de l'application OIDC (OpenID Connect)
1. Allez dans *Applications* -> *Applications* -> *Create App Integration*.
2. Choisissez **OIDC - OpenID Connect** puis **Web Application**.
3. *Sign-in redirect URIs*: Ajoutez `http://localhost:8000/oidc/callback` (et l'URL de votre déploiement Render, ex: `https://votre-app.onrender.com/oidc/callback`).
4. *Sign-out redirect URIs*: Mettez `http://localhost:8000`.
5. *Assignments*: Assignez l'application à Vous-même ou un groupe (ex: Everyone).
6. Notez les **Client ID** et **Client Secret**.

### 2. Création de l'application SAML 2.0
1. Allez dans *Applications* -> *Applications* -> *Create App Integration*.
2. Choisissez **SAML 2.0**.
3. Dans *General Settings*, donnez un nom à l'App.
4. Dans *SAML Settings*:
   - *Single sign-on URL (ACS)*: `http://localhost:8000/saml/acs` (et ajoutez votre URL Render plus tard si besoin, ou utilisez une variable dynamique si Okta le permet).
   - *Audience URI (SP Entity ID)*: `okta-debug-auth-sp` (ou n'importe quel ID unique de votre choix, mais vous devrez configurer `python3-saml` en conséquence).
   - *Attribute Statements (Optional)*: Ajoutez quelques attributs pour le debug (ex: `firstName` -> `user.firstName`, `email` -> `user.email`).
5. Terminez et assignez.
6. Dans l'onglet *Sign On*, copiez le lien **Identity Provider metadata** (le lien vers le XML de métadonnées). Vous pourrez l'utiliser dans `OKTA_SAML_METADATA_XML`.

## Installation et Utilisation Locale

1. **Cloner le repo**
2. **Créer un environnement virtuel (optionnel mais recommandé)**: `python -m venv venv` puis `source venv/bin/activate`
3. **Installer les dépendances**: `pip install -r requirements.txt`
4. **Configurer l'environnement**: Copiez `.env.example` vers `.env` et remplissez vos informations Okta.
5. **Démarrer l'application**: `uvicorn main:app --reload`
6. Rendez-vous sur `http://localhost:8000`

## Déploiement Gratuit sur Render

L'application est configurée pour être déployée facilement via un container Docker sur (Render)[https://render.com].

1. Poussez votre code sur un repo GitHub public ou privé.
2. Créez un compte sur Render.com.
3. Allez dans le Dashboard, cliquez sur **New +** -> **Web Service**.
4. Connectez votre repository GitHub.
5. Choisissez le langage/type d'environnement : il devrait détecter le fichier `render.yaml` (Blueprint) ou vous pouvez choisir **Docker**.
6. Dans l'interface web de Render, allez dans les paramètres de votre service et remplissez les **Environment Variables**:
    - `OKTA_DOMAIN`
    - `OKTA_CLIENT_ID`
    - `OKTA_CLIENT_SECRET`
    - `OKTA_AUTH_SERVER_ID` (si Default Custom Auth server, sinon laissez vide ou 'default')
    - `OKTA_SAML_METADATA_XML`
    - *(La variable `SECRET_KEY` sera auto-générée par le render.yaml)*
7. Si vous utilisez Render, n'oubliez pas d'ajouter l'URL HTTPS finale (ex: `https://votre-app.onrender.com/oidc/callback`) dans les **Redirect URIs** de vos configurations Okta !

## Mode Mock

Si vous souhaitez tester l'UI sans contacter les serveurs Okta (pour voir le CSS/HTML localement), passez `MOCK_MODE=true` dans votre fichier `.env`. L'application simulera des échanges OIDC et SAML réussis avec de fausses informations.
