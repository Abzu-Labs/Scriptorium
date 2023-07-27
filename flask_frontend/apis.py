import requests
from config import API_URL

def signup(email, password):
    data = {'email': email, 'password': password}
    response = requests.post(f"{API_URL}/signup", json=data)
    return response.json()

def login(email, password):
    data = {'email': email, 'password': password}
    response = requests.post(f"{API_URL}/login", data=data)
    return response.json() 

def get_projects():
    headers = {'Authorization': f"Bearer {session['access_token']}"}
    response = requests.get(f"{API_URL}/projects", headers=headers)
    return response.json()

# other API helper functions