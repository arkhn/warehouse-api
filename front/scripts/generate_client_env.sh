#!/bin/sh


echo "REACT_APP_FHIR_API_URL=http://$IP/api
REACT_APP_CLIENT_ID=front-api
REACT_APP_CLIENT_SECRET=front-api
REACT_APP_AUTH_URL=http://$IP/hydra/oauth2/auth
REACT_APP_TOKEN_URL=http://$IP/hydra/oauth2/token
REACT_APP_REVOKE_URL=http://$IP/hydra/oauth2/revoke
REACT_APP_LOGOUT_URL=http://$IP/hydra/oauth2/sessions/logout
REACT_APP_LOGIN_REDIRECT_URL=http://$IP/front-api/
REACT_APP_LOGOUT_REDIRECT_URL=http://$IP/front-api/login
"