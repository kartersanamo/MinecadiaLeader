import functools
import logger
import aiomysql
import discord
import json
from typing import Optional
import os
import time
from dotenv import load_dotenv

load_dotenv()

log_tasks = logger.logging.getLogger("Tasks")
log_commands = logger.logging.getLogger("Commands")


def get_data():
   with open("Assets/config.json", "r") as file:
      data = json.load(file)
   if os.getenv("DISCORD_TOKEN"):
      data["TOKEN"] = os.getenv("DISCORD_TOKEN")
   return data


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


def task(action_name: str, log: bool = None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                time_elapsed = round((time.perf_counter() - start_time), 2)
                if time_elapsed > 3:
                    log_tasks.warning(
                        f"{action_name} took a long time to complete and finished in {time_elapsed}s"
                    )
                elif log:
                    log_tasks.info(f"{action_name} completed in {time_elapsed}s")
                return result
            except Exception as error:
                log_tasks.error(
                    f"{action_name} failed after {round((time.perf_counter() - start_time), 2)}s : {error}"
                )
                raise error
        return wrapper
    return decorator


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
        log_tasks.error(f"Error executing query: {query} {error}")
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
    await execute(
        f"INSERT INTO `statistics` (`user_ID`, `tickets_closed`, `messages_sent`, `warnings`, "
        f"`mutes`, `temp_bans`, `bans`, `screenshares`, `manual_bans`, `blacklists`, `revives`, "
        f"`appeals`, `threads_locked`, `strike_team_votes`, `characters_sent`, `punishment_requests`) "
        f"VALUES ('{user.id}', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0')"
    )
