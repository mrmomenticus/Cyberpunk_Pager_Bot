import logging
from sqlalchemy import func, select
from pager.databases.core import Game, Player, Inventory, Stuff, async_session_factory


"""
    ORM для работы с таблицей Players.
"""


class PlayerOrm:
    """
    Ищет игрока по его Telegram id.

    Args:
        id_tg: Telegram id

    Returns:
        Player: Возвращает оьъект игрока или None.
    """

    @staticmethod
    async def select_player_from_id(id_tg: int) -> Player:
        stmt = select(Player).where(Player.id_tg == id_tg)
        async with async_session_factory() as session:
            result = await session.execute(stmt)
            return result.scalars().first()

    """
        Ищет игрока по его имени.

        Args:
            player_name: Имя игрока

        Returns:
            Player: Возвращает оьъект игрока или None.
    """

    @staticmethod
    async def select_player_from_name(player_name: str) -> Player:
        stmt = select(Player).where(Player.player_name == player_name)
        async with async_session_factory() as session:
            result = await session.execute(stmt)
            return result.scalars().first()

    """
        Ищет игрока по его Telegram id.
        
        Args:
            id_tg: Telegram id
            
        Returns:
            Game: Возвращает все игры где присутствует этот игрок или None.
    """

    @staticmethod
    async def select_games_by_player_id(id_tg: int):
        stmt = (
            select(Game)
            .join(Player, Game.player_id == Player.id_tg)
            .where(Player.id_tg == id_tg)
        )
        async with async_session_factory() as session:
            result = await session.execute(stmt)
            games = result.scalars().all()
            return games

    @staticmethod
    async def update_new_player(new_player: Player):
        async with async_session_factory() as session:
            async with session.begin():
                session.add(new_player)
                session.add(Inventory(player_id=new_player.id_tg))
                await session.commit()
        

    """
        Добавляет url фото в photo_state игрока.
        
        Args:
            player_name: Имя игрока.
            photo_url: url фото.
    """

    @staticmethod
    async def create_photo_state(player_name: str, photo_url: str):  # TODO: узкое место
        async with async_session_factory() as session:
            async with session.begin():
                stmt = select(Player).where(
                    Player.player_name == player_name
                )  # TODO: Добавить исключение если не найден игрок
                result = await session.execute(stmt)
                player = result.scalars().first()
                if player is None:
                    logging.error("Такого игрока нет")
                    raise Exception("Такого игрока нет")
                player.photo_state = (
                    player.photo_state or []
                )  # Initialize as empty list if None
                player.photo_state = player.photo_state + [photo_url]
                await session.commit()

    @staticmethod
    async def select_photo_state(
        player_name: str,
    ):  # TODO: может быть ошибка, если в базе есть 2 одинаковых игрока по имени
        async with async_session_factory() as session:
            stmt = select(Player).where(Player.player_name == player_name)
            result = await session.execute(stmt)
            player = result.scalars().all()
            if player is not None:
                return player
            else:
                return None

    @staticmethod
    async def delete_photo_state(player_name: str):
        async with async_session_factory() as session:
            async with session.begin():
                stmt = select(Player).where(Player.player_name == player_name)
                result = await session.execute(stmt)
                player = result.scalars().first()
                if player is not None:
                    player.photo_state = None
                    await session.commit()
                else:
                    logging.error("Такого игрока нет")
                    raise Exception("Такого игрока нет")

    @staticmethod
    async def update_money(player_name: str, money: int):
        async with async_session_factory() as session:
            async with session.begin():
                stmt = (
                    select(Inventory)
                    .join(Player, Inventory.player_id == Player.id_tg)
                    .where(Player.player_name == player_name)
                )
                result = await session.execute(stmt)
                inventory = result.scalars().first()
                if inventory is not None:
                    sum = inventory.money + money
                    inventory.money += money
                    await session.commit()
                    return sum
                else:
                    logging.debug("Такого игрока нет")
                    return None
                
    @staticmethod
    async def take_money(player_name: str, money: int):
        async with async_session_factory() as session:
            async with session.begin():
                stmt = (
                    select(Inventory)
                    .join(Player, Inventory.player_id == Player.id_tg)
                    .where(Player.player_name == player_name)
                )
                result = await session.execute(stmt)
                inventory = result.scalars().first()
                if inventory is not None:
                    sum = inventory.money - money
                    inventory.money -= money
                    await session.commit()
                    return sum
                else:
                    logging.debug("Такого игрока нет")
                    return None
    @staticmethod
    async def select_money(player_name: str):
        async with async_session_factory() as session:
            stmt = (
                select(Inventory)
                .join(Player, Inventory.player_id == Player.id_tg)
                .where(Player.player_name == player_name)
            )
            result = await session.execute(stmt)
            inventory = result.scalars().first()
            if inventory is not None:
                return inventory.money
            else:
                return None
    @staticmethod
    async def add_new_item(player_name: str, item_name: str, price_item: int, description: str):
        async with async_session_factory() as session:
            async with session.begin():
                stmt = (
                    select(Inventory)
                    .join(Player, Inventory.player_id == Player.id_tg)
                    .where(Player.player_name == player_name)
                )
                result = await session.execute(stmt)
                inventory = result.scalars().first()
                if inventory is not None:
                    session.add(
                        Stuff(
                            invetory_id=inventory.id,
                            title=item_name,
                            price=price_item,
                            description=description
                        )
                    )
                else:
                    raise ValueError("Такого игрока нет")
                await session.commit()

class GameOrm:
    @staticmethod
    async def get_game_by_number_group(number_group: int) -> Game:
        stmt = select(Game).where(Game.number_group == number_group)
        async with async_session_factory() as session:
            result = await session.execute(stmt)
            result = result.scalars().first()
            if result is not None:
                return result
            else:
                return None

    @staticmethod
    async def set_date_game(number_group: int, date_str: str):
        async with async_session_factory() as session:
            async with session.begin():
                stmt = select(Game).where(Game.number_group == number_group)
                result = await session.execute(stmt)
                game = result.scalars().first()
                game.date = func.to_date(date_str, "DD.MM.YYYY")
                await session.commit()

    @staticmethod
    async def set_new_game(new_game: Game):
        async with async_session_factory() as session:
            async with session.begin():
                session.add(new_game)
                await session.commit()
