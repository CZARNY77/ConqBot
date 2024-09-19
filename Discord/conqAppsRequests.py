import requests
import os
import json

class conqSite:
    def __init__(self) -> None:
        self.headers = {'discord-key': f"{os.getenv('SITE_KEY')}"}

    #--------------------GET-------------------------
    def whitelist(self):
        with open('Discord/Keys/config.json', 'r') as file:
            url = json.load(file)["kop_whitelist"]
        response = requests.get(url, headers=self.headers)
        response.raise_for_status() 
        data = response.json()
        return data
    
    def surveys(self, house):
        with open('Discord/Keys/config.json', 'r') as file:
            url = json.load(file)["kop_survey"]
        url += f"?house={house}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status() 
        data = response.json()
        return data
    
    def config(self, house_id):
        with open('Discord/Keys/config.json', 'r') as file:
            url = json.load(file)["kop_config"]
        url += f"?house={house_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status() 
        data = response.json()
        return data
    
    def singup(self):
        with open('Discord/Keys/config.json', 'r') as file:
            url = json.load(file)["kop_singup"]
        response = requests.get(url, headers=self.headers)
        response.raise_for_status() 
        data = response.json()
        return data
    
    def users(self):
        with open('Discord/Keys/config.json', 'r') as file:
            url = json.load(file)["kop_users"]
        response = requests.get(url, headers=self.headers)
        response.raise_for_status() 
        data = response.json()
        return data
    
    def roles(self):
        with open('Discord/Keys/config.json', 'r') as file:
            url = json.load(file)["kop_roles"]
        response = requests.get(url, headers=self.headers)
        response.raise_for_status() 
        data = response.json()
        return data
    
    #------------------POST-----------------------
    def post_surveys(self, house, row):
        with open('Discord/Keys/config.json', 'r') as file:
            url = json.load(file)["kop_survey"]
        url += f"?house={house}"
        response = requests.post(url, json=row, headers=self.headers)
        if response.status_code == 200 or response.status_code == 201:
            print(f"{row['inGameNick']} został dodany do rodu {house}!")
        else:
            print(f"Błąd podczas wysyłania formularza: {response.status_code}, {response.text}")

    def post_whitelist(self, id, house):
        with open('Discord/Keys/config.json', 'r') as file:
            url = json.load(file)["kop_whitelist"]
        data = {
            "idDiscord": str(id),
            "house": str(house)
        }
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()