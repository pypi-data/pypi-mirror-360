import base64
import json
from .rest import request_with_retry, parallel_fetch

def get_access_token(client_id, client_secret):
    auth_string = f"{client_id}:{client_secret}"
    auth_base64 = base64.b64encode(auth_string.encode()).decode()
    
    url = "https://accounts.spotify.com/api/token"
    headers = {"Authorization": f"Basic {auth_base64}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
    response = request_with_retry('post', url, headers=headers, data=data)

    return response.get("access_token")

def get_token_pool(credentials):
    def _get_token(cred):
        return [token] if (token := get_access_token(*cred)) else []

    return parallel_fetch(_get_token, credentials)

def search(query, token, **kwargs):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, **kwargs}
    data = request_with_retry('get', url, headers=headers, params=params)
    
    return [json.dumps(item) for item in data.get(kwargs['type'] + 's', {}).get("items", [])]