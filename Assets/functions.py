import aiomysql
import discord
import json
from typing import Optional
import os

def get_data():
   with open("Assets/config.json", "r") as file:
      return json.load(file)

def get_db_config():
    """Database config from .env (preferred) or config.json."""
    if os.getenv("DB_HOST"):
        return {
            "host": os.getenv("DB_HOST", "127.0.0.1"),
            "port": int(os.getenv("DB_PORT", "3306")),
            "user": os.getenv("DB_USER", ""),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "") or os.getenv("DB_DATABASE", ""),
            "autocommit": os.getenv("DB_AUTOCOMMIT", "true").lower() in ("1", "true", "yes"),
        }
    data = get_data()
    return data.get("DATABASE_CONFIG") or {}
   
data = get_data()

async def connect():
    cfg = get_db_config()
    return await aiomysql.connect(
        host=cfg.get("host", "127.0.0.1"),
        port=cfg.get("port", 3306),
        user=cfg.get("user", ""),
        password=cfg.get("password", ""),
        db=cfg.get("database", ""),
        autocommit=bool(cfg.get("autocommit", True)),
        cursorclass=aiomysql.DictCursor
    )

def get_embed_logo_url(logo_path: Optional[str]) -> Optional[str]:
    if not logo_path:
        return None

    if logo_path.startswith(("http://", "https://")):
        return logo_path

    if os.path.isfile(logo_path):
        filename = os.path.basename(logo_path)
        return f"attachment://{filename}"

    return None

async def execute(query):
    rows = []
    connection = None 
    try:
        connection = await connect()
        async with connection.cursor() as cursor:
            await cursor.execute(query)
            rows = await cursor.fetchall()
    except Exception as error:
        print(error)
    finally:
        if connection:
            connection.close()
        return rows
    
async def is_found(user: discord.Member, statistic: str):
    rows = await execute(f"SELECT * FROM `statistics` WHERE `user_ID`='{user.id}'")
    if rows:
        return rows[0][statistic]
    else:
        await new_entry(user)
        return 0

async def new_entry(user: discord.Member):
    await execute(f"INSERT INTO `statistics` (`user_ID`, `tickets_closed`, `messages_sent`, `warnings`, `mutes`, `temp_bans`, `bans`, `screenshares`, `manual_bans`, `blacklists`, `revives`, `appeals`, `threads_locked`, `strike_team_votes`, `characters_sent`, `punishment_requests`) VALUES ('{user.id}', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0')")