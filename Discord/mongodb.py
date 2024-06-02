from pymongo import MongoClient
import json
# Ustawienie adresu URL połączenia. Jeśli korzystasz z MongoDB Atlas, możesz znaleźć ten URL w ustawieniach swojej bazy danych.
with open('Discord/Keys/config.json', 'r') as file:
    login = json.load(file)["mongodb"]
mongo_url = login  # Przykład lokalnego adresu URL. Zastąp odpowiednim URL, jeśli używasz MongoDB Atlas lub innego hosta.

# Utworzenie klienta MongoDB
client = MongoClient(mongo_url)

databases = client.list_database_names()
print("Bazy danych:")
for db_name in databases:
    print(f"- {db_name}")
    
    # Pobieranie wszystkich kolekcji z każdej bazy danych
    db = client[db_name]
    collections = db.list_collection_names()
    print(f"  Kolekcje w bazie danych '{db_name}':")
    for collection_name in collections:
        print(f"  - {collection_name}")

# Wybranie bazy danych (jeśli baza danych nie istnieje, zostanie utworzona)
db = client["TeamSorter"]
collection = db["user"]
# Wybranie kolekcji (jeśli kolekcja nie istnieje, zostanie utworzona)
# Przykładowe zapytanie do kolekcji
data = [
    {"id": 1, "name": "test1"},
    {"id": 2, "name": "test2"}
]
result = collection.insert_many(data)
print(f"Dokument dodany z id: {result.inserted_ids}")

query = {"id": 2}
document = collection.find_one(query)
print(document)

# Zamknięcie połączenia
client.close()