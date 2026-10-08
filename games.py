# ============================================================
# GAME BOT - GAMES.PY
# ============================================================
# 23 GAMES
#
# -العاب
# -حدد_امر
# /setupgames
#
# جميع الألعاب من منيو واحد.
# لا توجد أوامر منفصلة للألعاب.
#
# إعداد الألعاب:
# حتى 10 إعدادات
# كل إعداد = روم + رتبة
#
# ============================================================

import asyncio
import random
import re
import time

import discord
from discord import app_commands
from discord.ext import commands


# ============================================================
# CONFIG
# ============================================================

try:
    from config import (
        PREFIX,
        MAX_SETUP_SLOTS,
        WIN_POINTS,
        PARTICIPATION_POINTS,
        GUESS_TIME,
        FAST_GAME_TIME,
        TEXT_GAME_TIME,
        ELIMINATION_TIME,
        MAFIA_TIME,
        HIDE_SEEK_TIME,
        MUSICAL_CHAIRS_TIME,
        ROULETTE_TIME,
    )
except ImportError:
    PREFIX = "-"
    MAX_SETUP_SLOTS = 10
    WIN_POINTS = 10
    PARTICIPATION_POINTS = 2
    GUESS_TIME = 30
    FAST_GAME_TIME = 15
    TEXT_GAME_TIME = 30
    ELIMINATION_TIME = 30
    MAFIA_TIME = 30
    HIDE_SEEK_TIME = 30
    MUSICAL_CHAIRS_TIME = 30
    ROULETTE_TIME = 20


# ============================================================
# GAMES
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
# DRAWINGS
# ============================================================

DRAWINGS = [
    {
        "answer": "تفاحة",
        "aliases": ["تفاح", "apple"],
        "image": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=900&q=80",
    },
    {
        "answer": "قطة",
        "aliases": ["قط", "بس", "cat"],
        "image": "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?auto=format&fit=crop&w=900&q=80",
    },
    {
        "answer": "كلب",
        "aliases": ["dog"],
        "image": "https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=900&q=80",
    },
    {
        "answer": "بيتزا",
        "aliases": ["pizza"],
        "image": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=900&q=80",
    },
    {
        "answer": "سيارة",
        "aliases": ["سياره", "car"],
        "image": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=900&q=80",
    },
    {
        "answer": "طائرة",
        "aliases": ["طياره", "plane", "airplane"],
        "image": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=900&q=80",
    },
    {
        "answer": "دراجة",
        "aliases": ["دراجه", "bike", "bicycle"],
        "image": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=900&q=80",
    },
    {
        "answer": "كرة",
        "aliases": ["كره", "ball", "football"],
        "image": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?auto=format&fit=crop&w=900&q=80",
    },
    {
        "answer": "شجرة",
        "aliases": ["شجره", "tree"],
        "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=900&q=80",
    },
]


# ============================================================
# FLAGS
# ============================================================

FLAGS = [
    {"country": "السعودية", "aliases": ["السعوديه", "saudi", "saudi arabia"], "code": "sa"},
    {"country": "الإمارات", "aliases": ["الامارات", "uae", "emirates"], "code": "ae"},
    {"country": "الكويت", "aliases": ["kuwait"], "code": "kw"},
    {"country": "قطر", "aliases": ["qatar"], "code": "qa"},
    {"country": "البحرين", "aliases": ["bahrain"], "code": "bh"},
    {"country": "عمان", "aliases": ["سلطنة عمان", "oman"], "code": "om"},
    {"country": "مصر", "aliases": ["egypt"], "code": "eg"},
    {"country": "العراق", "aliases": ["iraq"], "code": "iq"},
    {"country": "الأردن", "aliases": ["الاردن", "jordan"], "code": "jo"},
    {"country": "المغرب", "aliases": ["morocco"], "code": "ma"},
    {"country": "الجزائر", "aliases": ["algeria"], "code": "dz"},
    {"country": "تونس", "aliases": ["tunisia"], "code": "tn"},
    {"country": "تركيا", "aliases": ["turkey", "turkiye"], "code": "tr"},
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
    {
        "country": "أمريكا",
        "aliases": ["امريكا", "usa", "united states"],
        "code": "us",
    },
    {
        "country": "بريطانيا",
        "aliases": ["بريطانيا", "انجلترا", "uk", "england"],
        "code": "gb",
    },
]


# ============================================================
# WORDS
# ============================================================

WORDS = [
    ("سيارة", ["سياره", "car"]),
    ("مدرسة", ["مدرسه", "school"]),
    ("مستشفى", ["hospital"]),
    ("كمبيوتر", ["حاسوب", "computer"]),
    ("جوال", ["هاتف", "phone"]),
    ("طائرة", ["طياره", "airplane", "plane"]),
    ("كرة", ["كره", "ball"]),
    ("كتاب", ["book"]),
    ("قلم", ["pen"]),
    ("بحر", ["sea"]),
    ("جبل", ["mountain"]),
    ("شجرة", ["شجره", "tree"]),
    ("نخلة", ["نخله", "palm"]),
    ("بيت", ["house"]),
    ("باب", ["door"]),
    ("نافذة", ["نافذه", "window"]),
    ("ساعة", ["ساعه", "clock"]),
    ("دراجة", ["دراجه", "bike"]),
    ("مفتاح", ["key"]),
    ("هاتف", ["جوال", "phone"]),
]


