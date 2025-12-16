import sqlite3
from typing import List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Media:
    id: int
    title: str
    year: int
    media_type: str  # 'movie' or 'tv'
    tmdb_id: int
    file_id: str
    file_path: str
    caption: str
    poster_url: str
    created_at: str

@dataclass
class Episode:
    id: int
    media_id: int
    season_number: int
    episode_number: int
    title: str
    file_id: str
    file_path: str
    created_at: str

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create media table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                year INTEGER,
                media_type TEXT NOT NULL,
                tmdb_id INTEGER NOT NULL,
                file_id TEXT,
                file_path TEXT,
                caption TEXT,
                poster_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create episodes table for TV series
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                media_id INTEGER NOT NULL,
                season_number INTEGER NOT NULL,
                episode_number INTEGER NOT NULL,
                title TEXT,
                file_id TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (media_id) REFERENCES media (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_media(self, media: Media) -> int:
        """Add a new media entry to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO media (title, year, media_type, tmdb_id, file_id, file_path, caption, poster_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (media.title, media.year, media.media_type, media.tmdb_id, 
              media.file_id, media.file_path, media.caption, media.poster_url))
        
        media_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return media_id

    def add_episode(self, episode: Episode) -> int:
        """Add a new episode entry to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO episodes (media_id, season_number, episode_number, title, file_id, file_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (episode.media_id, episode.season_number, episode.episode_number,
              episode.title, episode.file_id, episode.file_path))
        
        episode_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return episode_id

    def get_media_by_id(self, media_id: int) -> Optional[Media]:
        """Retrieve a media entry by its ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM media WHERE id = ?', (media_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Media(*row)
        return None

    def get_media_by_tmdb_id(self, tmdb_id: int) -> Optional[Media]:
        """Retrieve a media entry by its TMDB ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM media WHERE tmdb_id = ?', (tmdb_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Media(*row)
        return None

    def search_media(self, query: str) -> List[Media]:
        """Search for media by title"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM media 
            WHERE title LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{query}%',))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [Media(*row) for row in rows]

    def get_episodes_by_media_id(self, media_id: int) -> List[Episode]:
        """Retrieve all episodes for a TV series"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM episodes 
            WHERE media_id = ?
            ORDER BY season_number, episode_number
        ''', (media_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [Episode(*row) for row in rows]

    def get_episode_by_id(self, episode_id: int) -> Optional[Episode]:
        """Retrieve an episode by its ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM episodes WHERE id = ?', (episode_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Episode(*row)
        return None

    def delete_media(self, media_id: int) -> bool:
        """Delete a media entry and its episodes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete episodes first (foreign key constraint)
        cursor.execute('DELETE FROM episodes WHERE media_id = ?', (media_id,))
        
        # Delete media
        cursor.execute('DELETE FROM media WHERE id = ?', (media_id,))
        
        changes = cursor.rowcount
        conn.commit()
        conn.close()
        
        return changes > 0

    def delete_all_media(self) -> int:
        """Delete all media and episodes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete episodes first (foreign key constraint)
        cursor.execute('DELETE FROM episodes')
        episodes_deleted = cursor.rowcount
        
        # Delete media
        cursor.execute('DELETE FROM media')
        media_deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return media_deleted

    def get_stats(self) -> Tuple[int, int]:
        """Get database statistics (media count, episodes count)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM media')
        media_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM episodes')
        episodes_count = cursor.fetchone()[0]
        
        conn.close()
        
        return media_count, episodes_count