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
    "https://rabat.embassy.qa/en/kingdom-of-morocco/general-information",
    "https://rabat.embassy.qa/en/kingdom-of-morocco/foreigners-residence",
    "https://rabat.embassy.qa/en/kingdom-of-morocco/do-and-dont",
    "https://rabat.embassy.qa/en/kingdom-of-morocco/political-system",
    "https://rabat.embassy.qa/en/kingdom-of-morocco/tourism",
    "https://rabat.embassy.qa/en/kingdom-of-morocco/family-law",
    "https://rabat.embassy.qa/en/kingdom-of-morocco/important-phones",
    "https://rabat.embassy.qa/en/kingdom-of-morocco/faq"
]

# Dossier pour enregistrer les images
image_directory = "./img"

# Fichier de sortie JSON
output_json_file = "../data_js/generalInfoma.json"

# Lancer le scraping
scrape_multiple_pages(urls_to_scrape, output_json_file, image_directory)