# ============================================================
# COLORS
# ============================================================

COLORS = [
    ("أحمر", ["احمر"], "🟥"),
    ("أزرق", ["ازرق"], "🟦"),
    ("أخضر", ["اخضر"], "🟩"),
    ("أصفر", ["اصفر"], "🟨"),
    ("برتقالي", ["برتقالي"], "🟧"),
    ("بنفسجي", ["بنفسجي"], "🟪"),
    ("وردي", ["وردي"], "🌸"),
    ("أسود", ["اسود"], "⬛"),
    ("أبيض", ["ابيض"], "⬜"),
    ("بني", ["بني"], "🟫"),
]


# ============================================================
# TEXT NORMALIZATION
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


def matches_answer(message, answer, aliases=None):
    message = normalize(message)

    options = [answer]

    if aliases:
        options.extend(aliases)

    return any(
        normalize(option) == message
        for option in options
    )


def mask_word(word):
    return " ".join(
        "⬜" if not char.isspace() else " "
        for char in word
    )


def mask_reveal(word, revealed_indexes):
    result = []

    for index, char in enumerate(word):
        if char.isspace():
            result.append(" ")
        elif index in revealed_indexes:
            result.append(char)
        else:
            result.append("⬜")

    return " ".join(result)


def game_embed(
    title,
    description,
    color=None,
):
    if color is None:
        color = discord.Color.blurple()

    return discord.Embed(
        title=title,
        description=description,
        color=color,
    )


# ============================================================
# GAMES MENU
# ============================================================

class GamesSelect(discord.ui.Select):

    def __init__(self, game_system):

        self.game_system = game_system

        options = [
            discord.SelectOption(
                label=name,
                value=key,
                emoji=emoji,
            )
            for key, emoji, name in GAMES
        ]

        super().__init__(
            placeholder="🎮 اختر اللعبة...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction):

        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ هذا النظام داخل السيرفر فقط.",
                ephemeral=True,
            )
            return

        if not self.game_system.can_use_games(
            interaction.guild.id,
            interaction.channel.id,
            interaction.user,
        ):
            await interaction.response.send_message(
                "❌ ما عندك صلاحية تشغيل الألعاب في هذا الروم.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        await self.game_system.start_game(
            interaction.channel,
            interaction.user,
            self.values[0],
        )


class GamesView(discord.ui.View):

    def __init__(self, game_system):
        super().__init__(timeout=180)
        self.add_item(GamesSelect(game_system))


# ============================================================
# SETUP UI
# ============================================================

class SetupSlotSelect(discord.ui.Select):

    def __init__(self, game_system):

        self.game_system = game_system

        options = []

        for number in range(1, MAX_SETUP_SLOTS + 1):
            options.append(
                discord.SelectOption(
                    label=f"الإعداد {number}",
                    description=f"تحديد روم ورتبة للإعداد {number}",
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
            f"⚙️ **الإعداد رقم {slot}**\n\n"
            "📢 اختر روم الألعاب:",
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


class SetupChannelSelect(discord.ui.ChannelSelect):

    def __init__(self, game_system, slot):

        self.game_system = game_system
        self.slot = slot

        super().__init__(
            placeholder="📢 اختر روم الألعاب...",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction):

        channel = self.values[0]

        await interaction.response.send_message(
            f"✅ الروم: {channel.mention}\n\n"
            "👤 الآن اختر رتبة الألعاب:",
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


class SetupRoleSelect(discord.ui.RoleSelect):

    def __init__(
        self,
        game_system,
        slot,
        channel_id,
    ):

        self.game_system = game_system
        self.slot = slot
        self.channel_id = channel_id

        super().__init__(
            placeholder="👤 اختر رتبة الألعاب...",
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction):

        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ حدث خطأ.",
                ephemeral=True,
            )
            return

        role = self.values[0]

        self.game_system.set_setup(
            interaction.guild.id,
            self.slot,
            self.channel_id,
            role.id,
        )

        await interaction.response.send_message(
            f"✅ تم حفظ الإعداد **{self.slot}**.\n\n"
            f"📢 الروم: <#{self.channel_id}>\n"
            f"👤 الرتبة: {role.mention}\n\n"
            f"يمكنك إعداد حتى **{MAX_SETUP_SLOTS}** إعدادات.",
            ephemeral=True,
        )


class SetupRoleView(discord.ui.View):

    def __init__(
        self,
        game_system,
        slot,
        channel_id,
    ):

        super().__init__(timeout=180)

        self.add_item(
            SetupRoleSelect(
                game_system,
                slot,
                channel_id,
            )
        )


# ============================================================
# JOIN SYSTEM
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
                "⚠️ أنت منضم بالفعل.",
                ephemeral=True,
            )
            return

        if len(self.parent_view.players) >= self.parent_view.maximum:
            await interaction.response.send_message(
                "❌ اكتمل عدد اللاعبين.",
                ephemeral=True,
            )
            return

        self.parent_view.players[
            interaction.user.id
        ] = interaction.user

        await interaction.response.send_message(
            f"✅ انضممت للعبة.\n"
            f"👥 اللاعبين: "
            f"{len(self.parent_view.players)}/"
            f"{self.parent_view.maximum}",
            ephemeral=True,
        )

        if len(self.parent_view.players) >= self.parent_view.minimum:
            self.parent_view.start_requested = True
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

        if len(self.parent_view.players) < self.parent_view.minimum:
            await interaction.response.send_message(
                f"❌ تحتاج على الأقل "
                f"{self.parent_view.minimum} لاعبين.",
                ephemeral=True,
            )
            return

        self.parent_view.start_requested = True
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
        timeout=30,
    ):

        super().__init__(timeout=timeout)

        self.minimum = minimum
        self.maximum = maximum
        self.players = {}
        self.start_requested = False

        self.add_item(JoinButton(self))
        self.add_item(StartButton(self))


