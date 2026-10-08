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
# INTENTS
# ============================================================

intents = discord.Intents.default()

# مهم جدًا لألعاب التخمين والكتابة
intents.message_content = True

# مهم لمعرفة رتب الأعضاء
intents.members = True

# غير مطلوب
intents.presences = False


# ============================================================
# BOT
# ============================================================

class GameBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="-",
            intents=intents,
            help_command=None,
            case_insensitive=True
        )

        # ====================================================
        # DATABASE
        # ====================================================

        self.database = Database()

        # ====================================================
        # GAME SYSTEM
        # ====================================================

        self.game_system = GameSystem(self)


    # ========================================================
    # SETUP HOOK
    # ========================================================

    async def setup_hook(self):

        logger.info("🔄 جاري تحميل نظام الألعاب...")

        try:

            await self.game_system.setup()

            logger.info(
                "✅ تم تحميل نظام الألعاب بنجاح."
            )

        except Exception:

            logger.exception(
                "❌ فشل تحميل نظام الألعاب."
            )

            raise

        # ====================================================
        # SYNC SLASH COMMANDS
        # ====================================================

        try:

            synced = await self.tree.sync()

            logger.info(
                "✅ تم مزامنة %s أمر Slash.",
                len(synced)
            )

        except Exception:

            logger.exception(
                "❌ حدث خطأ أثناء مزامنة أوامر Slash."
            )


    # ========================================================
    # READY
    # ========================================================

    async def on_ready(self):

        logger.info("=" * 60)

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

        logger.info("=" * 60)

        # ====================================================
        # STATUS
        # ====================================================

        activity = discord.Game(
            name="-العاب"
        )

        await self.change_presence(
            status=discord.Status.online,
            activity=activity
        )


    # ========================================================
    # COMMAND ERROR
    # ========================================================

    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError
    ):

        # ----------------------------------------------------
        # COMMAND NOT FOUND
        # ----------------------------------------------------

        if isinstance(
            error,
            commands.CommandNotFound
        ):
            return


        # ----------------------------------------------------
        # MISSING PERMISSIONS
        # ----------------------------------------------------

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            try:

                await ctx.send(
                    "❌ ما عندك صلاحية لاستخدام هذا الأمر."
                )

            except Exception:
                pass

            return


        # ----------------------------------------------------
        # CHECK FAILURE
        # ----------------------------------------------------

        if isinstance(
            error,
            commands.CheckFailure
        ):

            try:

                await ctx.send(
                    "❌ ما تقدر تستخدم هذا الأمر هنا."
                )

            except Exception:
                pass

            return


        # ----------------------------------------------------
        # MISSING ARGUMENT
        # ----------------------------------------------------

        if isinstance(
            error,
            commands.MissingRequiredArgument
        ):

            try:

                await ctx.send(
                    "❌ ناقصك أحد الخيارات المطلوبة."
                )

            except Exception:
                pass

            return


        # ----------------------------------------------------
        # BAD ARGUMENT
        # ----------------------------------------------------

        if isinstance(
            error,
            commands.BadArgument
        ):

            try:

                await ctx.send(
                    "❌ البيانات المدخلة غير صحيحة."
                )

            except Exception:
                pass

            return


        # ----------------------------------------------------
        # GENERIC ERROR
        # ----------------------------------------------------

        logger.exception(
            "❌ Command Error:",
            exc_info=error
        )

        try:

            await ctx.send(
                "❌ حدث خطأ أثناء تنفيذ الأمر."
            )

        except Exception:
            pass


# ============================================================
# CREATE BOT
# ============================================================

bot = GameBot()


# ============================================================
# MAIN
# ============================================================

async def main():

    async with bot:

        await bot.start(TOKEN)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        logger.info(
            "🛑 تم إيقاف البوت."
        )

    except Exception:

        logger.exception(
            "❌ توقف البوت بسبب خطأ."
        )
