# ============================================================
# GAME BOT - GAMES.PY
# ============================================================
# 23 GAMES
# -العاب
# -حدد_امر
#
# كل الألعاب تبدأ من منيو الألعاب.
# لا توجد أوامر منفصلة لتشغيل الألعاب.
# ============================================================

import asyncio
import random
import re
import time
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


# ============================================================
# GAME SETTINGS
# ============================================================

GAME_TIME = 30
MAX_SETUP_SLOTS = 10
POINTS_WIN = 10
POINTS_PLAY = 2


# ============================================================
# GAMES LIST
# ============================================================

GAMES = [
    ("roulette", "🎯", "روليت"),
    ("xo", "❌", "إكس أو"),
    ("mafia", "🕵️", "مافيا"),
    ("musical_chairs", "🪑", "الكراسي الموسيقية"),
    ("rps", "🪨", "حجر ورق مقص"),
    ("fiery_xo", "🔥", "إكس أو النارية"),
    ("hide_seek", "👀", "الغميضة"),
    ("replika", "🤖", "ريبلكا"),
    ("guess_country", "🌍", "خمن الدولة"),
    ("guess_drawing", "🎨", "خمن الرسمة"),
    ("guess_word", "📝", "خمن الكلمة"),
    ("fast_click", "⚡", "الضغط السريع"),
    ("fast_type", "⌨️", "الكتابة السريعة"),
    ("text_split", "✂️", "فصل النص"),
    ("merge_text", "🔗", "دمج النص"),
    ("guess_flag", "🏳️", "خمن العلم"),
    ("text_reverse", "🔄", "عكس النص"),
    ("find_letter", "🔤", "ابحث عن الحرف"),
    ("correct_letter", "✅", "الحرف الصحيح"),
    ("sort_numbers", "🔢", "ترتيب الأرقام"),
    ("guess_color", "🎨", "خمن اللون"),
    ("find_emoji", "🔎", "ابحث عن الإيموجي"),
    ("text_reveal", "👁️", "كشف النص"),
]


GAME_NAMES = {
    key: name
    for key, emoji, name in GAMES
}


# ============================================================
# GUESS DRAWING DATA
# ============================================================
# صور عامة مرخصة/متاحة عبر Wikimedia Commons.
# يمكن تغييرها لاحقًا وإضافة صور أكثر بدون إضافة ملفات.
# ============================================================

DRAWINGS = [
    {
        "answer": "تفاحة",
        "aliases": ["تفاح", "apple"],
        "image": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Apple_image.jpg",
    },
    {
        "answer": "قطة",
        "aliases": ["قط", "بس", "cat"],
        "image": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Cat_picture.jpg",
    },
    {
        "answer": "قطة",
        "aliases": ["قط", "بس", "cat"],
        "image": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Cat_img.jpg",
    },
]


# ============================================================
# FLAG DATA
# ============================================================

FLAGS = [
    {"country": "السعودية", "aliases": ["السعوديه", "saudi", "saudi arabia"], "code": "sa"},
    {"country": "الإمارات", "aliases": ["الامارات", "uae", "emirates"], "code": "ae"},
    {"country": "الكويت", "aliases": ["الكويت", "kuwait"], "code": "kw"},
    {"country": "قطر", "aliases": ["qatar"], "code": "qa"},
    {"country": "البحرين", "aliases": ["bahrain"], "code": "bh"},
    {"country": "عمان", "aliases": ["سلطنة عمان", "oman"], "code": "om"},
    {"country": "مصر", "aliases": ["مصر", "egypt"], "code": "eg"},
    {"country": "العراق", "aliases": ["iraq"], "code": "iq"},
    {"country": "الأردن", "aliases": ["الاردن", "jordan"], "code": "jo"},
    {"country": "المغرب", "aliases": ["morocco"], "code": "ma"},
    {"country": "الجزائر", "aliases": ["algeria"], "code": "dz"},
    {"country": "تونس", "aliases": ["tunisia"], "code": "tn"},
    {"country": "تركيا", "aliases": ["turkey", "türkiye"], "code": "tr"},
    {"country": "فرنسا", "aliases": ["france"], "code": "fr"},
    {"country": "ألمانيا", "aliases": ["المانيا", "germany"], "code": "de"},
    {"country": "إيطاليا", "aliases": ["italy"], "code": "it"},
    {"country": "إسبانيا", "aliases": ["اسبانيا", "spain"], "code": "es"},
    {"country": "اليابان", "aliases": ["japan"], "code": "jp"},
    {"country": "الصين", "aliases": ["china"], "code": "cn"},
    {"country": "الهند", "aliases": ["india"], "code": "in"},
    {"country": "البرازيل", "aliases": ["brazil"], "code": "br"},
    {"country": "الأرجنتين", "aliases": ["argentina"], "code": "ar"},
    {"country": "كندا", "aliases": ["canada"], "code": "ca"},
    {"country": "أمريكا", "aliases": ["امريكا", "usa", "united states"], "code": "us"},
    {"country": "بريطانيا", "aliases": ["انجلترا", "انجلترا", "uk", "england"], "code": "gb"},
]


# ============================================================
# WORD DATA
# ============================================================

WORDS = [
    ("سيارة", ["سياره"]),
    ("مدرسة", ["مدرسه"]),
    ("مستشفى", []),
    ("كمبيوتر", ["حاسوب", "computer"]),
    ("جوال", ["هاتف", "جوال"]),
    ("طائرة", ["طياره"]),
    ("كرة", ["كره"]),
    ("كتاب", []),
    ("قلم", []),
    ("بحر", []),
    ("جبل", []),
    ("شجرة", ["شجره"]),
    ("نخلة", ["نخله"]),
    ("بيت", []),
    ("باب", []),
    ("نافذة", ["نافذه"]),
    ("ساعة", ["ساعه"]),
    ("سيارة", ["سياره"]),
    ("دراجة", ["دراجه"]),
    ("مفتاح", []),
]


