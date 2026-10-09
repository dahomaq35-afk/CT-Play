# ============================================================
# GAME BOT - MAIN.PY
# Discord Games Bot + Render Web Server
# CTRP Play
# ============================================================
import os
import asyncio
import logging
import threading
import discord
from discord.ext import commands
from flask import Flask, jsonify
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
TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
if not TOKEN:
    raise RuntimeError(
        "لم يتم العثور على DISCORD_TOKEN. "
        "أضف متغير DISCORD_TOKEN في Environment Variables في Render."
    )
# ============================================================
# RENDER PORT
# ============================================================
try:
    PORT = int(os.getenv("PORT", "10000"))
except (TypeError, ValueError):
    PORT = 10000
# ============================================================
# FLASK WEB SERVER
# ============================================================
app = Flask(__name__)
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "service": "CTRP Play",
        "bot": "Discord Games Bot",
        "message": "البوت يعمل بنجاح."
    }), 200
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy"
    }), 200
@app.errorhandler(404)
def page_not_found(_error):
    return jsonify({
        "status": "error",
        "message": "الصفحة غير موجودة."
    }), 404
@app.errorhandler(500)
def internal_server_error(_error):
    logger.exception("حدث خطأ داخلي في Web Server.")
    return jsonify({
        "status": "error",
        "message": "حدث خطأ داخلي في الخادم."
    }), 500
def run_web_server():
    """
    تشغيل Flask في Thread منفصل حتى لا يتوقف البوت.
    """
    try:
        logger.info(
            "تشغيل Web Server على المنفذ %s...",
            PORT
        )
        app.run(
            host="0.0.0.0",
            port=PORT,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception:
        logger.exception(
            "فشل تشغيل Web Server."
        )
# ============================================================
# DISCORD INTENTS
# ============================================================
intents = discord.Intents.default()
# ضروري لألعاب التخمين والكتابة والأوامر النصية.
intents.message_content = True
# ضروري لفحص رتب الأعضاء.
intents.members = True
# غير مطلوب للألعاب.
intents.presences = False
# ============================================================
# BOT CLASS
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
        # منع تكرار إجراءات on_ready عند إعادة الاتصال.
        self._ready_logged = False
    # ========================================================
    # SETUP HOOK
    # ========================================================
    async def setup_hook(self):
        logger.info(
            "جاري تحميل نظام الألعاب..."
        )
        # ----------------------------------------------------
        # LOAD GAME SYSTEM
        # ----------------------------------------------------
        try:
            await self.game_system.setup()
            logger.info(
                "تم تحميل نظام الألعاب بنجاح."
            )
        except Exception:
            logger.exception(
                "فشل تحميل نظام الألعاب."
            )
            raise
        # ----------------------------------------------------
        # SYNC SLASH COMMANDS
        # ----------------------------------------------------
        try:
            synced = await self.tree.sync()
            logger.info(
                "تمت مزامنة %s أمر Slash.",
                len(synced)
            )
        except discord.HTTPException:
            logger.exception(
                "فشلت مزامنة أوامر Slash مع Discord."
            )
        except Exception:
            logger.exception(
                "حدث خطأ غير متوقع أثناء مزامنة أوامر Slash."
            )
    # ========================================================
    # READY EVENT
    # ========================================================
    async def on_ready(self):
        if self.user is None:
            logger.warning(
                "اتصل البوت دون توفر بيانات المستخدم."
            )
            return
        logger.info("=" * 60)
        logger.info(
            "تم تشغيل البوت: %s",
            self.user
        )
        logger.info(
            "ID: %s",
            self.user.id
        )
        logger.info(
            "عدد السيرفرات: %s",
            len(self.guilds)
        )
        logger.info("=" * 60)
        # ----------------------------------------------------
        # BOT STATUS
        # ----------------------------------------------------
        try:
            activity = discord.Game(
                name="-العاب"
            )
            await self.change_presence(
                status=discord.Status.online,
                activity=activity
            )
        except discord.HTTPException:
            logger.exception(
                "تعذر تحديث حالة البوت."
            )
        self._ready_logged = True
    # ========================================================
    # GLOBAL PREFIX COMMAND ERROR HANDLER
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
            except discord.HTTPException:
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
            except discord.HTTPException:
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
            except discord.HTTPException:
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
                    "❌ البيانات المدخلة غير صحيحة. "
                    "تأكد من الروم أو الرتبة أو رقم الخانة."
                )
            except discord.HTTPException:
                pass
            return
        # ----------------------------------------------------
        # COMMAND ON COOLDOWN
        # ----------------------------------------------------
        if isinstance(
            error,
            commands.CommandOnCooldown
        ):
            try:
                await ctx.send(
                    f"⏳ انتظر {error.retry_after:.1f} ثانية "
                    "قبل استخدام الأمر مرة ثانية."
                )
            except discord.HTTPException:
                pass
            return
        # ----------------------------------------------------
        # COMMAND INVOCATION ERROR
        # ----------------------------------------------------
        if isinstance(
            error,
            commands.CommandInvokeError
        ):
            original_error = error.original
            logger.error(
                "حدث خطأ أثناء تنفيذ الأمر %s: %s",
                ctx.command,
                original_error,
                exc_info=(
                    type(original_error),
                    original_error,
                    original_error.__traceback__
                )
            )
            try:
                await ctx.send(
                    "❌ حدث خطأ أثناء تنفيذ الأمر. "
                    "تم تسجيل الخطأ في سجلات البوت."
                )
            except discord.HTTPException:
                pass
            return
        # ----------------------------------------------------
        # GENERIC ERROR
        # ----------------------------------------------------
        logger.error(
            "Command Error: %s",
            error,
            exc_info=(
                type(error),
                error,
                error.__traceback__
            )
        )
        try:
            await ctx.send(
                "❌ حدث خطأ أثناء تنفيذ الأمر."
            )
        except discord.HTTPException:
            pass
    # ========================================================
    # SLASH COMMAND ERROR HANDLER
    # ========================================================
    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError
    ):
        logger.error(
            "Slash Command Error: %s",
            error,
            exc_info=(
                type(error),
                error,
                error.__traceback__
            )
        )
        message = (
            "❌ حدث خطأ أثناء تنفيذ الأمر. "
            "راجع سجلات البوت إذا استمرت المشكلة."
        )
        try:
            if interaction.response.is_done():
                await interaction.followup.send(
                    message,
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    message,
                    ephemeral=True
                )
        except discord.HTTPException:
            logger.exception(
                "تعذر إرسال رسالة خطأ Slash Command."
            )
    # ========================================================
    # SHUTDOWN
    # ========================================================
    async def close(self):
        logger.info(
            "جاري إغلاق البوت..."
        )
        try:
            if self.game_system is not None:
                shutdown_method = getattr(
                    self.game_system,
                    "shutdown",
                    None
                )
                if callable(shutdown_method):
                    result = shutdown_method()
                    if asyncio.iscoroutine(result):
                        await result
        except Exception:
            logger.exception(
                "حدث خطأ أثناء إيقاف الألعاب."
            )
        await super().close()
        logger.info(
            "تم إغلاق اتصال Discord."
        )
