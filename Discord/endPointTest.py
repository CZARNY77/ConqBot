import requests

url = "https://cb-social.vercel.app/api/add-user"
data = {
    "message": "CZARNY"
}

response = requests.post(url, json=data)

if response.status_code == 200:
    print("Dane zostały pomyślnie wysłane")
    print("Odpowiedź serwera:", response.json())
else:
    print("Wystąpił błąd:", response.status_code)
    print("Treść odpowiedzi:", response.text)