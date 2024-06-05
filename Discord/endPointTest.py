import requests
import json

with open('Discord/Keys/config.json', 'r') as file:
    url = json.load(file)["kop_singup"]

data = {
    "_id": "665b944fd594e3847f2b80e9",
}

full_url = f"{url}/2024-06-01"

try:
    #response = requests.delete(full_url)
    #response.raise_for_status()

    response = requests.get(full_url)
    response.raise_for_status() 
    data = response.json()
    if data["signup"]:
        response = requests.delete(full_url)
        response.raise_for_status()
        print("usunięto")
    else:
        print("nie ma takiej daty")
    #response = requests.post(url, json=data)
    #response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    #print("Dane zostały pomyślnie wysłane")
    #print("Odpowiedź serwera:", response.json())
except requests.exceptions.HTTPError as e:
    print("Wystąpił błąd HTTP:", e)
    print("Treść odpowiedzi:", response.text)
except requests.exceptions.RequestException as e:
    print("Wystąpił błąd żądania:", e)