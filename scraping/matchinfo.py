import os
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

# Fonction pour nettoyer le texte
def clean_text(raw_text):
    return " ".join(raw_text.split())  # Supprime les espaces multiples


# Fonction principale pour extraire le texte, les images et les métadonnées
def scrape_page(url, image_save_dir):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Erreur: Impossible d'accéder à {url}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraire le titre de la page
        title = soup.title.string if soup.title else "Titre non disponible"

        # Extraire le texte
        raw_text = soup.get_text()
        cleaned_text = clean_text(raw_text)

        # Structurer les données collectées
        page_data = {
            "url": url,
            "title": title,
            "text": cleaned_text
        }
        return page_data

    except Exception as e:
        print(f"Erreur lors du scraping de {url}: {e}")
        return None


# Fonction pour scraper plusieurs pages
def scrape_multiple_pages(urls, output_file, image_save_dir="images"):
    all_data = []
    for url in urls:
        print(f"Scraping {url}...")
        page_data = scrape_page(url, image_save_dir)
        if page_data:
            all_data.append(page_data)

    # Sauvegarder les données dans un fichier JSON
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(all_data, json_file, indent=4, ensure_ascii=False)
    print(f"Données sauvegardées dans {output_file}")


# Liste des URLs à scraper
urls_to_scrape = [
    "https://www.cafonline.com/caf-africa-cup-of-nations/news/totalenergies-afcon-2025-in-morocco-everything-you-need-to-know/",
    "https://www.forbes.com/sites/sindiswamabunda/2024/11/20/afcon-2025-the-road-to-morocco-begins-as-24-teams-confirmed-for-africas-biggest-football-tournament/"
]

# Dossier pour enregistrer les images
image_directory = "./img"

# Fichier de sortie JSON
output_json_file = "../data_js/matchInfoma.json"

# Lancer le scraping
scrape_multiple_pages(urls_to_scrape, output_json_file, image_directory)
