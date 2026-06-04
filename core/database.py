import aiomysql

from core.config import get_db_config


async def connect():
    cfg = get_db_config()
    return await aiomysql.connect(
        host=cfg.get("host", "127.0.0.1"),
        port=cfg.get("port", 3306),
        user=cfg.get("user", ""),
        password=cfg.get("password", ""),
        db=cfg.get("database", ""),
        autocommit=bool(cfg.get("autocommit", True)),
        cursorclass=aiomysql.DictCursor,
    )


from core.loggers import log_tasks


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
