import logging
from asyncio import run

from PGram import Bot
from aiogram.client.default import DefaultBotProperties
from x_model import init_db

from xync_bot.routers import Store
from xync_bot.routers.cond import cr as cr

# from xync_bot.routers.main import mr
from xync_bot.routers.pay.handler import pay as pay

if __name__ == "__main__":
    from xync_bot.loader import TOKEN, TORM

    logging.basicConfig(level=logging.INFO)

    async def main() -> None:
        cn = await init_db(TORM)
        store = Store()
        store.glob = await Store.Global()
        bot = Bot(TOKEN, [pay], cn, default=DefaultBotProperties(parse_mode="HTML"), store=store)
        await bot.start()

    run(main())