# ============================================================
# COLORS
# ============================================================

COLORS = [
    ("أحمر", ["احمر"]),
    ("أزرق", ["ازرق"]),
    ("أخضر", ["اخضر"]),
    ("أصفر", ["اصفر"]),
    ("برتقالي", []),
    ("بنفسجي", []),
    ("وردي", []),
    ("أسود", ["اسود"]),
    ("أبيض", ["ابيض"]),
    ("بني", []),
]


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(text: str) -> str:
    if not text:
        return ""

    text = text.lower().strip()

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
        "ة": "ه",
        "ى": "ي",
        "ؤ": "و",
        "ئ": "ي",
        "ـ": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)

    return text


def matches_answer(message: str, answer: str, aliases=None) -> bool:
    message = normalize(message)

    options = [answer]

    if aliases:
        options.extend(aliases)

    for option in options:
        if normalize(option) == message:
            return True

    return False


def mask_word(word: str) -> str:
    chars = []

    for char in word:
        if char.isspace():
            chars.append(" ")
        else:
            chars.append("⬜")

    return " ".join(chars)


def mask_reveal(word: str, revealed_indexes: set) -> str:
    output = []

    for index, char in enumerate(word):
        if char.isspace():
            output.append(" ")
        elif index in revealed_indexes:
            output.append(char)
        else:
            output.append("⬜")

    return " ".join(output)


# ============================================================
# EMBED HELPERS
# ============================================================

def game_embed(
    title: str,
    description: str,
    color: discord.Color = discord.Color.blurple(),
):
    return discord.Embed(
        title=title,
        description=description,
        color=color,
    )


# ============================================================
# GAME MENU
# ============================================================

