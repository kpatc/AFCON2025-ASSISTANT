import json
import requests
import re
import os
import pandas as pd
from typing import Optional, Dict, List, Any
from langchain_core.tools import Tool
from langchain.tools import tool
from markdownify import markdownify
from serpapi import GoogleSearch
from datetime import datetime
from functools import lru_cache
from langchain.agents import Tool
from langchain.chains import LLMChain

class FinalAnswerException(Exception):
    """Exception personnalisée pour gérer la réponse finale"""
    pass

class QueryClassifier:
    """Classifie les requêtes pour utiliser les outils appropriés"""
    
    CATEGORIES = {
        'match': r'\b(match|game|fixture|schedule|stadium)\b',
        'accommodation': r'\b(hotel|hostel|room|stay|accommodation)\b',
        'restaurant': r'\b(restaurant|food|eat|dining)\b',
        'health': r'\b(hospital|pharmacy|doctor|medical|health)\b',
        'transport': r'\b(transport|bus|train|taxi|direction|travel)\b',
        'weather': r'\b(weather|temperature|rain|forecast)\b',
        'general': r'\b(morocco|afcon|can|tourism|visit)\b'
    }
    
    @staticmethod
    def classify_query(query: str) -> List[str]:
        """Retourne les catégories pertinentes pour une requête"""
        query = query.lower()
        categories = []
        
        for category, pattern in QueryClassifier.CATEGORIES.items():
            if re.search(pattern, query):
                categories.append(category)
        
        return categories or ['general']

def create_search_all_sources(qa_chain):
    """Créer une fonction de recherche combinée"""
    def search_all_sources(query: str) -> str:
        categories = QueryClassifier.classify_query(query)
        results = []
        
        # Rechercher dans la base de connaissances selon les catégories
        for category in categories:
            try:
                result = qa_chain.run(f"[{category}] {query}")
                results.append(result)
            except Exception as e:
                print(f"Erreur lors de la recherche dans {category}: {str(e)}")
        
        return "\n\n".join(results) if results else "Aucune information trouvée."
    
    return search_all_sources

@tool
def final_answer(response: str) -> str:
    """Format and return the final response."""
    try:
        # Clean and structure the response
        content_parts = []
        for line in response.split('\n'):
            if not line.startswith(('Action:', 'Action Input:', 'Thought:', '>', 'Invalid Format:')):
                content_parts.append(line)
        
        clean_response = '\n'.join(line for line in content_parts if line.strip())
        
        # Add contextual emojis
        if not any(emoji in clean_response for emoji in ['👋', '🇲🇦', '⚽', '🏆', '🏟️', '🏨', '🌤️']):
            if any(term in clean_response.lower() for term in ['bonjour', 'hi', 'hello', 'salam']):
                clean_response = f"👋 {clean_response}"
            elif any(term in clean_response.lower() for term in ['météo', 'temps', 'weather']):
                clean_response = f"🌤️ {clean_response}"
            elif any(term in clean_response.lower() for term in ['hotel', 'logement', 'hébergement']):
                clean_response = f"🏨 {clean_response}"
            elif any(term in clean_response.lower() for term in ['monument', 'visite', 'tourisme']):
                clean_response = f"🏛️ {clean_response}"
            elif 'can' in clean_response.lower() or 'afcon' in clean_response.lower():
                clean_response = f"🏆 {clean_response}"
            else:
                clean_response = f"🇲🇦 {clean_response}"
        
        # Structure the response for frontend
        formatted_response = {
            "content": clean_response,
            "type": "text"
        }
        
        raise FinalAnswerException(json.dumps(formatted_response))
        
    except Exception as e:
        if isinstance(e, FinalAnswerException):
            raise e
        return str(e)

@lru_cache(maxsize=50)
def visit_webpage_tool(url: str) -> str:
    """Cache webpage visits to improve performance"""
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        markdown_content = markdownify(response.text).strip()
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
        if len(markdown_content) > 10000:
            markdown_content = markdown_content[:10000] + "\n\n...[truncated]"
        return markdown_content
    except requests.exceptions.Timeout:
        return "The request timed out. Please try again later or check the URL."
    except requests.exceptions.RequestException as e:
        return f"Error fetching the webpage: {str(e)}"

