import asyncio
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMIN_ID, DATABASE_GROUP_ID, OFFICIAL_CHANNEL_ID, TMDB_API_KEY, START_MESSAGE, HELP_MESSAGE
from database import Database, Media, Episode
from tmdb_api import TMDBApi

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize components
db = Database("media_database.db")
tmdb = TMDBApi(TMDB_API_KEY)

# Store temporary data for media indexing
temp_indexing_data = {}

# Ensure downloads directory exists
if not os.path.exists("downloads"):
    os.makedirs("downloads")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    await update.message.reply_text(START_MESSAGE, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")

async def search_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search for media by title"""
    if not context.args:
        await update.message.reply_text("Por favor proporciona un término de búsqueda. Ejemplo: /search Avatar")
        return
    
    query = " ".join(context.args)
    results = db.search_media(query)
    
    if not results:
        await update.message.reply_text("No se encontraron resultados para tu búsqueda.")
        return
    
    # Display first 5 results
    for media in results[:5]:
        keyboard = [[InlineKeyboardButton("📥 Descargar", callback_data=f"download_{media.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await update.message.reply_photo(
                photo=media.poster_url,
                caption=media.caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error sending media {media.id}: {e}")
            # Fallback without image
            await update.message.reply_text(
                text=media.caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show database statistics"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Solo los administradores pueden usar este comando.")
        return
    
    media_count, episodes_count = db.get_stats()
    stats_message = f"📊 Estadísticas de la Base de Datos:\n\n"
    stats_message += f"Películas/Series: {media_count}\n"
    stats_message += f"Episodios: {episodes_count}"
    
    await update.message.reply_text(stats_message)

async def delete_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a media entry by ID"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Solo los administradores pueden usar este comando.")
        return
    
    if not context.args:
        await update.message.reply_text("Por favor proporciona el ID del contenido a eliminar. Ejemplo: /delete_media 123")
        return
    
    try:
        media_id = int(context.args[0])
        media = db.get_media_by_id(media_id)
        
        if not media:
            await update.message.reply_text(f"No se encontró contenido con ID {media_id}.")
            return
        
        # Delete media from database
        if db.delete_media(media_id):
            # Also delete associated file if it exists locally
            if media.file_path and os.path.exists(media.file_path):
                try:
                    os.remove(media.file_path)
                except Exception as e:
                    logger.error(f"Error deleting file {media.file_path}: {e}")
            
            await update.message.reply_text(f"Contenido '{media.title}' con ID {media_id} eliminado exitosamente.")
        else:
            await update.message.reply_text(f"No se pudo eliminar el contenido con ID {media_id}.")
    except ValueError:
        await update.message.reply_text("Por favor proporciona un ID válido.")
    except Exception as e:
        logger.error(f"Error deleting media: {e}")
        await update.message.reply_text("Ocurrió un error al eliminar el contenido.")

async def delete_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete all media from database"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Solo los administradores pueden usar este comando.")
        return
    
    # Confirm action
    if not context.args or context.args[0].lower() != "confirmar":
        await update.message.reply_text(
            "⚠️ Esta acción eliminará TODO el contenido de la base de datos.\n"
            "Para confirmar, usa: /delete_all confirmar"
        )
        return
    
    try:
        # Get count before deletion
        media_count, episodes_count = db.get_stats()
        
        # Delete all entries
        deleted_count = db.delete_all_media()
        
        # Clean up downloads directory
        if os.path.exists("downloads"):
            for filename in os.listdir("downloads"):
                file_path = os.path.join("downloads", filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    logger.error(f"Error deleting file {file_path}: {e}")
        
        await update.message.reply_text(
            f"✅ Se han eliminado {deleted_count} entradas de la base de datos.\n"
            f"Archivos de películas/series: {media_count}\n"
            f"Episodios: {episodes_count}"
        )
    except Exception as e:
        logger.error(f"Error deleting all media: {e}")
        await update.message.reply_text("Ocurrió un error al eliminar todo el contenido.")

async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a movie by TMDB ID"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Solo los administradores pueden usar este comando.")
        return
    
    if not context.args:
        await update.message.reply_text("Por favor proporciona el ID de TMDB de la película. Ejemplo: /add_movie 19995")
        return
    
    try:
        tmdb_id = int(context.args[0])
        movie_data = tmdb.get_movie_details(tmdb_id)
        
        if not movie_data:
            await update.message.reply_text("No se pudo obtener información de la película. Verifica el ID de TMDB.")
            return
        
        # Check if movie already exists
        existing_media = db.get_media_by_tmdb_id(tmdb_id)
        if existing_media:
            await update.message.reply_text(f"Esta película ya está en la base de datos con ID {existing_media.id}.")
            return
        
        # Format caption and get poster
        caption = tmdb.format_movie_caption(movie_data)
        poster_url = tmdb.get_poster_url(movie_data.get("poster_path", ""))
        
        # Create media object
        media = Media(
            id=0,
            title=movie_data.get("title", ""),
            year=int(movie_data.get("release_date", "")[:4]) if movie_data.get("release_date") else 0,
            media_type="movie",
            tmdb_id=tmdb_id,
            file_id="",
            file_path="",
            caption=caption,
            poster_url=poster_url,
            created_at=""
        )
        
        # Save to database
        media_id = db.add_media(media)
        
        # Send to official channel
        keyboard = [[InlineKeyboardButton("📥 Descargar", callback_data=f"download_{media_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            message = await context.bot.send_photo(
                chat_id=OFFICIAL_CHANNEL_ID,
                photo=poster_url,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
            # Update with message ID for future reference
            await update.message.reply_text(f"Película añadida exitosamente con ID {media_id} y publicada en el canal.")
        except Exception as e:
            logger.error(f"Error publishing to channel: {e}")
            await update.message.reply_text(f"Película añadida con ID {media_id} pero hubo un error al publicar en el canal.")
            
    except ValueError:
        await update.message.reply_text("Por favor proporciona un ID de TMDB válido.")
    except Exception as e:
        logger.error(f"Error adding movie: {e}")
        await update.message.reply_text("Ocurrió un error al añadir la película.")

async def add_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a TV series by TMDB ID"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Solo los administradores pueden usar este comando.")
        return
    
    if not context.args:
        await update.message.reply_text("Por favor proporciona el ID de TMDB de la serie. Ejemplo: /add_series 1399")
        return
    
    try:
        tmdb_id = int(context.args[0])
        tv_data = tmdb.get_tv_show_details(tmdb_id)
        
        if not tv_data:
            await update.message.reply_text("No se pudo obtener información de la serie. Verifica el ID de TMDB.")
            return
        
        # Check if series already exists
        existing_media = db.get_media_by_tmdb_id(tmdb_id)
        if existing_media:
            await update.message.reply_text(f"Esta serie ya está en la base de datos con ID {existing_media.id}.")
            return
        
        # Format caption and get poster
        caption = tmdb.format_tv_show_caption(tv_data)
        poster_url = tmdb.get_poster_url(tv_data.get("poster_path", ""))
        
        # Create media object
        media = Media(
            id=0,
            title=tv_data.get("name", ""),
            year=int(tv_data.get("first_air_date", "")[:4]) if tv_data.get("first_air_date") else 0,
            media_type="tv",
            tmdb_id=tmdb_id,
            file_id="",
            file_path="",
            caption=caption,
            poster_url=poster_url,
            created_at=""
        )
        
        # Save to database
        media_id = db.add_media(media)
        
        # Send to official channel
        keyboard = [[InlineKeyboardButton("📥 Descargar", callback_data=f"download_{media_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            message = await context.bot.send_photo(
                chat_id=OFFICIAL_CHANNEL_ID,
                photo=poster_url,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
            # Update with message ID for future reference
            await update.message.reply_text(f"Serie añadida exitosamente con ID {media_id} y publicada en el canal.")
        except Exception as e:
            logger.error(f"Error publishing to channel: {e}")
            await update.message.reply_text(f"Serie añadida con ID {media_id} pero hubo un error al publicar en el canal.")
            
    except ValueError:
        await update.message.reply_text("Por favor proporciona un ID de TMDB válido.")
    except Exception as e:
        logger.error(f"Error adding series: {e}")
        await update.message.reply_text("Ocurrió un error al añadir la serie.")

async def handle_database_group_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages from the database group to index media files"""
    if update.effective_chat.id != DATABASE_GROUP_ID:
        return
    
    # Only process messages with documents or videos
    if not update.message.document and not update.message.video:
        return
    
    # Store file information temporarily
    file_id = update.message.document.file_id if update.message.document else update.message.video.file_id
    file_name = update.message.document.file_name if update.message.document else "video.mp4"
    
    # Clean filename and search TMDB automatically
    clean_name = tmdb.clean_filename(file_name)
    
    # Search for movies and TV shows
    movies = tmdb.search_movies(clean_name)[:3]  # Top 3 matches
    tv_shows = tmdb.search_tv_shows(clean_name)[:3]  # Top 3 matches
    
    # Prepare keyboard with search results
    keyboard = []
    
    # Add movie options
    if movies:
        keyboard.append([InlineKeyboardButton("🎬 Películas encontradas:", callback_data="noop")])
        for movie in movies:
            title = movie.get("title", "Unknown")
            year = movie.get("release_date", "")[:4] if movie.get("release_date") else "N/A"
            button_text = f"{title} ({year})"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"select_movie_{movie['id']}")])
    
    # Add TV show options
    if tv_shows:
        keyboard.append([InlineKeyboardButton("📺 Series encontradas:", callback_data="noop")])
        for show in tv_shows:
            title = show.get("name", "Unknown")
            year = show.get("first_air_date", "")[:4] if show.get("first_air_date") else "N/A"
            button_text = f"{title} ({year})"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"select_tv_{show['id']}")])
    
    # Add manual option
    keyboard.append([InlineKeyboardButton("➕ Ingresar ID manualmente", callback_data="manual_id")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Store data for later use
    temp_indexing_data[update.effective_user.id] = {
        "file_id": file_id,
        "file_name": file_name,
        "clean_name": clean_name,
        "message_id": update.message.message_id
    }
    
    await update.message.reply_text(
        f"Nuevo archivo detectado: {file_name}\n\nResultados de búsqueda automatizada:",
        reply_markup=reply_markup
    )

async def download_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle download button presses"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Extract media ID from callback data
        media_id = int(query.data.split("_")[1])
        media = db.get_media_by_id(media_id)
        
        if not media:
            await query.edit_message_text("Contenido no encontrado.")
            return
        
        # For TV series, show episode selection
        if media.media_type == "tv":
            episodes = db.get_episodes_by_media_id(media_id)
            
            if not episodes:
                await query.edit_message_text("Esta serie aún no tiene episodios disponibles.")
                return
            
            # Create episode selection keyboard
            keyboard = []
            current_season = None
            season_row = []
            
            for episode in episodes:
                if episode.season_number != current_season:
                    if current_season is not None:
                        keyboard.append(season_row)
                    current_season = episode.season_number
                    season_row = []
                
                button_text = f"S{episode.season_number}E{episode.episode_number}"
                season_row.append(InlineKeyboardButton(button_text, callback_data=f"episode_{episode.id}"))
            
            if season_row:
                keyboard.append(season_row)
            
            keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data=f"back_{media_id}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"Selecciona un episodio de {media.title}:",
                reply_markup=reply_markup
            )
        else:
            # For movies, send the file directly
            if media.file_id:
                await context.bot.send_document(
                    chat_id=query.from_user.id,
                    document=media.file_id,
                    caption=media.caption,
                    parse_mode="Markdown"
                )
                await query.edit_message_text("Archivo enviado. ¡Disfruta!")
            else:
                await query.edit_message_text("El archivo no está disponible actualmente.")
                
    except Exception as e:
        logger.error(f"Error handling download callback: {e}")
        await query.edit_message_text("Ocurrió un error al procesar tu solicitud.")

async def episode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle episode selection"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Extract episode ID from callback data
        episode_id = int(query.data.split("_")[1])
        
        # Get episode and associated media
        episode = db.get_episode_by_id(episode_id)
        if not episode:
            await query.edit_message_text("Episodio no encontrado.")
            return
        
        media = db.get_media_by_id(episode.media_id)
        if not media:
            await query.edit_message_text("Contenido no encontrado.")
            return
        
        # Send the episode file
        if episode.file_id:
            await context.bot.send_document(
                chat_id=query.from_user.id,
                document=episode.file_id,
                caption=f"{media.title} - S{episode.season_number:02d}E{episode.episode_number:02d}: {episode.title}",
                parse_mode="Markdown"
            )
            await query.edit_message_text("Episodio enviado. ¡Disfruta!")
        else:
            await query.edit_message_text("El episodio no está disponible actualmente.")
            
    except Exception as e:
        logger.error(f"Error handling episode callback: {e}")
        await query.edit_message_text("Ocurrió un error al procesar tu solicitud.")

async def back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back button presses"""
    query = update.callback_query
    await query.answer()
    
    try:
        # Extract media ID from callback data
        media_id = int(query.data.split("_")[1])
        media = db.get_media_by_id(media_id)
        
        if not media:
            await query.edit_message_text("Contenido no encontrado.")
            return
        
        # Show original media view
        keyboard = [[InlineKeyboardButton("📥 Descargar", callback_data=f"download_{media_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=media.caption,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error handling back callback: {e}")
        await query.edit_message_text("Ocurrió un error al procesar tu solicitud.")

async def handle_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle TMDB selection callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check if user has pending indexing data
    if user_id not in temp_indexing_data:
        await query.edit_message_text("Sesión expirada. Por favor, sube el archivo nuevamente.")
        return
    
    data = temp_indexing_data[user_id]
    
    try:
        if query.data == "manual_id":
            # Prompt for manual TMDB ID entry
            await query.edit_message_text(
                "Por favor, ingresa el ID de TMDB:\n\n"
                "Para películas: /add_movie <id>\n"
                "Para series: /add_series <id>"
            )
            return
        elif query.data == "noop":
            # Do nothing for header buttons
            return
        elif query.data.startswith("select_movie_"):
            # Extract movie ID
            tmdb_id = int(query.data.split("_")[-1])
            await process_movie_addition(update, context, tmdb_id, data)
        elif query.data.startswith("select_tv_"):
            # Extract TV show ID
            tmdb_id = int(query.data.split("_")[-1])
            await process_series_addition(update, context, tmdb_id, data)
    except Exception as e:
        logger.error(f"Error handling selection callback: {e}")
        await query.edit_message_text("Ocurrió un error al procesar tu solicitud.")

async def process_movie_addition(update: Update, context: ContextTypes.DEFAULT_TYPE, tmdb_id: int, file_data: dict):
    """Process movie addition with automatic TMDB data fetching"""
    try:
        movie_data = tmdb.get_movie_details(tmdb_id)
        
        if not movie_data:
            await update.callback_query.edit_message_text("No se pudo obtener información de la película. Verifica el ID de TMDB.")
            return
        
        # Check if movie already exists
        existing_media = db.get_media_by_tmdb_id(tmdb_id)
        if existing_media:
            await update.callback_query.edit_message_text(f"Esta película ya está en la base de datos con ID {existing_media.id}.")
            return
        
        # Format caption and get poster
        caption = tmdb.format_movie_caption(movie_data)
        poster_url = tmdb.get_poster_url(movie_data.get("poster_path", ""))
        
        # Create media object
        media = Media(
            id=0,
            title=movie_data.get("title", ""),
            year=int(movie_data.get("release_date", "")[:4]) if movie_data.get("release_date") else 0,
            media_type="movie",
            tmdb_id=tmdb_id,
            file_id=file_data["file_id"],
            file_path="",
            caption=caption,
            poster_url=poster_url,
            created_at=""
        )
        
        # Save to database
        media_id = db.add_media(media)
        
        # Send to official channel
        keyboard = [[InlineKeyboardButton("📥 Descargar", callback_data=f"download_{media_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            message = await context.bot.send_photo(
                chat_id=OFFICIAL_CHANNEL_ID,
                photo=poster_url,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
            # Clear temporary data
            if update.callback_query.from_user.id in temp_indexing_data:
                del temp_indexing_data[update.callback_query.from_user.id]
            
            await update.callback_query.edit_message_text(f"✅ Película añadida exitosamente con ID {media_id} y publicada en el canal.")
        except Exception as e:
            logger.error(f"Error publishing to channel: {e}")
            await update.callback_query.edit_message_text(f"Película añadida con ID {media_id} pero hubo un error al publicar en el canal.")
            
    except Exception as e:
        logger.error(f"Error adding movie: {e}")
        await update.callback_query.edit_message_text("Ocurrió un error al añadir la película.")

async def process_series_addition(update: Update, context: ContextTypes.DEFAULT_TYPE, tmdb_id: int, file_data: dict):
    """Process TV series addition with automatic TMDB data fetching"""
    try:
        tv_data = tmdb.get_tv_show_details(tmdb_id)
        
        if not tv_data:
            await update.callback_query.edit_message_text("No se pudo obtener información de la serie. Verifica el ID de TMDB.")
            return
        
        # Check if series already exists
        existing_media = db.get_media_by_tmdb_id(tmdb_id)
        if existing_media:
            await update.callback_query.edit_message_text(f"Esta serie ya está en la base de datos con ID {existing_media.id}.")
            return
        
        # Format caption and get poster
        caption = tmdb.format_tv_show_caption(tv_data)
        poster_url = tmdb.get_poster_url(tv_data.get("poster_path", ""))
        
        # Create media object
        media = Media(
            id=0,
            title=tv_data.get("name", ""),
            year=int(tv_data.get("first_air_date", "")[:4]) if tv_data.get("first_air_date") else 0,
            media_type="tv",
            tmdb_id=tmdb_id,
            file_id=file_data["file_id"],
            file_path="",
            caption=caption,
            poster_url=poster_url,
            created_at=""
        )
        
        # Save to database
        media_id = db.add_media(media)
        
        # Send to official channel
        keyboard = [[InlineKeyboardButton("📥 Descargar", callback_data=f"download_{media_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            message = await context.bot.send_photo(
                chat_id=OFFICIAL_CHANNEL_ID,
                photo=poster_url,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
            # Clear temporary data
            if update.callback_query.from_user.id in temp_indexing_data:
                del temp_indexing_data[update.callback_query.from_user.id]
            
            await update.callback_query.edit_message_text(f"✅ Serie añadida exitosamente con ID {media_id} y publicada en el canal.")
        except Exception as e:
            logger.error(f"Error publishing to channel: {e}")
            await update.callback_query.edit_message_text(f"Serie añadida con ID {media_id} pero hubo un error al publicar en el canal.")
            
    except Exception as e:
        logger.error(f"Error adding series: {e}")
        await update.callback_query.edit_message_text("Ocurrió un error al añadir la serie.")

def main():
    """Start the bot"""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_media))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("delete_media", delete_media))
    application.add_handler(CommandHandler("delete_all", delete_all))
    application.add_handler(CommandHandler("add_movie", add_movie))
    application.add_handler(CommandHandler("add_series", add_series))

    # Register message handler for database group
    application.add_handler(MessageHandler(filters.Chat(DATABASE_GROUP_ID) & (filters.Document.ALL | filters.VIDEO), 
                                          handle_database_group_messages))

    # Register callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(download_callback, pattern="^download_"))
    application.add_handler(CallbackQueryHandler(episode_callback, pattern="^episode_"))
    application.add_handler(CallbackQueryHandler(back_callback, pattern="^back_"))
    application.add_handler(CallbackQueryHandler(handle_selection_callback, pattern="^(select_|manual_id|noop)"))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()