import requests
from typing import Dict, Optional, List
import re

class TMDBApi:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
    
    def clean_filename(self, filename: str) -> str:
        """Clean filename to extract media title"""
        # Remove file extension
        filename = re.sub(r'\.[^.]*$', '', filename)
        
        # Remove common quality indicators, years, and other metadata
        filename = re.sub(r'\b(1080p|720p|480p|2160p|HDRip|BRRip|WEBRip|WEB-DL|HDTV|DVD|BluRay|x264|x265|h264|h265|AAC|DDP?5\.1|DD?5\.1|HEVC|AVC)\b', '', filename, flags=re.IGNORECASE)
        
        # Remove years (1900-2099)
        filename = re.sub(r'\b(19|20)\d{2}\b', '', filename)
        
        # Remove season and episode indicators
        filename = re.sub(r'\b[Ss]\d+[Ee]\d+\b', '', filename)
        filename = re.sub(r'\bSeason\s*\d+\b', '', filename, flags=re.IGNORECASE)
        filename = re.sub(r'\bEpisode\s*\d+\b', '', filename, flags=re.IGNORECASE)
        
        # Remove common prefixes/suffixes
        filename = re.sub(r'^\[.*?\]|\[.*?\]$', '', filename)
        filename = re.sub(r'^\(.*?\)|\(.*?\)$', '', filename)
        
        # Remove emojis and special characters
        filename = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', '', filename)
        filename = re.sub(r'[^a-zA-Z0-9\s\u00C0-\u017F\-_\']', ' ', filename)
        
        # Remove extra spaces
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        return filename

    def search_movies(self, query: str) -> List[Dict]:
        """Search for movies by title"""
        # Clean the query
        clean_query = self.clean_filename(query)
        
        url = f"{self.base_url}/search/movie"
        params = {
            "api_key": self.api_key,
            "query": clean_query,
            "language": "es-ES"  # Spanish language
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("results", [])
        return []

    def search_tv_shows(self, query: str) -> List[Dict]:
        """Search for TV shows by title"""
        # Clean the query
        clean_query = self.clean_filename(query)
        
        url = f"{self.base_url}/search/tv"
        params = {
            "api_key": self.api_key,
            "query": clean_query,
            "language": "es-ES"  # Spanish language
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("results", [])
        return []

    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get detailed information about a movie"""
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            "api_key": self.api_key,
            "language": "es-ES"  # Spanish language
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None

    def get_tv_show_details(self, tv_id: int) -> Optional[Dict]:
        """Get detailed information about a TV show"""
        url = f"{self.base_url}/tv/{tv_id}"
        params = {
            "api_key": self.api_key,
            "language": "es-ES"  # Spanish language
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None

    def get_season_details(self, tv_id: int, season_number: int) -> Optional[Dict]:
        """Get detailed information about a TV season"""
        url = f"{self.base_url}/tv/{tv_id}/season/{season_number}"
        params = {
            "api_key": self.api_key,
            "language": "es-ES"  # Spanish language
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return None

    def format_movie_caption(self, movie_data: Dict) -> str:
        """Format movie data into a caption"""
        title = movie_data.get("title", "Unknown Title")
        year = movie_data.get("release_date", "")[:4] if movie_data.get("release_date") else "N/A"
        rating = movie_data.get("vote_average", "N/A")
        overview = movie_data.get("overview", "No description available")
        duration = movie_data.get("runtime", "N/A")
        
        # Limit overview length for Telegram
        if len(overview) > 200:
            overview = overview[:200] + "..."
        
        caption = f"🎬 *{title}*\n\n"
        caption += f"📅 Año: {year}\n"
        caption += f"⭐ Calificación: {rating}/10\n"
        caption += f"⏱ Duración: {duration} min\n\n"
        caption += f"📖 Descripción: {overview}"
        
        return caption

    def format_tv_show_caption(self, tv_data: Dict) -> str:
        """Format TV show data into a caption"""
        title = tv_data.get("name", "Unknown Title")
        year = tv_data.get("first_air_date", "")[:4] if tv_data.get("first_air_date") else "N/A"
        rating = tv_data.get("vote_average", "N/A")
        seasons = tv_data.get("number_of_seasons", "N/A")
        episodes = tv_data.get("number_of_episodes", "N/A")
        overview = tv_data.get("overview", "No description available")
        
        # Limit overview length for Telegram
        if len(overview) > 200:
            overview = overview[:200] + "..."
        
        caption = f"📺 *{title}*\n\n"
        caption += f"📅 Año: {year}\n"
        caption += f"⭐ Calificación: {rating}/10\n"
        caption += f"📚 Temporadas: {seasons}\n"
        caption += f"🎭 Episodios: {episodes}\n\n"
        caption += f"📖 Descripción: {overview}"
        
        return caption

    def get_poster_url(self, poster_path: str) -> str:
        """Get full poster URL from poster path"""
        if poster_path:
            return f"{self.image_base_url}{poster_path}"
        return ""