@lru_cache(maxsize=100)
def web_search(query: str) -> str:
    """Cache web search results to improve performance"""
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "Error: SERPAPI_API_KEY not found in environment variables"
        
        search = GoogleSearch({
            "q": query,
            "api_key": api_key
        })
        
        results = search.get_dict()
        
        if "error" in results:
            return f"Search error: {results['error']}"
            
        # Format organic results
        if "organic_results" in results:
            formatted_results = []
            for result in results["organic_results"][:3]:  # Get top 3 results
                title = result.get("title", "No title")
                snippet = result.get("snippet", "No description")
                link = result.get("link", "")
                formatted_results.append(f"{title}\n{snippet}\nSource: {link}\n")
            
            return "\n".join(formatted_results)
        else:
            return "No results found"
            
    except Exception as e:
        return f"Error performing web search: {str(e)}"

@tool
def get_weather(city: str, forecast: bool = False) -> str:
    """Get current weather or forecast for a city using OpenMeteo API."""
    try:
        # First, we need to get coordinates for the city using Nominatim
        geocoding_url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json&limit=1"
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Weather Bot/1.0)'
        }
        
        location_response = requests.get(geocoding_url, headers=headers)
        location_response.raise_for_status()
        location_data = location_response.json()
        
        if not location_data:
            return f"Désolé, je ne trouve pas la ville {city}"
            
        lat = location_data[0]['lat']
        lon = location_data[0]['lon']
        city_name = location_data[0].get('display_name', city).split(',')[0]
        
        # Base URL for OpenMeteo API
        base_url = "https://api.open-meteo.com/v1"
        
        if forecast:
            # Get 5-day forecast
            weather_url = f"{base_url}/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_mean,weathercode&timezone=auto"
            weather_response = requests.get(weather_url)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            
            # Weather code mapping
            weather_codes = {
                0: "Ciel dégagé ☀️",
                1: "Partiellement nuageux 🌤️",
                2: "Nuageux ⛅",
                3: "Couvert ☁️",
                45: "Brumeux 🌫️",
                48: "Brouillard givrant 🌫️",
                51: "Bruine légère 🌧️",
                53: "Bruine modérée 🌧️",
                55: "Bruine dense 🌧️",
                61: "Pluie légère 🌧️",
                63: "Pluie modérée 🌧️",
                65: "Pluie forte 🌧️",
                71: "Neige légère 🌨️",
                73: "Neige modérée 🌨️",
                75: "Neige forte 🌨️",
                77: "Grains de neige 🌨️",
                80: "Averses légères 🌦️",
                81: "Averses modérées 🌦️",
                82: "Averses violentes 🌦️",
                95: "Orage ⛈️"
            }
            
            # Format forecast data
            forecast_info = []
            dates = weather_data['daily']['time']
            max_temps = weather_data['daily']['temperature_2m_max']
            min_temps = weather_data['daily']['temperature_2m_min']
            precip_prob = weather_data['daily']['precipitation_probability_mean']
            weather_codes_data = weather_data['daily']['weathercode']
            
            for i in range(5):  # 5 days forecast
                date = datetime.strptime(dates[i], "%Y-%m-%d").strftime("%d/%m/%Y")
                weather_desc = weather_codes.get(weather_codes_data[i], "Conditions inconnues")
                forecast_info.append(
                    f"🗓️ {date}: {min_temps[i]}°C à {max_temps[i]}°C - {weather_desc} - "
                    f"Probabilité de précipitation: {precip_prob[i]}%"
                )
            
            return "\n".join([
                f"🌤️ Prévisions météo pour {city_name}:",
                *forecast_info
            ])
        else:
            # Get current weather
            weather_url = f"{base_url}/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
            weather_response = requests.get(weather_url)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            
            current = weather_data['current_weather']
            temp = current['temperature']
            windspeed = current['windspeed']
            
            # Get weather description based on weathercode
            weather_desc = {
                0: "Ciel dégagé ☀️",
                1: "Partiellement nuageux 🌤️",
                2: "Nuageux ⛅",
                3: "Couvert ☁️",
                45: "Brumeux 🌫️",
                48: "Brouillard givrant 🌫️",
                51: "Bruine légère 🌧️",
                53: "Bruine modérée 🌧️",
                55: "Bruine dense 🌧️",
                61: "Pluie légère 🌧️",
                63: "Pluie modérée 🌧️",
                65: "Pluie forte 🌧️",
                71: "Neige légère 🌨️",
                73: "Neige modérée 🌨️",
                75: "Neige forte 🌨️",
                77: "Grains de neige 🌨️",
                80: "Averses légères 🌦️",
                81: "Averses modérées 🌦️",
                82: "Averses violentes 🌦️",
                95: "Orage ⛈️"
            }.get(current['weathercode'], "Conditions inconnues")
            
            return "\n".join([
                f"🌤️ Météo actuelle à {city_name}:",
                f"Température: {temp}°C",
                f"Vitesse du vent: {windspeed} km/h",
                f"Conditions: {weather_desc}"
            ])
            
    except requests.exceptions.RequestException as e:
        return f"Erreur lors de la récupération des données météo: {str(e)}"

