from core.database import DatabasePool


class FactionRepository:
    def __init__(self, db: DatabasePool | None = None):
        self._db = db or DatabasePool.get()

    async def execute(self, query: str) -> list:
        return await self._db.execute(query)

    async def find_by_leader(self, leader_id: int) -> list:
        return await self._db.execute(
            f"SELECT * FROM `leader_factions` WHERE `leader_id` = '{leader_id}'"
        )

    async def find_by_coleader_1(self, user_id: int) -> list:
        return await self._db.execute(
            f"SELECT * FROM `leader_factions` WHERE `coleader_id_1` = '{user_id}'"
        )

    async def find_by_coleader_2(self, user_id: int) -> list:
        return await self._db.execute(
            f"SELECT * FROM `leader_factions` WHERE `coleader_id_2` = '{user_id}'"
        )

    async def all_faction_names(self) -> list:
        return await self._db.execute("SELECT faction_name FROM leader_factions")

    async def find_by_faction_name(self, faction: str) -> list:
        return await self._db.execute(
            f"SELECT * FROM leader_factions WHERE faction_name= '{faction}'"
        )

    async def find_by_leader_id(self, user_id: int) -> list:
        return await self._db.execute(
            f"SELECT * FROM leader_factions WHERE leader_id= '{user_id}'"
        )

    async def find_by_coleader_id_1(self, user_id: int) -> list:
        return await self._db.execute(
            f"SELECT * FROM leader_factions WHERE coleader_id_1= '{user_id}'"
        )

    async def find_by_coleader_id_2(self, user_id: int) -> list:
        return await self._db.execute(
            f"SELECT * FROM leader_factions WHERE coleader_id_2= '{user_id}'"
        )

    async def delete_by_channel(self, channel_id: int) -> None:
        await self._db.execute(
            f"DELETE FROM leader_factions WHERE channel_id='{channel_id}'"
        )

    async def insert_faction(
        self, faction: str, leader_id: int, channel_id: int
    ) -> None:
        await self._db.execute(
            f"INSERT INTO leader_factions (faction_name, leader_id, coleader_id_1, "
            f"coleader_id_2, channel_id) VALUES ('{faction}', '{leader_id}', '', '', '{channel_id}')"
        )

    async def update_coleader_1(self, faction: str, user_id: int) -> None:
        await self._db.execute(
            f"UPDATE leader_factions SET coleader_id_1 = '{user_id}' WHERE faction_name= '{faction}'"
        )

    async def update_coleader_2(self, faction: str, user_id: int) -> None:
        await self._db.execute(
            f"UPDATE leader_factions SET coleader_id_2 = '{user_id}' WHERE faction_name= '{faction}'"
        )
