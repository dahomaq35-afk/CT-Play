# ============================================================
# GAME BOT - MAIN.PY
# ============================================================

import os
import asyncio
import logging

import discord
from discord.ext import commands

from games import GameSystem
from database import Database


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("GameBot")


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "❌ لم يتم العثور على DISCORD_TOKEN في Environment Variables."
    )


# ============================================================
# DISCORD INTENTS
# ============================================================

intents = discord.Intents.default()

# استقبال رسائل اللاعبين، مهم للألعاب التي تعتمد على الكتابة
intents.message_content = True

# معرفة أعضاء السيرفر
intents.members = True

# لا نحتاج حالة Online/Idle للأعضاء
intents.presences = False


# ============================================================
# BOT
# ============================================================

class GameBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        self.database = Database()
        self.game_system = GameSystem(self)

    async def setup_hook(self):
        """
        تحميل نظام الألعاب ومزامنة Slash Commands.
        """

        await self.game_system.setup()

        try:
            synced = await self.tree.sync()

            logger.info(
                "✅ تم مزامنة %s أمر.",
                len(synced)
            )

        except Exception:
            logger.exception(
                "❌ حدث خطأ أثناء مزامنة أوامر Discord."
            )

    async def on_ready(self):
        logger.info(
            "✅ تم تشغيل البوت: %s",
            self.user
        )

        logger.info(
            "🆔 ID: %s",
            self.user.id
        )

        logger.info(
            "🌐 عدد السيرفرات: %s",
            len(self.guilds)
        )

        # حالة البوت
        activity = discord.Game(
            name="/games"
        )

        await self.change_presence(
            status=discord.Status.online,
            activity=activity
        )

    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError
    ):
        # تجاهل الأوامر غير الموجودة
        if isinstance(
            error,
            commands.CommandNotFound
        ):
            return

        logger.error(
            "❌ Command Error: %s",
            error
        )


# ============================================================
# CREATE BOT
# ============================================================

bot = GameBot()


# ============================================================
# START BOT
# ============================================================

async def main():

    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        logger.info(
            "🛑 تم إيقاف البوت."
        )