def extract_terminal_blocks(terminal_output: str) -> Dict[str, List[str]]:
    """Extrait les différents blocs d'information du terminal output."""
    blocks = {
        "greeting": None,  # Pour stocker la première salutation
        "database_info": [],
        "web_info": [],
        "additional_info": [],
        "final_answer": []
    }
    
    current_block = None
    content_buffer = []
    greeting_found = False
    
    # Liste des phrases de salutation connues
    greeting_phrases = [
        "Hello!", "I'm ready", "Ready to help",
        "How can I assist", "Let me help",
        "Welcome", "I can help you with"
    ]
    
    for line in terminal_output.split('\n'):
        line = line.strip()
        
        # Ignorer les lignes d'avertissement et techniques
        if any(marker in line for marker in [
            "> Entering new", "> Finished", "Invalid Format:", 
            "Action Input:", "Thought:", "INFO:", "WARNING:",
            "LangChainDeprecationWarning", "warn_deprecated"
        ]):
            continue
            
        # Capturer la première salutation
        if not greeting_found and any(phrase in line for phrase in greeting_phrases):
            blocks["greeting"] = line
            greeting_found = True
            continue
            
        # Identifier le début des blocs
        if "Information from Database:" in line:
            if current_block and content_buffer:
                blocks[current_block].extend(content_buffer)
            current_block = "database_info"
            content_buffer = []
            continue
        elif "Information from Web:" in line:
            if current_block and content_buffer:
                blocks[current_block].extend(content_buffer)
            current_block = "web_info"
            content_buffer = []
            continue
        elif "Action: Final Answer" in line:
            if current_block and content_buffer:
                blocks[current_block].extend(content_buffer)
            current_block = "final_answer"
            content_buffer = []
            continue
        elif any(marker in line for marker in [
            "Based on my research",
            "Voici les informations",
            "Additional information",
            "Here's what I found"
        ]):
            if current_block and content_buffer:
                blocks[current_block].extend(content_buffer)
            current_block = "additional_info"
            content_buffer = []
            continue
            
        # Ajouter le contenu au buffer du bloc actuel
        if current_block and line and not line.startswith(("Action:", "I'm ready", "Please provide")):
            content_buffer.append(line)
    
    # Ajouter le dernier buffer
    if current_block and content_buffer:
        blocks[current_block].extend(content_buffer)
    
    return blocks