# ============================================================
# RPS
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

        if len(self.parent_view.choices) >= 2:
            await interaction.response.send_message(
                "❌ اكتمل عدد اللاعبين.",
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

        if len(self.parent_view.choices) >= 2:
            self.parent_view.stop()


class RPSView(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=FAST_GAME_TIME)

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

        super().__init__(timeout=10)

        self.winner = None

        self.add_item(
            FastClickButton(self)
        )


# ============================================================
# XO
# ============================================================

class XOButton(discord.ui.Button):

    def __init__(self, game, index):

        self.game = game
        self.index = index

        super().__init__(
            label="⬜",
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

        super().__init__(timeout=120)

        self.game = game

        for index in range(9):
            self.add_item(
                XOButton(
                    game,
                    index,
                )
            )


class XOGame:

    def __init__(
        self,
        system,
        channel,
        player_x,
        player_o,
        fiery=False,
    ):

        self.system = system
        self.channel = channel

        self.player_x = player_x
        self.player_o = player_o

        self.fiery = fiery

        self.board = [None] * 9

        self.current = player_x

        self.symbols = {
            player_x.id: "❌",
            player_o.id: "⭕",
        }

        self.fire_cells = set()

        if fiery:
            self.fire_cells = set(
                random.sample(range(9), 2)
            )

        self.view = XOView(self)

        self.message = None
        self.finished = False

    async def start(self):
        await self.update_message()

    async def play_move(self, interaction, index):

        if self.finished:
            await interaction.response.send_message(
                "❌ انتهت اللعبة.",
                ephemeral=True,
            )
            return

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

        if self.fiery and index in self.fire_cells:

            self.finished = True

            await interaction.response.defer()

            for child in self.view.children:
                child.disabled = True

            winner = (
                self.player_o
                if self.current.id == self.player_x.id
                else self.player_x
            )

            if self.message:
                await self.message.edit(
                    content=(
                        "🔥 **إكس أو النارية**\n\n"
                        f"💥 {interaction.user.mention} "
                        "ضغط على الخانة النارية وخسر!\n\n"
                        f"🏆 الفائز: {winner.mention}"
                    ),
                    view=self.view,
                )

            await self.system.winner(
                self.channel,
                winner,
            )

            self.system.active_games.pop(
                self.channel.id,
                None,
            )

            return

        self.board[index] = self.symbols[
            interaction.user.id
        ]

        await interaction.response.defer()

        winner_symbol = self.check_winner()

        if winner_symbol:

            self.finished = True

            for child in self.view.children:
                child.disabled = True

            winner = self.current

            if self.message:
                await self.message.edit(
                    content=(
                        f"🏆 الفائز: "
                        f"{winner.mention}"
                    ),
                    view=self.view,
                )

            await self.system.winner(
                self.channel,
                winner,
            )

            self.system.active_games.pop(
                self.channel.id,
                None,
            )

            return

        if all(
            cell is not None
            for cell in self.board
        ):

            self.finished = True

            for child in self.view.children:
                child.disabled = True

            if self.message:
                await self.message.edit(
                    content="🤝 تعادل!",
                    view=self.view,
                )

            self.system.active_games.pop(
                self.channel.id,
                None,
            )

            return

        self.current = (
            self.player_o
            if self.current.id == self.player_x.id
            else self.player_x
        )

        await self.update_message()

    async def update_message(self):

        board = []

        for index in range(9):

            if self.board[index]:
                value = self.board[index]

            elif self.fiery and index in self.fire_cells:
                value = "🔥"

            else:
                value = "⬜"

            board.append(value)

        title = (
            "🔥 إكس أو النارية"
            if self.fiery
            else "❌⭕ إكس أو"
        )

        content = (
            f"**{title}**\n\n"
            f"{board[0]} {board[1]} {board[2]}\n"
            f"{board[3]} {board[4]} {board[5]}\n"
            f"{board[6]} {board[7]} {board[8]}\n\n"
            f"الدور: {self.current.mention}"
        )

        if self.fiery:
            content += "\n\n⚠️ انتبه: 🔥 = خانة نارية."

        if self.message is None:
            self.message = await self.channel.send(
                content=content,
                view=self.view,
            )
        else:
            await self.message.edit(
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
# GAME SYSTEM
# ============================================================

class GameSystem:

    def __init__(self, bot):

        self.bot = bot

        self.active_games = {}

        self.guild_setups = {}

        self.points = {}

        self.listener_added = False
        self.commands_added = False
        self.slash_added = False


    # ========================================================
    # SETUP
    # ========================================================

    async def setup(self):

        # ----------------------------------------------------
        # -العاب
        #
        # مهم:
        # لا نستخدم self.games_command مباشرة داخل
        # commands.Command لأن discord.py يقوم بفحص
        # signature الخاص بالـ bound method.
        # ----------------------------------------------------

        if self.bot.get_command("العاب") is None:

            async def games_callback(ctx: commands.Context):
                await self.games_command(ctx)

            self.bot.add_command(
                commands.Command(
                    games_callback,
                    name="العاب",
                    help="فتح قائمة الألعاب",
                )
            )


        # ----------------------------------------------------
        # -حدد_امر
        # ----------------------------------------------------

        if self.bot.get_command("حدد_امر") is None:

            async def setup_callback(ctx: commands.Context):
                await self.setup_command(ctx)

            self.bot.add_command(
                commands.Command(
                    setup_callback,
                    name="حدد_امر",
                    help="إعداد رومات ورتب الألعاب",
                )
            )


        # ----------------------------------------------------
        # /setupgames
        #
        # لا نستخدم @app_commands.command على method
        # داخل GameSystem.
        # نسجل callback مستقل لتجنب مشاكل binding.
        # ----------------------------------------------------

        if not self.slash_added:

            async def slash_callback(
                interaction: discord.Interaction,
            ):
                await self.setupgames_slash(
                    interaction
                )

            slash_command = app_commands.Command(
                name="setupgames",
                description="إعداد رومات ورتب الألعاب",
                callback=slash_callback,
            )

            try:
                self.bot.tree.add_command(
                    slash_command
                )
            except app_commands.CommandAlreadyRegistered:
                pass

            self.slash_added = True


        # ----------------------------------------------------
        # on_message
        # ----------------------------------------------------

        if not self.listener_added:

            self.bot.add_listener(
                self.on_message,
                "on_message",
            )

            self.listener_added = True


    # ========================================================
    # LOAD SETUPS
    # ========================================================

    def load_setups(self, guild_id):

        if guild_id in self.guild_setups:
            return self.guild_setups[guild_id]

        setups = {}

        try:

            rows = self.bot.database.get_setups(
                guild_id
            )

            for row in rows:

                try:

                    if isinstance(row, dict):

                        slot = int(row["slot"])
                        channel_id = int(
                            row["channel_id"]
                        )
                        role_id = int(
                            row["role_id"]
                        )

                    else:

                        slot = int(row[0])
                        channel_id = int(row[1])
                        role_id = int(row[2])

                    setups[slot] = {
                        "channel_id": channel_id,
                        "role_id": role_id,
                    }

                except Exception:
                    continue

        except Exception as error:

            print(
                f"[SETUP LOAD ERROR] {error}"
            )

            setups = {}

        self.guild_setups[guild_id] = setups

        return setups


    # ========================================================
    # -العاب
    # ========================================================

    async def games_command(self, ctx):

        if ctx.guild is None:
            return

        if not self.can_use_games(
            ctx.guild.id,
            ctx.channel.id,
            ctx.author,
        ):

            await ctx.send(
                "❌ ما عندك صلاحية تشغيل الألعاب في هذا الروم."
            )
            return

        embed = game_embed(
            "🎮 قائمة الألعاب",
            "اختر اللعبة من القائمة وستبدأ مباشرة.\n\n"
            "🎯 ألعاب إقصاء\n"
            "🧠 ألعاب تخمين\n"
            "⚡ ألعاب سرعة\n"
            "👥 ألعاب جماعية\n"
            "🔤 ألعاب نصوص",
        )

        await ctx.send(
            embed=embed,
            view=GamesView(self),
        )


    # ========================================================
    # -حدد_امر
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
            f"الحد الأقصى: **{MAX_SETUP_SLOTS} إعدادات**.\n"
            "كل إعداد = روم + رتبة.",
        )

        await ctx.send(
            embed=embed,
            view=SetupMainView(self),
        )


    # ========================================================
    # /setupgames
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
            "اختر رقم الإعداد.\n\n"
            f"يمكنك إعداد حتى **{MAX_SETUP_SLOTS}** "
            "رومات ورتب.",
        )

        await interaction.response.send_message(
            embed=embed,
            view=SetupMainView(self),
            ephemeral=True,
        )


    # ========================================================
    # SAVE SETUP
    # ========================================================

    def set_setup(
        self,
        guild_id,
        slot,
        channel_id,
        role_id,
    ):

        if not 1 <= int(slot) <= MAX_SETUP_SLOTS:
            return False

        guild_id = int(guild_id)
        slot = int(slot)
        channel_id = int(channel_id)
        role_id = int(role_id)

        if guild_id not in self.guild_setups:
            self.guild_setups[guild_id] = {}

        self.guild_setups[guild_id][slot] = {
            "channel_id": channel_id,
            "role_id": role_id,
        }

        try:

            self.bot.database.save_setup(
                guild_id,
                slot,
                channel_id,
                role_id,
            )

        except Exception as error:

            print(
                f"[SETUP SAVE ERROR] {error}"
            )

        return True


    # ========================================================
    # ACCESS
    # ========================================================

    def can_use_games(
        self,
        guild_id,
        channel_id,
        member,
    ):

        setups = self.load_setups(
            guild_id
        )

        # إذا لم يتم إعداد أي روم:
        # الإدارة تستطيع الاختبار.
        if not setups:
            return member.guild_permissions.manage_guild

        for setup in setups.values():

            if setup["channel_id"] != int(channel_id):
                continue

            if member.guild_permissions.manage_guild:
                return True

            role_id = setup["role_id"]

            return any(
                role.id == role_id
                for role in member.roles
            )

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

        if channel_id in self.active_games:

            await channel.send(
                "⚠️ توجد لعبة شغالة حاليًا في هذا الروم."
            )
            return

        method = getattr(
            self,
            f"game_{game_key}",
            None,
        )

        if method is None:

            await channel.send(
                "❌ هذه اللعبة غير متاحة."
            )
            return

        self.active_games[channel_id] = {
            "game": game_key,
            "starter": starter.id,
            "started": time.time(),
        }

        try:

            await method(channel)

        except asyncio.CancelledError:

            raise

        except Exception as error:

            print(
                f"[GAME ERROR] {game_key}: {error}"
            )

            import traceback

            traceback.print_exc()

            try:
                await channel.send(
                    "❌ حدث خطأ داخل اللعبة وتم إيقافها."
                )
            except Exception:
                pass

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

        if message.content.startswith(PREFIX):
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

            try:
                await handler(message)

            except Exception as error:

                print(
                    f"[ANSWER ERROR] {error}"
                )


    # ========================================================
    # WINNER
    # ========================================================

    async def winner(
        self,
        channel,
        member,
        points=WIN_POINTS,
    ):

        if member is None:
            return

        self.points[member.id] = (
            self.points.get(
                member.id,
                0,
            )
            + points
        )

        embed = game_embed(
            "🏆 الفائز!",
            f"🎉 الفائز: {member.mention}\n\n"
            f"⭐ النقاط: **+{points}**",
            discord.Color.green(),
        )

        await channel.send(
            embed=embed
        )

        # User / Member ليس بالضرورة عنده guild.
        # لذلك نأخذ guild من channel.
        guild = getattr(channel, "guild", None)

        if guild is None:
            return

        try:

            self.bot.database.add_win(
                guild.id,
                member.id,
                points,
            )

        except Exception as error:

            print(
                f"[DATABASE WIN ERROR] {error}"
            )

        try:

            game_key = self.active_games.get(
                channel.id,
                {},
            ).get(
                "game",
                "unknown",
            )

            self.bot.database.add_game_history(
                guild.id,
                channel.id,
                GAME_NAMES.get(
                    game_key,
                    "لعبة",
                ),
                member.id,
                points,
            )

        except Exception:
            pass


    # ========================================================
    # GAME 1 - ROULETTE
    # ========================================================

    async def game_roulette(self, channel):

        view = JoinView(
            minimum=2,
            maximum=20,
            timeout=30,
        )

        await channel.send(
            embed=game_embed(
                "🎯 روليت",
                "لعبة إقصاء عشوائي فقط.\n"
                "بدون رهانات أو أموال.\n\n"
                "🎮 اضغط انضمام.",
            ),
            view=view,
        )

        await view.wait()

        players = list(
            view.players.values()
        )

        if len(players) < 2:

            await channel.send(
                "❌ لم يكتمل عدد اللاعبين."
            )
            return

        while len(players) > 1:

            eliminated = random.choice(players)

            players.remove(eliminated)

            await channel.send(
                f"🎯 تم اختيار {eliminated.mention}.\n"
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
            timeout=30,
        )

        await channel.send(
            embed=game_embed(
                "❌⭕ إكس أو",
                "🎮 يحتاج لاعبين.\n"
                "اضغط انضمام.",
            ),
            view=view,
        )

        await view.wait()

        players = list(
            view.players.values()
        )

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

        for _ in range(120):

            if channel.id not in self.active_games:
                return

            if game.finished:
                return

            await asyncio.sleep(1)


    # ========================================================
    # GAME 3 - MAFIA
    # ========================================================

    async def game_mafia(self, channel):

        view = JoinView(
            minimum=4,
            maximum=12,
            timeout=30,
        )

        await channel.send(
            embed=game_embed(
                "🕵️ مافيا",
                "🎮 انضم للعبة.\n"
                "يجب وجود 4 لاعبين على الأقل.",
            ),
            view=view,
        )

        await view.wait()

        players = list(
            view.players.values()
        )

        if len(players) < 4:

            await channel.send(
                "❌ تحتاج 4 لاعبين على الأقل."
            )
            return

        mafia_count = max(
            1,
            len(players) // 4,
        )

        mafia_players = random.sample(
            players,
            mafia_count,
        )

        mafia_ids = {
            player.id
            for player in mafia_players
        }

        for player in players:

            try:

                if player.id in mafia_ids:

                    await player.send(
                        "🕵️ **دورك: مافيا**\n"
                        "حافظ على سريتك."
                    )

                else:

                    await player.send(
                        "👤 **دورك: مواطن**\n"
                        "حاول اكتشاف المافيا."
                    )

            except discord.Forbidden:
                pass

        await channel.send(
            embed=game_embed(
                "🕵️ بدأت المافيا!",
                "📩 تم إرسال الأدوار في الخاص.\n\n"
                f"👥 عدد اللاعبين: {len(players)}\n"
                f"🕵️ عدد المافيا: {mafia_count}\n\n"
                f"⏱️ الجولة تستمر {MAFIA_TIME} ثانية.",
            )
        )

        await asyncio.sleep(MAFIA_TIME)

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
            timeout=30,
        )

        await channel.send(
            embed=game_embed(
                "🪑 الكراسي الموسيقية",
                "🎮 انضم للعبة.",
            ),
            view=view,
        )

        await view.wait()

        players = list(
            view.players.values()
        )

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
                "🪑 توقفت الموسيقى!\n"
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

        view = RPSView()

        await channel.send(
            embed=game_embed(
                "🪨📄✂️ حجر ورق مقص",
                "أول لاعبين يختارون يدخلون الجولة.",
            ),
            view=view,
        )

        await view.wait()

        players = list(
            view.choices.keys()
        )[:2]

        if len(players) < 2:

            await channel.send(
                "❌ لم يدخل لاعبان."
            )
            return

        p1 = self.bot.get_user(players[0])
        p2 = self.bot.get_user(players[1])

        if p1 is None or p2 is None:
            return

        c1 = view.choices[players[0]]
        c2 = view.choices[players[1]]

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

        winner = p1 if (c1, c2) in wins else p2

        await self.winner(
            channel,
            winner,
        )


    # ========================================================
    # GAME 6 - FIERY XO
    # ========================================================

    async def game_fiery_xo(self, channel):

        view = JoinView(
            minimum=2,
            maximum=2,
            timeout=30,
        )

        await channel.send(
            embed=game_embed(
                "🔥 إكس أو النارية",
                "اضغط انضمام.\n\n"
                "⚠️ توجد خانات 🔥.\n"
                "الضغط على خانة نارية يعني الخسارة.",
            ),
            view=view,
        )

        await view.wait()

        players = list(
            view.players.values()
        )

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
            fiery=True,
        )

        await game.start()

        for _ in range(120):

            if channel.id not in self.active_games:
                return

            if game.finished:
                return

            await asyncio.sleep(1)


    # ========================================================
    # GAME 7 - HIDE & SEEK
    # ========================================================

    async def game_hide_seek(self, channel):

        view = JoinView(
            minimum=3,
            maximum=15,
            timeout=30,
        )

        await channel.send(
            embed=game_embed(
                "👀 الغميضة",
                "اضغط انضمام.",
            ),
            view=view,
        )

        await view.wait()

        players = list(
            view.players.values()
        )

        if len(players) < 3:

            await channel.send(
                "❌ تحتاج 3 لاعبين على الأقل."
            )
            return

        seeker = random.choice(players)

        hidden_players = [
            player
            for player in players
            if player.id != seeker.id
        ]

        hidden = random.choice(hidden_players)

        await channel.send(
            f"👀 الباحث: {seeker.mention}\n"
            "🙈 تم اختيار المختبئ.\n\n"
            f"⏱️ أمام الباحث {HIDE_SEEK_TIME} ثانية.",
        )

        await asyncio.sleep(HIDE_SEEK_TIME)

        await channel.send(
            f"🔎 المختبئ كان: {hidden.mention}"
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
            "البوت سريع جدا",
            "الالعاب ممتعة",
            "هذا اختبار سرعة",
            "ديسكورد رائع",
        ]

        sentence = random.choice(sentences)

        self.active_games[channel.id]["answer"] = normalize(
            sentence
        )

        await channel.send(
            embed=game_embed(
                "🤖 ريبلكا",
                f"انسخ الجملة كما هي:\n\n"
                f"**{sentence}**\n\n"
                f"⏱️ لديك {TEXT_GAME_TIME} ثانية.",
            )
        )

        await asyncio.sleep(TEXT_GAME_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ انتهى الوقت!\n"
                f"الإجابة: **{sentence}**"
            )


    async def answer_replika(self, message):

        game = self.active_games.get(
            message.channel.id
        )

        if not game:
            return

        if normalize(message.content) != game.get("answer"):
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
    # GAME 9 - GUESS COUNTRY
    # ========================================================

    async def game_guess_country(self, channel):

        item = random.choice(FLAGS)

        clues = {
            "السعودية": "تقع في شبه الجزيرة العربية.",
            "الإمارات": "عاصمتها أبوظبي.",
            "الكويت": "دولة خليجية.",
            "قطر": "استضافت كأس العالم 2022.",
            "البحرين": "دولة جزيرية خليجية.",
            "عمان": "تقع جنوب شرق شبه الجزيرة العربية.",
            "مصر": "يمر بها نهر النيل.",
            "العراق": "دجلة والفرات يمران بها.",
            "الأردن": "عاصمتها عمّان.",
            "المغرب": "تقع في شمال غرب أفريقيا.",
            "الجزائر": "أكبر دول أفريقيا مساحة.",
            "تونس": "دولة في شمال أفريقيا.",
            "تركيا": "تقع بين آسيا وأوروبا.",
            "فرنسا": "عاصمتها باريس.",
            "ألمانيا": "عاصمتها برلين.",
            "إيطاليا": "تشتهر بشكل شبه الجزيرة.",
            "إسبانيا": "تقع في شبه الجزيرة الإيبيرية.",
            "اليابان": "دولة جزرية في شرق آسيا.",
            "الصين": "دولة كبيرة في شرق آسيا.",
            "الهند": "تقع في جنوب آسيا.",
            "البرازيل": "أكبر دولة في أمريكا الجنوبية.",
            "الأرجنتين": "تقع في جنوب أمريكا الجنوبية.",
            "كندا": "تقع شمال الولايات المتحدة.",
            "أمريكا": "عاصمتها واشنطن.",
            "بريطانيا": "دولة جزرية أوروبية.",
        }

        clue = clues.get(
            item["country"],
            "دولة معروفة.",
        )

        self.active_games[channel.id]["answer"] = item["country"]
        self.active_games[channel.id]["aliases"] = item["aliases"]

        await channel.send(
            embed=game_embed(
                "🌍 خمن الدولة",
                f"💡 تلميح:\n{clue}\n\n"
                f"⏱️ {GUESS_TIME} ثانية.",
            )
        )

        await asyncio.sleep(GUESS_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ انتهى الوقت!\n"
                f"الإجابة: **{item['country']}**"
            )


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

        self.active_games[channel.id]["answer"] = item["answer"]
        self.active_games[channel.id]["aliases"] = item["aliases"]

        letter_count = len(
            "".join(
                item["answer"].split()
            )
        )

        embed = game_embed(
            "🎨 خمن الرسمة",
            "ما الموجود في الصورة؟\n\n"
            f"🔤 عدد الحروف: **{letter_count}**\n\n"
            f"⏱️ الوقت: **{GUESS_TIME} ثانية**",
        )

        embed.set_image(
            url=item["image"]
        )

        await channel.send(
            embed=embed
        )

        await asyncio.sleep(GUESS_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ انتهى الوقت!\n"
                f"الإجابة: **{item['answer']}**"
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

        word, aliases = random.choice(WORDS)

        self.active_games[channel.id]["answer"] = word
        self.active_games[channel.id]["aliases"] = aliases

        await channel.send(
            embed=game_embed(
                "📝 خمن الكلمة",
                f"الكلمة:\n\n"
                f"{mask_word(word)}\n\n"
                f"🔤 عدد الحروف: {len(word)}\n"
                f"⏱️ {GUESS_TIME} ثانية.",
            )
        )

        await asyncio.sleep(GUESS_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ الإجابة كانت: **{word}**"
            )


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
            "تحدي",
            "سرعة الكتابة",
        ])

        self.active_games[channel.id]["answer"] = normalize(text)

        await channel.send(
            embed=game_embed(
                "⌨️ الكتابة السريعة",
                f"اكتب الكلمة بالضبط:\n\n"
                f"**{text}**\n\n"
                f"⏱️ {TEXT_GAME_TIME} ثانية.",
            )
        )

        await asyncio.sleep(TEXT_GAME_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ انتهى الوقت!\n"
                f"الإجابة: **{text}**"
            )


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
            "تحدي",
        ])

        answer = " ".join(word)

        self.active_games[channel.id]["answer"] = normalize(answer)

        await channel.send(
            embed=game_embed(
                "✂️ فصل النص",
                f"النص:\n\n"
                f"**{word}**\n\n"
                "افصل الحروف بمسافات.\n\n"
                f"مثال:\n`{' '.join(word)}`\n\n"
                f"⏱️ {TEXT_GAME_TIME} ثانية.",
            )
        )

        await asyncio.sleep(TEXT_GAME_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ الإجابة:\n`{answer}`"
            )


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
            "ت ح د ي",
        ])

        answer = word.replace(" ", "")

        self.active_games[channel.id]["answer"] = normalize(answer)

        await channel.send(
            embed=game_embed(
                "🔗 دمج النص",
                f"ادمج الحروف:\n\n"
                f"**{word}**\n\n"
                f"⏱️ {TEXT_GAME_TIME} ثانية.",
            )
        )

        await asyncio.sleep(TEXT_GAME_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ الإجابة: **{answer}**"
            )


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

        item = random.choice(FLAGS)

        self.active_games[channel.id]["answer"] = item["country"]
        self.active_games[channel.id]["aliases"] = item["aliases"]

        image_url = (
            f"https://flagcdn.com/w640/{item['code']}.png"
        )

        embed = game_embed(
            "🏳️ خمن العلم",
            "ما الدولة صاحبة هذا العلم؟\n\n"
            f"⏱️ {GUESS_TIME} ثانية.",
        )

        embed.set_image(
            url=image_url
        )

        await channel.send(
            embed=embed
        )

        await asyncio.sleep(GUESS_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ انتهى الوقت!\n"
                f"الإجابة: **{item['country']}**"
            )


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
            "تحدي",
        ])

        reversed_text = text[::-1]

        self.active_games[channel.id]["answer"] = normalize(
            reversed_text
        )

        await channel.send(
            embed=game_embed(
                "🔄 عكس النص",
                f"اعكس النص:\n\n"
                f"**{text}**\n\n"
                f"⏱️ {TEXT_GAME_TIME} ثانية.",
            )
        )

        await asyncio.sleep(TEXT_GAME_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ الإجابة: **{reversed_text}**"
            )


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

        target = random.choice(letters)

        other_letters = [
            letter
            for letter in letters
            if letter != target
        ]

        sequence = [
            random.choice(other_letters)
            for _ in range(49)
        ]

        position = random.randint(0, 49)

        sequence.insert(
            position,
            target,
        )

        display = " ".join(sequence)

        self.active_games[channel.id]["answer"] = normalize(
            target
        )

        await channel.send(
            embed=game_embed(
                "🔤 ابحث عن الحرف",
                f"الحرف المطلوب: **{target}**\n\n"
                f"{display}\n\n"
                "أرسل الحرف عندما تجده.",
            )
        )

        await asyncio.sleep(TEXT_GAME_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ انتهى الوقت!\n"
                f"الحرف كان: **{target}**"
            )


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

        letters = list(
            "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
        )

        target = random.choice(letters)

        fake = random.choice([
            letter
            for letter in letters
            if letter != target
        ])

        sequence = [
            fake
            for _ in range(30)
        ]

        correct_index = random.randrange(30)

        sequence[correct_index] = target

        display = " ".join(sequence)

        self.active_games[channel.id]["answer"] = str(
            correct_index + 1
        )

        await channel.send(
            embed=game_embed(
                "✅ الحرف الصحيح",
                f"الحرف المطلوب: **{target}**\n\n"
                f"{display}\n\n"
                "أرسل رقم مكانه من **1 إلى 30**.",
            )
        )

        await asyncio.sleep(TEXT_GAME_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ الإجابة: **{correct_index + 1}**"
            )


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

        scrambled = numbers[:]

        random.shuffle(scrambled)

        answer = " ".join(
            str(number)
            for number in sorted(numbers)
        )

        self.active_games[channel.id]["answer"] = answer

        await channel.send(
            embed=game_embed(
                "🔢 ترتيب الأرقام",
                f"رتب من الأصغر إلى الأكبر:\n\n"
                f"**{' - '.join(map(str, scrambled))}**\n\n"
                "مثال: `1 2 3 4 5 6`\n\n"
                f"⏱️ {TEXT_GAME_TIME} ثانية.",
            )
        )

        await asyncio.sleep(TEXT_GAME_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ الإجابة: `{answer}`"
            )


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

        color = random.choice(COLORS)

        name = color[0]
        aliases = color[1]
        emoji = color[2]

        self.active_games[channel.id]["answer"] = name
        self.active_games[channel.id]["aliases"] = aliases

        await channel.send(
            embed=game_embed(
                "🎨 خمن اللون",
                f"اللون الظاهر:\n\n"
                f"# {emoji}\n\n"
                "اكتب اسم اللون.\n\n"
                f"⏱️ {GUESS_TIME} ثانية.",
            )
        )

        await asyncio.sleep(GUESS_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ الإجابة: **{name}**"
            )


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

        emojis = [
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

        target = random.choice(emojis)

        others = [
            emoji
            for emoji in emojis
            if emoji != target
        ]

        sequence = [
            random.choice(others)
            for _ in range(49)
        ]

        position = random.randint(0, 49)

        sequence.insert(
            position,
            target,
        )

        display = " ".join(sequence)

        self.active_games[channel.id]["answer"] = target

        await channel.send(
            embed=game_embed(
                "🔎 ابحث عن الإيموجي",
                f"الإيموجي المطلوب: **{target}**\n\n"
                f"{display}\n\n"
                "أرسل الإيموجي عندما تجده.",
            )
        )

        await asyncio.sleep(TEXT_GAME_TIME)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ الإجابة: **{target}**"
            )


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

        word, aliases = random.choice(WORDS)

        self.active_games[channel.id]["answer"] = word
        self.active_games[channel.id]["aliases"] = aliases

        revealed = set()

        message = await channel.send(
            embed=game_embed(
                "👁️ كشف النص",
                f"الكلمة تحتوي على "
                f"**{len(word)} حروف**.\n\n"
                f"{mask_reveal(word, revealed)}\n\n"
                "سيتم كشف حروف تدريجيًا.",
            )
        )

        reveal_count = min(
            3,
            len([
                char
                for char in word
                if not char.isspace()
            ]),
        )

        for _ in range(reveal_count):

            await asyncio.sleep(5)

            if channel.id not in self.active_games:
                return

            available = [
                index
                for index in range(len(word))
                if not word[index].isspace()
                and index not in revealed
            ]

            if not available:
                break

            revealed.add(
                random.choice(available)
            )

            await message.edit(
                embed=game_embed(
                    "👁️ كشف النص",
                    f"الكلمة تحتوي على "
                    f"**{len(word)} حروف**.\n\n"
                    f"{mask_reveal(word, revealed)}\n\n"
                    "💡 حاول التخمين!",
                )
            )

        remaining = max(
            0,
            TEXT_GAME_TIME - (reveal_count * 5),
        )

        if remaining:
            await asyncio.sleep(remaining)

        if channel.id in self.active_games:

            await channel.send(
                f"⏰ الإجابة: **{word}**"
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
# EXPORT
# ============================================================

__all__ = [
    "GameSystem",
]