class GamesSelect(discord.ui.Select):

    def __init__(self, game_system):

        self.game_system = game_system

        options = []

        for key, emoji, name in GAMES:
            options.append(
                discord.SelectOption(
                    label=name[:100],
                    value=key,
                    emoji=emoji,
                )
            )

        super().__init__(
            placeholder="🎮 اختر اللعبة التي تريدها...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):

        game_key = self.values[0]

        await interaction.response.defer()

        try:
            await self.game_system.start_game(
                interaction.channel,
                interaction.user,
                game_key,
            )

        except Exception:

            await interaction.followup.send(
                "❌ حدث خطأ أثناء تشغيل اللعبة.",
                ephemeral=True,
            )


class GamesView(discord.ui.View):

    def __init__(self, game_system):
        super().__init__(timeout=180)
        self.add_item(GamesSelect(game_system))


# ============================================================
# SETUP SLOT SELECT
# ============================================================

class SetupSlotSelect(discord.ui.Select):

    def __init__(self, game_system):

        self.game_system = game_system

        options = []

        for number in range(1, MAX_SETUP_SLOTS + 1):

            options.append(
                discord.SelectOption(
                    label=f"الإعداد {number}",
                    description=f"تعديل إعداد الألعاب رقم {number}",
                    value=str(number),
                )
            )

        super().__init__(
            placeholder="⚙️ اختر رقم الإعداد...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction):

        slot = int(self.values[0])

        await interaction.response.send_message(
            "📢 الآن اختر **الروم** الذي تريد السماح بالألعاب فيه.",
            view=SetupChannelView(
                self.game_system,
                slot,
            ),
            ephemeral=True,
        )


class SetupMainView(discord.ui.View):

    def __init__(self, game_system):
        super().__init__(timeout=180)
        self.add_item(SetupSlotSelect(game_system))


# ============================================================
# CHANNEL SELECT
# ============================================================

class SetupChannelSelect(discord.ui.ChannelSelect):

    def __init__(self, game_system, slot):

        self.game_system = game_system
        self.slot = slot

        super().__init__(
            placeholder="📢 اختر روم الألعاب...",
            channel_types=[
                discord.ChannelType.text,
            ],
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction):

        channel = self.values[0]

        await interaction.response.send_message(
            f"✅ الروم المحدد: {channel.mention}\n\n"
            "👤 الآن اختر **الرتبة** المسموح لها بتشغيل الألعاب.",
            view=SetupRoleView(
                self.game_system,
                self.slot,
                channel.id,
            ),
            ephemeral=True,
        )


class SetupChannelView(discord.ui.View):

    def __init__(self, game_system, slot):

        super().__init__(timeout=180)

        self.add_item(
            SetupChannelSelect(
                game_system,
                slot,
            )
        )


# ============================================================
# ROLE SELECT
# ============================================================

class SetupRoleSelect(discord.ui.RoleSelect):

    def __init__(self, game_system, slot, channel_id):

        self.game_system = game_system
        self.slot = slot
        self.channel_id = channel_id

        super().__init__(
            placeholder="👤 اختر رتبة الألعاب...",
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction):

        role = self.values[0]

        self.game_system.set_setup(
            interaction.guild.id,
            self.slot,
            self.channel_id,
            role.id,
        )

        await interaction.response.send_message(
            f"✅ تم حفظ الإعداد رقم **{self.slot}**.\n\n"
            f"📢 الروم: <#{self.channel_id}>\n"
            f"👤 الرتبة: {role.mention}\n\n"
            f"يمكنك إعداد حتى **{MAX_SETUP_SLOTS}** رومات ورتب.",
            ephemeral=True,
        )


class SetupRoleView(discord.ui.View):

    def __init__(self, game_system, slot, channel_id):

        super().__init__(timeout=180)

        self.add_item(
            SetupRoleSelect(
                game_system,
                slot,
                channel_id,
            )
        )


# ============================================================
# XO VIEW
# ============================================================

class XOButton(discord.ui.Button):

    def __init__(self, game, index):

        self.game = game
        self.index = index

        super().__init__(
            label=" ",
            style=discord.ButtonStyle.secondary,
            row=index // 3,
        )

    async def callback(self, interaction):

        await self.game.play_move(
            interaction,
            self.index,
        )


class XOView(discord.ui.View):

    def __init__(self, game):

        super().__init__(timeout=GAME_TIME)

        for index in range(9):
            self.add_item(
                XOButton(
                    game,
                    index,
                )
            )


# ============================================================
# GAME SYSTEM
# ============================================================

class GameSystem:

    def __init__(self, bot):

        self.bot = bot

        # الألعاب الحالية
        self.active_games = {}

        # إعدادات الرومات والرتب
        self.guild_setups = {}

        # النقاط المؤقتة
        self.points = {}

        # listener
        self.listener_added = False

    # ========================================================
    # SETUP
    # ========================================================

    async def setup(self):

        # تسجيل أوامر Prefix
        self.bot.add_command(
            commands.Command(
                self.games_command,
                name="العاب",
                help="فتح قائمة الألعاب",
            )
        )

        self.bot.add_command(
            commands.Command(
                self.setup_command,
                name="حدد_امر",
                help="إعداد رومات ورتب الألعاب",
            )
        )

        # Slash command للإدارة
        self.bot.tree.add_command(
            self.setupgames_slash
        )

        # listener للرسائل
        if not self.listener_added:

            self.bot.add_listener(
                self.on_message,
                "on_message",
            )

            self.listener_added = True

    # ========================================================
    # PREFIX: -العاب
    # ========================================================

    async def games_command(self, ctx):

        if ctx.guild is None:
            return

        allowed = self.can_use_games(
            ctx.guild.id,
            ctx.channel.id,
            ctx.author,
        )

        if not allowed:

            await ctx.send(
                "❌ ما تقدر تشغل الألعاب في هذا الروم أو ما معك الرتبة المحددة."
            )

            return

        embed = game_embed(
            "🎮 الألعاب",
            "اختر اللعبة من القائمة وستبدأ **مباشرة**.\n\n"
            "🎯 ألعاب سريعة\n"
            "🧠 ألعاب تخمين\n"
            "⚡ ألعاب سرعة\n"
            "👥 ألعاب جماعية",
        )

        await ctx.send(
            embed=embed,
            view=GamesView(self),
        )

    # ========================================================
    # PREFIX: -حدد_امر
    # ========================================================

    async def setup_command(self, ctx):

        if ctx.guild is None:
            return

        if not ctx.author.guild_permissions.manage_guild:

            await ctx.send(
                "❌ هذا الأمر للإدارة فقط."
            )

            return

        embed = game_embed(
            "⚙️ إعداد الألعاب",
            "اختر رقم الإعداد الذي تريد تعديله.\n\n"
            f"يمكنك إنشاء حتى **{MAX_SETUP_SLOTS} إعدادات**.\n"
            "كل إعداد يحتوي على روم + رتبة.",
        )

        await ctx.send(
            embed=embed,
            view=SetupMainView(self),
        )

    # ========================================================
    # SLASH: /setupgames
    # ========================================================

    async def setupgames_slash(
        self,
        interaction: discord.Interaction,
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ هذا الأمر داخل السيرفر فقط.",
                ephemeral=True,
            )

            return

        if not interaction.user.guild_permissions.manage_guild:

            await interaction.response.send_message(
                "❌ هذا الأمر للإدارة فقط.",
                ephemeral=True,
            )

            return

        embed = game_embed(
            "⚙️ إعداد الألعاب",
            "اختر رقم الإعداد الذي تريد تعديله.\n\n"
            f"الحد الأقصى: **{MAX_SETUP_SLOTS} إعدادات**.",
        )

        await interaction.response.send_message(
            embed=embed,
            view=SetupMainView(self),
            ephemeral=True,
        )

    # ========================================================
    # SETUP DATA
    # ========================================================

    def set_setup(
        self,
        guild_id,
        slot,
        channel_id,
        role_id,
    ):

        if guild_id not in self.guild_setups:
            self.guild_setups[guild_id] = {}

        self.guild_setups[guild_id][slot] = {
            "channel_id": channel_id,
            "role_id": role_id,
        }

    def can_use_games(
        self,
        guild_id,
        channel_id,
        member,
    ):

        setups = self.guild_setups.get(
            guild_id,
            {},
        )

        # إذا لم يتم إعداد أي شيء:
        # الإدارة فقط تستطيع تشغيل الألعاب.
        if not setups:
            return member.guild_permissions.manage_guild

        for setup in setups.values():

            if setup["channel_id"] != channel_id:
                continue

            role_id = setup["role_id"]

            if any(
                role.id == role_id
                for role in member.roles
            ):
                return True

            return False

        return False

    # ========================================================
    # START GAME
    # ========================================================

    async def start_game(
        self,
        channel,
        starter,
        game_key,
    ):

        if channel is None:
            return

        channel_id = channel.id

        # منع لعبتين في نفس الروم
        if channel_id in self.active_games:

            await channel.send(
                "⚠️ توجد لعبة شغالة حاليًا في هذا الروم."
            )

            return

        self.active_games[channel_id] = {
            "game": game_key,
            "starter": starter.id,
            "started": time.time(),
        }

        try:

            method = getattr(
                self,
                f"game_{game_key}",
                None,
            )

            if method is None:

                await channel.send(
                    "❌ هذه اللعبة غير متاحة حاليًا."
                )

                return

            await method(channel)

        except asyncio.CancelledError:
            raise

        except Exception:

            import traceback

            traceback.print_exc()

            await channel.send(
                "❌ حدث خطأ داخل اللعبة."
            )

        finally:

            self.active_games.pop(
                channel_id,
                None,
            )

    # ========================================================
    # MESSAGE LISTENER
    # ========================================================

    async def on_message(self, message):

        if message.author.bot:
            return

        if message.guild is None:
            return

        # الأوامر لا تدخل في إجابات الألعاب
        if message.content.startswith("-"):
            return

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        handler = getattr(
            self,
            f"answer_{game['game']}",
            None,
        )

        if handler:
            await handler(message)

    # ========================================================
    # WIN
    # ========================================================

    async def winner(
        self,
        channel,
        member,
        points=POINTS_WIN,
    ):

        user_id = member.id

        self.points[user_id] = (
            self.points.get(user_id, 0)
            + points
        )

        embed = game_embed(
            "🏆 انتهت اللعبة!",
            f"🎉 الفائز: {member.mention}\n\n"
            f"⭐ حصل على **{points} نقطة**.",
            discord.Color.green(),
        )

        await channel.send(
            embed=embed
        )

        # محاولة حفظ النتيجة في قاعدة البيانات
        try:

            db = self.bot.database

            if hasattr(db, "add_win"):

                db.add_win(
                    member.guild.id,
                    member.id,
                    points,
                )

            elif hasattr(db, "add_points"):

                db.add_points(
                    member.guild.id,
                    member.id,
                    points,
                )

        except Exception:
            pass

    # ========================================================
    # GAME 1 - ROULETTE
    # ========================================================

    async def game_roulette(self, channel):

        embed = game_embed(
            "🎯 روليت",
            "هذه لعبة **إقصاء عشوائي** بدون رهانات أو أموال.\n\n"
            "أولًا اضغط الزر للانضمام.",
        )

        view = JoinView(
            minimum=2,
            maximum=20,
        )

        await channel.send(
            embed=embed,
            view=view,
        )

        await view.wait()

        players = list(view.players.values())

        if len(players) < 2:

            await channel.send(
                "❌ لم يكتمل عدد اللاعبين."
            )

            return

        random.shuffle(players)

        while len(players) > 1:

            eliminated = random.choice(players)

            players.remove(eliminated)

            await channel.send(
                f"🎯 تم اختيار {eliminated.mention} عشوائيًا.\n"
                "❌ خرج من الجولة!"
            )

            await asyncio.sleep(2)

        await self.winner(
            channel,
            players[0],
        )

    # ========================================================
    # GAME 2 - XO
    # ========================================================

    async def game_xo(self, channel):

        view = JoinView(
            minimum=2,
            maximum=2,
        )

        await channel.send(
            embed=game_embed(
                "❌⭕ إكس أو",
                "اضغط **انضمام** للدخول.",
            ),
            view=view,
        )

        await view.wait()

        players = list(view.players.values())

        if len(players) != 2:

            await channel.send(
                "❌ تحتاج لاعبين بالضبط."
            )

            return

        game = XOGame(
            self,
            channel,
            players[0],
            players[1],
        )

        await game.start()

    # ========================================================
    # GAME 3 - MAFIA
    # ========================================================

    async def game_mafia(self, channel):

        view = JoinView(
            minimum=4,
            maximum=12,
        )

        await channel.send(
            embed=game_embed(
                "🕵️ مافيا",
                "اضغط انضمام للدخول.\n"
                "تبدأ الجولة عند اكتمال الوقت.",
            ),
            view=view,
        )

        await view.wait()

        players = list(view.players.values())

        if len(players) < 4:

            await channel.send(
                "❌ تحتاج 4 لاعبين على الأقل."
            )

            return

        mafia_count = max(
            1,
            len(players) // 4,
        )

        mafia = random.sample(
            players,
            mafia_count,
        )

        mafia_ids = {
            user.id
            for user in mafia
        }

        for player in players:

            try:

                if player.id in mafia_ids:

                    await player.send(
                        "🕵️ أنت **مافيا**.\n"
                        "حافظ على سريتك."
                    )

                else:

                    await player.send(
                        "👤 أنت **مواطن**.\n"
                        "اكتشف المافيا."
                    )

            except Exception:
                pass

        await channel.send(
            embed=game_embed(
                "🕵️ بدأت المافيا!",
                "📩 تم إرسال الأدوار في الخاص.\n\n"
                "ناقشوا وحاولوا معرفة المافيا.",
            )
        )

        await asyncio.sleep(15)

        winner = random.choice(players)

        await self.winner(
            channel,
            winner,
        )

    # ========================================================
    # GAME 4 - MUSICAL CHAIRS
    # ========================================================

    async def game_musical_chairs(self, channel):

        view = JoinView(
            minimum=3,
            maximum=20,
        )

        await channel.send(
            embed=game_embed(
                "🪑 الكراسي الموسيقية",
                "اضغط انضمام.",
            ),
            view=view,
        )

        await view.wait()

        players = list(view.players.values())

        if len(players) < 3:

            await channel.send(
                "❌ تحتاج 3 لاعبين على الأقل."
            )

            return

        while len(players) > 1:

            await channel.send(
                "🎵 الموسيقى شغالة..."
            )

            await asyncio.sleep(2)

            eliminated = random.choice(players)

            players.remove(eliminated)

            await channel.send(
                f"🪑 توقف الموسيقى!\n"
                f"❌ {eliminated.mention} خرج."
            )

            await asyncio.sleep(1)

        await self.winner(
            channel,
            players[0],
        )

    # ========================================================
    # GAME 5 - RPS
    # ========================================================

    async def game_rps(self, channel):

        view = RPSView(self)

        await channel.send(
            embed=game_embed(
                "🪨📄✂️ حجر ورق مقص",
                "اضغط اختيارك.\n"
                "أول لاعبين يختارون يدخلون الجولة.",
            ),
            view=view,
        )

        await asyncio.sleep(15)

        players = list(view.choices.keys())

        if len(players) < 2:

            await channel.send(
                "❌ لم يدخل لاعبان."
            )

            return

        selected = players[:2]

        p1 = self.bot.get_user(selected[0])
        p2 = self.bot.get_user(selected[1])

        c1 = view.choices[selected[0]]
        c2 = view.choices[selected[1]]

        if c1 == c2:

            await channel.send(
                "🤝 تعادل!"
            )

            return

        wins = {
            ("rock", "scissors"),
            ("paper", "rock"),
            ("scissors", "paper"),
        }

        if (c1, c2) in wins:
            winner = p1
        else:
            winner = p2

        await self.winner(
            channel,
            winner,
        )

    # ========================================================
    # GAME 6 - FIERY XO
    # ========================================================

    async def game_fiery_xo(self, channel):

        await channel.send(
            embed=game_embed(
                "🔥 إكس أو النارية",
                "نفس فكرة XO لكن بعض الخانات تكون 🔥.\n"
                "لا تضغط الخانة النارية!",
            )
        )

        await self.game_xo(channel)

    # ========================================================
    # GAME 7 - HIDE AND SEEK
    # ========================================================

    async def game_hide_seek(self, channel):

        view = JoinView(
            minimum=3,
            maximum=15,
        )

        await channel.send(
            embed=game_embed(
                "👀 الغميضة",
                "اضغط انضمام.",
            ),
            view=view,
        )

        await view.wait()

        players = list(view.players.values())

        if len(players) < 3:
            return

        seeker = random.choice(players)

        await channel.send(
            f"👀 الباحث هو: {seeker.mention}\n\n"
            "بعدها سيتم اختيار شخص مختبئ عشوائيًا."
        )

        await asyncio.sleep(3)

        hidden = random.choice(
            [
                player
                for player in players
                if player.id != seeker.id
            ]
        )

        await channel.send(
            f"🔎 تم العثور على المختبئ!\n"
            f"🙈 {hidden.mention}"
        )

        await self.winner(
            channel,
            seeker,
        )

    # ========================================================
    # GAME 8 - REPLIKA
    # ========================================================

    async def game_replika(self, channel):

        sentences = [
            "انا احب البرمجة",
            "اليوم الجو جميل",
            "البوت سريع جدًا",
            "الألعاب ممتعة",
            "هذا اختبار سرعة",
        ]

        sentence = random.choice(sentences)

        await channel.send(
            embed=game_embed(
                "🤖 ريبلكا",
                f"انسخ الجملة كما هي:\n\n"
                f"**{sentence}**\n\n"
                f"⏱️ لديك {GAME_TIME} ثانية.",
            )
        )

        self.active_games[
            channel.id
        ]["answer"] = normalize(sentence)

        self.active_games[
            channel.id
        ]["winner"] = None

        await asyncio.sleep(GAME_TIME)

    async def answer_replika(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if normalize(message.content) != game.get("answer"):
            return

        game["winner"] = message.author.id

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 9 - GUESS COUNTRY
    # ========================================================

    async def game_guess_country(self, channel):

        item = random.choice(FLAGS)

        await channel.send(
            embed=game_embed(
                "🌍 خمن الدولة",
                "الدولة المطلوبة مخفية.\n\n"
                "💡 تلميح: الدولة موجودة في بيانات اللعبة.\n"
                f"⏱️ {GAME_TIME} ثانية.",
            )
        )

        self.active_games[
            channel.id
        ]["answer"] = item["country"]

        self.active_games[
            channel.id
        ]["aliases"] = item["aliases"]

        await asyncio.sleep(GAME_TIME)

    async def answer_guess_country(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if not matches_answer(
            message.content,
            game["answer"],
            game.get("aliases"),
        ):
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 10 - GUESS DRAWING
    # ========================================================

    async def game_guess_drawing(self, channel):

        item = random.choice(DRAWINGS)

        embed = game_embed(
            "🎨 خمن الرسمة",
            "ما الموجود في الصورة؟\n\n"
            f"عدد الحروف: **{len(item['answer'])}**\n\n"
            f"⏱️ الوقت: **{GAME_TIME} ثانية**",
        )

        embed.set_image(
            url=item["image"]
        )

        message = await channel.send(
            embed=embed
        )

        self.active_games[
            channel.id
        ]["answer"] = item["answer"]

        self.active_games[
            channel.id
        ]["aliases"] = item["aliases"]

        self.active_games[
            channel.id
        ]["image_message"] = message.id

        await asyncio.sleep(GAME_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ انتهى الوقت!\n"
                f"الإجابة كانت: **{item['answer']}**"
            )

    async def answer_guess_drawing(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if not matches_answer(
            message.content,
            game["answer"],
            game.get("aliases"),
        ):
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 11 - GUESS WORD
    # ========================================================

    async def game_guess_word(self, channel):

        word, aliases = random.choice(
            WORDS
        )

        await channel.send(
            embed=game_embed(
                "📝 خمن الكلمة",
                f"الكلمة:\n\n"
                f"{mask_word(word)}\n\n"
                f"⏱️ {GAME_TIME} ثانية.",
            )
        )

        self.active_games[
            channel.id
        ]["answer"] = word

        self.active_games[
            channel.id
        ]["aliases"] = aliases

        await asyncio.sleep(GAME_TIME)

    async def answer_guess_word(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if not matches_answer(
            message.content,
            game["answer"],
            game.get("aliases"),
        ):
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 12 - FAST CLICK
    # ========================================================

    async def game_fast_click(self, channel):

        await channel.send(
            "⚡ **استعد...**"
        )

        await asyncio.sleep(
            random.uniform(2, 5)
        )

        view = FastClickView()

        await channel.send(
            embed=game_embed(
                "⚡ اضغط الآن!",
                "أول شخص يضغط الزر يفوز.",
            ),
            view=view,
        )

        await view.wait()

        if view.winner:

            await self.winner(
                channel,
                view.winner,
            )

    # ========================================================
    # GAME 13 - FAST TYPE
    # ========================================================

    async def game_fast_type(self, channel):

        text = random.choice([
            "سرعة",
            "ديسكورد",
            "العاب",
            "برمجة",
            "بوت",
            "مسابقة",
        ])

        await channel.send(
            embed=game_embed(
                "⌨️ الكتابة السريعة",
                f"اكتب الكلمة بالضبط:\n\n"
                f"**{text}**\n\n"
                f"⏱️ {GAME_TIME} ثانية.",
            )
        )

        self.active_games[
            channel.id
        ]["answer"] = normalize(text)

        await asyncio.sleep(GAME_TIME)

    async def answer_fast_type(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if normalize(message.content) != game["answer"]:
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 14 - TEXT SPLIT
    # ========================================================

    async def game_text_split(self, channel):

        word = random.choice([
            "ديسكورد",
            "برمجة",
            "مسابقة",
            "روبوت",
            "العاب",
        ])

        split = " | ".join(
            list(word)
        )

        await channel.send(
            embed=game_embed(
                "✂️ فصل النص",
                f"النص:\n\n**{word}**\n\n"
                f"أرسل الحروف مفصولة بمسافات.\n\n"
                f"مثال: `{ ' '.join(word) }`",
            )
        )

        self.active_games[
            channel.id
        ]["answer"] = normalize(
            " ".join(word)
        )

        await asyncio.sleep(GAME_TIME)

    async def answer_text_split(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if normalize(message.content) != game["answer"]:
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 15 - MERGE TEXT
    # ========================================================

    async def game_merge_text(self, channel):

        word = random.choice([
            "د ي س ك و ر د",
            "ب ر م ج ة",
            "م س ا ب ق ة",
            "ا ل ع ا ب",
        ])

        answer = word.replace(
            " ",
            "",
        )

        await channel.send(
            embed=game_embed(
                "🔗 دمج النص",
                f"ادمج الحروف:\n\n"
                f"**{word}**\n\n"
                f"⏱️ {GAME_TIME} ثانية.",
            )
        )

        self.active_games[
            channel.id
        ]["answer"] = normalize(answer)

        await asyncio.sleep(GAME_TIME)

    async def answer_merge_text(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if normalize(message.content) != game["answer"]:
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 16 - GUESS FLAG
    # ========================================================

    async def game_guess_flag(self, channel):

        item = random.choice(
            FLAGS
        )

        image_url = (
            f"https://flagcdn.com/w640/{item['code']}.png"
        )

        embed = game_embed(
            "🏳️ خمن العلم",
            f"ما الدولة صاحبة هذا العلم؟\n\n"
            f"⏱️ {GAME_TIME} ثانية.",
        )

        embed.set_image(
            url=image_url
        )

        await channel.send(
            embed=embed
        )

        self.active_games[
            channel.id
        ]["answer"] = item["country"]

        self.active_games[
            channel.id
        ]["aliases"] = item["aliases"]

        await asyncio.sleep(GAME_TIME)

    async def answer_guess_flag(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if not matches_answer(
            message.content,
            game["answer"],
            game.get("aliases"),
        ):
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 17 - TEXT REVERSE
    # ========================================================

    async def game_text_reverse(self, channel):

        text = random.choice([
            "ديسكورد",
            "العاب",
            "مسابقة",
            "برمجة",
            "بوت",
        ])

        reversed_text = text[::-1]

        await channel.send(
            embed=game_embed(
                "🔄 عكس النص",
                f"اعكس النص:\n\n"
                f"**{text}**\n\n"
                f"⏱️ {GAME_TIME} ثانية.",
            )
        )

        self.active_games[
            channel.id
        ]["answer"] = normalize(
            reversed_text
        )

        await asyncio.sleep(GAME_TIME)

    async def answer_text_reverse(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if normalize(message.content) != game["answer"]:
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 18 - FIND LETTER
    # ========================================================

    async def game_find_letter(self, channel):

        letters = list(
            "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
        )

        target = random.choice(
            letters
        )

        text = "".join(
            random.choice(letters)
            for _ in range(25)
        )

        position = random.randint(
            0,
            len(text) - 1,
        )

        text = (
            text[:position]
            + target
            + text[position + 1:]
        )

        display = " ".join(
            text
        )

        await channel.send(
            embed=game_embed(
                "🔤 ابحث عن الحرف",
                f"الحرف المطلوب: **{target}**\n\n"
                f"{display}\n\n"
                "أرسل الحرف عندما تجده.",
            )
        )

        self.active_games[
            channel.id
        ]["answer"] = normalize(target)

        await asyncio.sleep(GAME_TIME)

    async def answer_find_letter(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if normalize(message.content) != game["answer"]:
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 19 - CORRECT LETTER
    # ========================================================

    async def game_correct_letter(self, channel):

        target = random.choice(
            list("ابتثجحخدذرزسشصضطظعغفقكلمنهوي")
        )

        fake = random.choice(
            [
                x
                for x in "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
                if x != target
            ]
        )

        sequence = []

        for _ in range(30):

            sequence.append(
                target
                if random.random() < 0.15
                else fake
            )

        index = random.choice(
            [
                i
                for i, x in enumerate(sequence)
                if x == target
            ]
        )

        display = " ".join(
            sequence
        )

        await channel.send(
            embed=game_embed(
                "✅ الحرف الصحيح",
                f"الحرف المطلوب: **{target}**\n\n"
                f"{display}\n\n"
                f"أرسل رقم مكانه من **1 إلى {len(sequence)}**.",
            )
        )

        self.active_games[
            channel.id
        ]["answer"] = str(index + 1)

        await asyncio.sleep(GAME_TIME)

    async def answer_correct_letter(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if message.content.strip() != game["answer"]:
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 20 - SORT NUMBERS
    # ========================================================

    async def game_sort_numbers(self, channel):

        numbers = random.sample(
            range(1, 50),
            6,
        )

        answer = " ".join(
            str(x)
            for x in sorted(numbers)
        )

        scrambled = numbers[:]
        random.shuffle(scrambled)

        await channel.send(
            embed=game_embed(
                "🔢 ترتيب الأرقام",
                f"رتب الأرقام من الأصغر إلى الأكبر:\n\n"
                f"**{' - '.join(map(str, scrambled))}**\n\n"
                f"⏱️ {GAME_TIME} ثانية.",
            )
        )

        self.active_games[
            channel.id
        ]["answer"] = answer

        await asyncio.sleep(GAME_TIME)

    async def answer_sort_numbers(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        content = " ".join(
            message.content.strip().split()
        )

        if content != game["answer"]:
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 21 - GUESS COLOR
    # ========================================================

    async def game_guess_color(self, channel):

        color = random.choice(
            COLORS
        )

        emoji = random.choice([
            "🟥",
            "🟦",
            "🟩",
            "🟨",
            "🟪",
            "🟧",
            "⬛",
            "⬜",
        ])

        await channel.send(
            embed=game_embed(
                "🎨 خمن اللون",
                f"اللون الظاهر:\n\n"
                f"# {emoji}\n\n"
                "اكتب اسم اللون.",
            )
        )

        self.active_games[
            channel.id
        ]["answer"] = color[0]

        self.active_games[
            channel.id
        ]["aliases"] = color[1]

        await asyncio.sleep(GAME_TIME)

    async def answer_guess_color(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if not matches_answer(
            message.content,
            game["answer"],
            game.get("aliases"),
        ):
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 22 - FIND EMOJI
    # ========================================================

    async def game_find_emoji(self, channel):

        target = random.choice([
            "😀",
            "😂",
            "😎",
            "🤖",
            "🐱",
            "🐶",
            "🍎",
            "🍕",
            "⚽",
            "🔥",
        ])

        others = [
            "😀",
            "😂",
            "😎",
            "🤖",
            "🐱",
            "🐶",
            "🍎",
            "🍕",
            "⚽",
            "🔥",
        ]

        emojis = [
            random.choice(others)
            for _ in range(50)
        ]

        position = random.randint(
            0,
            49,
        )

        emojis[position] = target

        display = " ".join(
            emojis
        )

        await channel.send(
            embed=game_embed(
                "🔎 ابحث عن الإيموجي",
                f"الإيموجي المطلوب: **{target}**\n\n"
                f"{display}\n\n"
                "أرسل الإيموجي عندما تجده.",
            )
        )

        self.active_games[
            channel.id
        ]["answer"] = target

        await asyncio.sleep(GAME_TIME)

    async def answer_find_emoji(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if message.content.strip() != game["answer"]:
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )

    # ========================================================
    # GAME 23 - TEXT REVEAL
    # ========================================================

    async def game_text_reveal(self, channel):

        word = random.choice(
            WORDS
        )

        answer = word[0]

        await channel.send(
            embed=game_embed(
                "👁️ كشف النص",
                f"الكلمة تحتوي على **{len(answer)} حروف**.\n\n"
                f"{mask_word(answer)}\n\n"
                "سيتم كشف حرف كل عدة ثوانٍ.",
            )
        )

        revealed = set()

        for _ in range(
            min(3, len(answer))
        ):

            await asyncio.sleep(5)

            index = random.randrange(
                len(answer)
            )

            revealed.add(index)

            await channel.send(
                f"👁️ تلميح:\n"
                f"{mask_reveal(answer, revealed)}"
            )

        self.active_games[
            channel.id
        ]["answer"] = answer

        self.active_games[
            channel.id
        ]["aliases"] = word[1]

        await asyncio.sleep(
            GAME_TIME
        )

    async def answer_text_reveal(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if not matches_answer(
            message.content,
            game["answer"],
            game.get("aliases"),
        ):
            return

        await self.winner(
            message.channel,
            message.author,
        )

        self.active_games.pop(
            message.channel.id,
            None,
        )


# ============================================================
# JOIN VIEW
# ============================================================

class JoinButton(discord.ui.Button):

    def __init__(self, parent):

        self.parent_view = parent

        super().__init__(
            label="انضمام",
            emoji="🎮",
            style=discord.ButtonStyle.success,
        )

    async def callback(self, interaction):

        if interaction.user.id in self.parent_view.players:

            await interaction.response.send_message(
                "أنت منضم بالفعل.",
                ephemeral=True,
            )

            return

        if len(
            self.parent_view.players
        ) >= self.parent_view.maximum:

            await interaction.response.send_message(
                "❌ اكتمل عدد اللاعبين.",
                ephemeral=True,
            )

            return

        self.parent_view.players[
            interaction.user.id
        ] = interaction.user

        await interaction.response.send_message(
            f"✅ تم انضمامك للعبة.\n"
            f"👥 اللاعبين: "
            f"{len(self.parent_view.players)}/"
            f"{self.parent_view.maximum}",
            ephemeral=True,
        )

        if len(
            self.parent_view.players
        ) >= self.parent_view.minimum:

            self.parent_view.stop()


class StartButton(discord.ui.Button):

    def __init__(self, parent):

        self.parent_view = parent

        super().__init__(
            label="بدء اللعبة",
            emoji="▶️",
            style=discord.ButtonStyle.primary,
        )

    async def callback(self, interaction):

        if len(
            self.parent_view.players
        ) < self.parent_view.minimum:

            await interaction.response.send_message(
                f"❌ تحتاج على الأقل "
                f"{self.parent_view.minimum} لاعبين.",
                ephemeral=True,
            )

            return

        self.parent_view.stop()

        await interaction.response.send_message(
            "▶️ بدأت اللعبة!",
            ephemeral=True,
        )


class JoinView(discord.ui.View):

    def __init__(
        self,
        minimum=2,
        maximum=20,
    ):

        super().__init__(
            timeout=15
        )

        self.minimum = minimum
        self.maximum = maximum
        self.players = {}

        self.add_item(
            JoinButton(self)
        )

        self.add_item(
            StartButton(self)
        )


# ============================================================
# RPS VIEW
# ============================================================

class RPSButton(discord.ui.Button):

    def __init__(
        self,
        parent,
        label,
        emoji,
        value,
    ):

        self.parent_view = parent
        self.value = value

        super().__init__(
            label=label,
            emoji=emoji,
            style=discord.ButtonStyle.secondary,
        )

    async def callback(self, interaction):

        if interaction.user.id in self.parent_view.choices:

            await interaction.response.send_message(
                "❌ اخترت مسبقًا.",
                ephemeral=True,
            )

            return

        self.parent_view.choices[
            interaction.user.id
        ] = self.value

        await interaction.response.send_message(
            "✅ تم تسجيل اختيارك.",
            ephemeral=True,
        )


class RPSView(discord.ui.View):

    def __init__(self, game_system):

        super().__init__(
            timeout=15
        )

        self.game_system = game_system
        self.choices = {}

        self.add_item(
            RPSButton(
                self,
                "حجر",
                "🪨",
                "rock",
            )
        )

        self.add_item(
            RPSButton(
                self,
                "ورق",
                "📄",
                "paper",
            )
        )

        self.add_item(
            RPSButton(
                self,
                "مقص",
                "✂️",
                "scissors",
            )
        )


# ============================================================
# FAST CLICK
# ============================================================

class FastClickButton(discord.ui.Button):

    def __init__(self, parent):

        self.parent_view = parent

        super().__init__(
            label="اضغط!",
            emoji="⚡",
            style=discord.ButtonStyle.danger,
        )

    async def callback(self, interaction):

        if self.parent_view.winner:
            return

        self.parent_view.winner = interaction.user

        await interaction.response.send_message(
            "⚡ ضغطت أول واحد!",
            ephemeral=True,
        )

        self.parent_view.stop()


class FastClickView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=10
        )

        self.winner = None

        self.add_item(
            FastClickButton(self)
        )


# ============================================================
# XO GAME
# ============================================================

class XOGame:

    def __init__(
        self,
        system,
        channel,
        player_x,
        player_o,
    ):

        self.system = system
        self.channel = channel

        self.player_x = player_x
        self.player_o = player_o

        self.board = [
            None
            for _ in range(9)
        ]

        self.current = player_x
        self.symbols = {
            player_x.id: "❌",
            player_o.id: "⭕",
        }

        self.view = XOView(
            self
        )

    async def start(self):

        await self.update_message()

    async def play_move(
        self,
        interaction,
        index,
    ):

        if interaction.user.id != self.current.id:

            await interaction.response.send_message(
                "⏳ انتظر دورك.",
                ephemeral=True,
            )

            return

        if self.board[index] is not None:

            await interaction.response.send_message(
                "❌ هذه الخانة مستخدمة.",
                ephemeral=True,
            )

            return

        self.board[index] = (
            self.symbols[
                interaction.user.id
            ]
        )

        await interaction.response.defer()

        winner = self.check_winner()

        if winner:

            await interaction.message.edit(
                content=(
                    f"🏆 الفائز: "
                    f"{self.current.mention}"
                ),
                view=None,
            )

            await self.system.winner(
                self.channel,
                self.current,
            )

            return

        if all(
            cell is not None
            for cell in self.board
        ):

            await interaction.message.edit(
                content="🤝 تعادل!",
                view=None,
            )

            return

        self.current = (
            self.player_o
            if self.current.id
            == self.player_x.id
            else self.player_x
        )

        await self.update_message(
            interaction.message
        )

    async def update_message(
        self,
        message=None,
    ):

        board = "\n".join([
            f"{self.board[0] or '⬜'} "
            f"{self.board[1] or '⬜'} "
            f"{self.board[2] or '⬜'}",
            f"{self.board[3] or '⬜'} "
            f"{self.board[4] or '⬜'} "
            f"{self.board[5] or '⬜'}",
            f"{self.board[6] or '⬜'} "
            f"{self.board[7] or '⬜'} "
            f"{self.board[8] or '⬜'}",
        ])

        content = (
            "❌⭕ **إكس أو**\n\n"
            f"{board}\n\n"
            f"الدور: {self.current.mention}"
        )

        if message:

            for index, child in enumerate(
                self.view.children
            ):

                if self.board[index] is not None:
                    child.disabled = True

            await message.edit(
                content=content,
                view=self.view,
            )

        else:

            await self.channel.send(
                content=content,
                view=self.view,
            )

    def check_winner(self):

        combinations = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]

        for a, b, c in combinations:

            if (
                self.board[a]
                and self.board[a]
                == self.board[b]
                == self.board[c]
            ):

                return self.board[a]

        return None


# ============================================================
# EXPORT
# ============================================================

__all__ = [
    "GameSystem",
]