# ============================================================
# CREATE BOT
# ============================================================
bot = GameBot()
# ============================================================
# MAIN
# ============================================================
async def main():
    # --------------------------------------------------------
    # START FLASK WEB SERVER IN BACKGROUND
    # --------------------------------------------------------
    web_thread = threading.Thread(
        target=run_web_server,
        daemon=True,
        name="RenderWebServer"
    )
    web_thread.start()
    logger.info(
        "تم تشغيل Thread الخاص بـ Web Server."
    )
    # --------------------------------------------------------
    # START DISCORD BOT
    # --------------------------------------------------------
    try:
        async with bot:
            logger.info(
                "جاري الاتصال بـ Discord..."
            )
            await bot.start(TOKEN)
    except discord.LoginFailure:
        logger.critical(
            "فشل تسجيل الدخول. تحقق من DISCORD_TOKEN."
        )
        raise
    except discord.PrivilegedIntentsRequired:
        logger.critical(
            "البوت يحتاج إلى تفعيل Message Content Intent "
            "و Server Members Intent من Discord Developer Portal."
        )
        raise
    except asyncio.CancelledError:
        logger.info(
            "تم إلغاء مهمة تشغيل البوت."
        )
        raise
    except Exception:
        logger.exception(
            "توقف البوت بسبب خطأ أثناء التشغيل."
        )
        raise
# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    try:
        asyncio.run(
            main()
        )
    except KeyboardInterrupt:
        logger.info(
            "تم إيقاف البوت يدويًا."
        )
    except Exception:
        logger.exception(
            "انتهى تشغيل البوت بسبب خطأ."
        )
