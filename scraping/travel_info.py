import requests
from bs4 import BeautifulSoup
import json

# URL de la page web
url = "https://www.visitmorocco.com/en/useful-information"

# Envoyer une requête GET
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Trouver les conteneurs des informations
data = []
bubbles = soup.find_all('div', class_='wrap')

for bubble in bubbles:
    title = bubble.find('span')  # Les titres semblent être dans des balises <h3>
    content = bubble.find('p')  # Les descriptions semblent être dans des balises <p>

    if title and content:
        data.append({
            "title": title.get_text(strip=True),
            "text": content.get_text(strip=True)
        })

# Sauvegarder les données en JSON
with open('../data_js/travelInfo.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Données sauvegardées dans 'travelInfo.json'.")
