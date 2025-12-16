import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# Admin Configuration
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Group/Channel IDs
DATABASE_GROUP_ID = int(os.getenv("DATABASE_GROUP_ID"))
OFFICIAL_CHANNEL_ID = int(os.getenv("OFFICIAL_CHANNEL_ID"))

# TMDB Configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Database Configuration
DATABASE_PATH = "media_database.db"

# Bot Messages
START_MESSAGE = """
🎬 Welcome to the Media Bot!

🔍 Use /search <movie/series name> to find content
📚 Use /help to see available commands
"""

HELP_MESSAGE = """
Available Commands:
/start - Start the bot
/search <query> - Search for movies or series
/help - Show this help message

Admin Commands:
/add_movie <movie_id> - Add a movie by TMDB ID
/add_series <series_id> - Add a series by TMDB ID
/delete_media <media_id> - Delete media by ID
/delete_all - Delete all media from database
/stats - Show database statistics
"""