def format_response_from_blocks(blocks: Dict[str, List[str]]) -> str:
    """Formate une réponse cohérente à partir des blocs d'information."""
    response_parts = []
    
    # Ajouter la salutation si elle existe
    if blocks["greeting"]:
        response_parts.append(blocks["greeting"])
    
    # Formatter le contenu principal
    main_content = []
    if blocks["final_answer"]:
        main_content.extend([line for line in blocks["final_answer"] 
                           if not any(phrase in line for phrase in ["I'm ready", "Please provide"])])
    elif blocks["additional_info"]:
        main_content.extend(blocks["additional_info"])
    
    if not main_content and (blocks["database_info"] or blocks["web_info"]):
        if blocks["database_info"]:
            relevant_info = [line for line in blocks["database_info"] 
                           if not line.startswith("I'm ready") 
                           and not line.startswith("Please provide")]
            if relevant_info:
                main_content.extend(relevant_info)
        
        if blocks["web_info"]:
            relevant_info = [line for line in blocks["web_info"] 
                           if line != "No results found" 
                           and not line.startswith("Error")]
            if relevant_info:
                main_content.extend(relevant_info)
    
    # Nettoyer et formater la réponse
    if main_content:
        response = "\n".join(main_content)
        
        # Nettoyer les marqueurs techniques restants
        response = re.sub(r'```[^`]*```', '', response)
        response = re.sub(r'Source: http[s]?://\S+', '', response)
        response = re.sub(r'I\'m ready.*', '', response)
        response = re.sub(r'Please provide.*', '', response)
        
        # Ajouter des emojis appropriés si nécessaire
        if not any(emoji in response for emoji in ['👋', '🇲🇦', '⚽', '🏆']):
            if any(word in response.lower() for word in ['bonjour', 'hi', 'hello', 'salam']):
                response = f"👋 {response}"
            elif any(word in response.lower() for word in ['hotel', 'logement']):
                response = f"🏨 {response}"
            elif any(word in response.lower() for word in ['stade', 'ville']):
                response = f"🏟️ {response}"
            else:
                response = f"🇲🇦 {response}"
        
        response_parts.append(response.strip())
    else:
        response_parts.append("👋 Je suis là pour vous aider avec la CAN 2025 au Maroc. Que voulez-vous savoir ?")
    
    # Retourner la réponse finale nettoyée
    final_response = " ".join(response_parts).strip()
    final_response = re.sub(r'\s+', ' ', final_response)  # Nettoyer les espaces multiples
    return final_response

@tool
def process_terminal_output(terminal_output: str) -> str:
    """Traite la sortie du terminal pour extraire et formater une réponse cohérente."""
    try:
        # Extraire les blocs d'information
        blocks = extract_terminal_blocks(terminal_output)
        
        # Formater la réponse finale
        response = format_response_from_blocks(blocks)
        
        # Lever l'exception avec la réponse formatée
        raise FinalAnswerException(response)
        
    except Exception as e:
        if isinstance(e, FinalAnswerException):
            raise e
        return str(e)

def get_tools(qa_chain):
    """Return the list of all available tools in order of priority."""
    search_all_sources = create_search_all_sources(qa_chain)
    
    tools = [
        Tool(
            name="CAN Knowledge Base",
            func=qa_chain.run,
            description="PRIORITY 1: Use for specific information about AFCON 2025"
        ),
        Tool(
            name="Local Search",
            func=search_all_sources,
            description="PRIORITY 2: Search in the local database including hotels, restaurants, and medical facilities"
        ),
        Tool(
            name="Weather Info",
            func=get_weather,
            description="PRIORITY 3: Get current weather or forecast for Moroccan cities"
        ),
        Tool(
            name="Web Search",
            func=web_search,
            description="PRIORITY 4: Search for current information about Morocco and AFCON"
        ),
        Tool(
            name="Visit Webpage",
            func=visit_webpage_tool,
            description="PRIORITY 5: Explore relevant URLs found during search"
        ),
        Tool(
            name="Process Response",
            func=process_terminal_output,
            description="PRIORITY 6: Process and format responses from other tools"
        ),
        Tool(
            name="Final Answer",
            func=final_answer,
            description="PRIORITY 7: Format and structure the final response with appropriate context"
        )
    ]
    
    return tools
