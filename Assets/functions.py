import aiomysql
import discord
import json

def get_data():
   with open("MinecadiaLeader/Assets/config.json", "r") as file:
      return json.load(file)
   
data = get_data()

async def connect():
    return await aiomysql.connect(
        host=data["DATABASE_CONFIG"]["host"],
        port=data["DATABASE_CONFIG"]["port"],
        user=data["DATABASE_CONFIG"]["user"],
        password=data["DATABASE_CONFIG"]["password"],
        db=data["DATABASE_CONFIG"]["database"],
        autocommit=bool(data["DATABASE_CONFIG"]["autocommit"]),
        cursorclass=aiomysql.DictCursor
    )

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