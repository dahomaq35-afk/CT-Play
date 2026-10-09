
# ============================================================
# GAME BOT - GAMES.PY
# FULL VERSION - 24 GAMES INCLUDING WHEEL
# Python 3.14+ / discord.py 2.7+
# ============================================================

import asyncio
import random
import re
import time
import traceback

import discord
from discord import app_commands
from discord.ext import commands

try:
    import config as cfg
except ImportError:
    cfg = None

# ============================================================
# CONFIG
# ============================================================

PREFIX = getattr(cfg, "PREFIX", "-")
MAX_SETUP_SLOTS = getattr(cfg, "MAX_SETUP_SLOTS", 10)
WIN_POINTS = getattr(cfg, "WIN_POINTS", 10)
PARTICIPATION_POINTS = getattr(cfg, "PARTICIPATION_POINTS", 2)
GUESS_TIME = getattr(cfg, "GUESS_TIME", 30)
FAST_GAME_TIME = getattr(cfg, "FAST_GAME_TIME", 15)
TEXT_GAME_TIME = getattr(cfg, "TEXT_GAME_TIME", 30)
ELIMINATION_TIME = getattr(cfg, "ELIMINATION_TIME", 30)
MAFIA_TIME = getattr(cfg, "MAFIA_TIME", 30)
HIDE_SEEK_TIME = getattr(cfg, "HIDE_SEEK_TIME", 30)
MUSICAL_CHAIRS_TIME = getattr(cfg, "MUSICAL_CHAIRS_TIME", 30)
ROULETTE_TIME = getattr(cfg, "ROULETTE_TIME", 20)
EXPLOIT_LOG_CHANNEL_ID = getattr(cfg, "EXPLOIT_LOG_CHANNEL_ID", None)
EXPLOIT_LOG_COOLDOWN_SECONDS = getattr(cfg, "EXPLOIT_LOG_COOLDOWN_SECONDS", 5)
EXPLOIT_LOGGING_ENABLED = getattr(cfg, "EXPLOIT_LOGGING_ENABLED", True)
ADMIN_BYPASS_SETUP = getattr(cfg, "ADMIN_BYPASS_SETUP", True)

# ============================================================
# GAME COMMANDS
# ============================================================

GAMES = [
    ("roulette", "🎯", "روليت", "روليت"),
    ("xo", "❌", "إكس أو", "XO"),
    ("mafia", "🕵️", "مافيا", "مافيا"),
    ("musical_chairs", "🪑", "الكراسي الموسيقية", "الكراسي_الموسيقية"),
    ("rps", "🪨", "حجر ورق مقص", "حجر_ورق_مقص"),
    ("fiery_xo", "🔥", "إكس أو النارية", "اكس_او_النارية"),
    ("hide_seek", "👀", "الغميضة", "الغميضة"),
    ("replika", "🤖", "ريبلكا", "ريبلكا"),
    ("guess_country", "🌍", "خمن الدولة", "خمن_الدولة"),
    ("guess_drawing", "🎨", "خمن الرسمة", "خمن_الرسمة"),
    ("guess_word", "📝", "خمن الكلمة", "خمن_الكلمة"),
    ("fast_click", "⚡", "الضغط السريع", "الضغط_السريع"),
    ("fast_type", "⌨️", "الكتابة السريعة", "الكتابة_السريعة"),
    ("text_split", "✂️", "فصل النص", "فصل_النص"),
    ("merge_text", "🔗", "دمج النص", "دمج_النص"),
    ("guess_flag", "🏳️", "خمن العلم", "خمن_العلم"),
    ("text_reverse", "🔄", "عكس النص", "عكس_النص"),
    ("find_letter", "🔤", "ابحث عن الحرف", "ابحث_عن_الحرف"),
    ("correct_letter", "✅", "الحرف الصحيح", "الحرف_الصحيح"),
    ("sort_numbers", "🔢", "ترتيب الأرقام", "ترتيب_الارقام"),
    ("guess_color", "🎨", "خمن اللون", "خمن_اللون"),
    ("find_emoji", "🔎", "ابحث عن الإيموجي", "ابحث_عن_الايموجي"),
    ("text_reveal", "👁️", "كشف النص", "كشف_النص"),
    ("wheel", "🎡", "العجلة", "العجلة"),
]

GAME_NAMES = {key: name for key, emoji, name, command in GAMES}
GAME_COMMANDS = {key: command for key, emoji, name, command in GAMES}

# ============================================================
# GAME DATA
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

FLAGS = [
    ("السعودية", ["السعوديه", "saudi", "saudi arabia"], "sa", "تقع في شبه الجزيرة العربية."),
    ("الإمارات", ["الامارات", "uae", "emirates"], "ae", "عاصمتها أبوظبي."),
    ("الكويت", ["kuwait"], "kw", "دولة خليجية."),
    ("قطر", ["qatar"], "qa", "استضافت كأس العالم 2022."),
    ("البحرين", ["bahrain"], "bh", "دولة جزيرية خليجية."),
    ("عمان", ["سلطنة عمان", "oman"], "om", "تقع جنوب شرق شبه الجزيرة العربية."),
    ("مصر", ["egypt"], "eg", "يمر بها نهر النيل."),
    ("العراق", ["iraq"], "iq", "يمر بها نهرا دجلة والفرات."),
    ("الأردن", ["الاردن", "jordan"], "jo", "عاصمتها عمّان."),
    ("المغرب", ["morocco"], "ma", "تقع في شمال غرب أفريقيا."),
    ("الجزائر", ["algeria"], "dz", "أكبر دول أفريقيا مساحة."),
    ("تونس", ["tunisia"], "tn", "دولة في شمال أفريقيا."),
    ("تركيا", ["turkey", "turkiye"], "tr", "تقع بين آسيا وأوروبا."),
    ("فرنسا", ["france"], "fr", "عاصمتها باريس."),
    ("ألمانيا", ["المانيا", "germany"], "de", "عاصمتها برلين."),
    ("إيطاليا", ["italy"], "it", "تشتهر بشكل شبه الجزيرة."),
    ("إسبانيا", ["اسبانيا", "spain"], "es", "تقع في شبه الجزيرة الإيبيرية."),
    ("اليابان", ["japan"], "jp", "دولة جزرية في شرق آسيا."),
    ("الصين", ["china"], "cn", "دولة كبيرة في شرق آسيا."),
    ("الهند", ["india"], "in", "تقع في جنوب آسيا."),
    ("البرازيل", ["brazil"], "br", "أكبر دولة في أمريكا الجنوبية."),
    ("الأرجنتين", ["argentina"], "ar", "تقع في جنوب أمريكا الجنوبية."),
    ("كندا", ["canada"], "ca", "تقع شمال الولايات المتحدة."),
    ("أمريكا", ["امريكا", "usa", "united states"], "us", "عاصمتها واشنطن."),
    ("بريطانيا", ["انجلترا", "uk", "england"], "gb", "دولة جزرية أوروبية."),
]

COLORS = [
    ("أحمر", ["احمر"], "🟥"),
    ("أزرق", ["ازرق"], "🟦"),
    ("أخضر", ["اخضر"], "🟩"),
    ("أصفر", ["اصفر"], "🟨"),
    ("برتقالي", [], "🟧"),
    ("بنفسجي", [], "🟪"),
    ("وردي", [], "🌸"),
    ("أسود", ["اسود"], "⬛"),
    ("أبيض", ["ابيض"], "⬜"),
    ("بني", [], "🟫"),
]

# ============================================================
# TEXT HELPERS
# ============================================================

def normalize(text):
    if not text:
        return ""

    text = str(text).lower().strip()

    replacements = {
        "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
        "ة": "ه", "ى": "ي", "ؤ": "و", "ئ": "ي", "ـ": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return re.sub(r"\s+", " ", text)


def matches_answer(message, answer, aliases=None):
    target = normalize(message)
    options = [answer] + list(aliases or [])
    return any(normalize(option) == target for option in options)


def embed(title, description, color=None):
    return discord.Embed(
        title=title,
        description=description,
        color=color or discord.Color.blurple(),
    )


# ============================================================
# JOIN VIEW
# ============================================================

class JoinButton(discord.ui.Button):
    def __init__(self, view):
        self.join_view = view
        super().__init__(
            label="انضمام",
            emoji="🎮",
            style=discord.ButtonStyle.success,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.join_view

        if interaction.user.id in view.players:
            await interaction.response.send_message(
                "أنت منضم بالفعل.",
                ephemeral=True,
            )
            return

        if len(view.players) >= view.maximum:
            await interaction.response.send_message(
                "اكتمل عدد اللاعبين.",
                ephemeral=True,
            )
            return

        view.players[interaction.user.id] = interaction.user

        await interaction.response.send_message(
            f"تم انضمامك. عدد اللاعبين: {len(view.players)}/{view.maximum}",
            ephemeral=True,
        )

        if len(view.players) >= view.maximum:
            view.stop()


class JoinView(discord.ui.View):
    def __init__(self, minimum=2, maximum=20, timeout=30):
        super().__init__(timeout=timeout)
        self.minimum = minimum
        self.maximum = maximum
        self.players = {}
        self.add_item(JoinButton(self))


# ============================================================
# FAST CLICK VIEW
# ============================================================

class FastClickView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=FAST_GAME_TIME)
        self.winner = None

        button = discord.ui.Button(
            label="اضغط الآن!",
            emoji="⚡",
            style=discord.ButtonStyle.success,
        )
        button.callback = self._clicked
        self.add_item(button)

    async def _clicked(self, interaction: discord.Interaction):
        if self.winner is not None:
            await interaction.response.send_message(
                "سبقك لاعب آخر.",
                ephemeral=True,
            )
            return

        self.winner = interaction.user
        self.stop()

        await interaction.response.send_message(
            "أنت أول من ضغط!",
            ephemeral=True,
        )


# ============================================================
# WHEEL GAME VIEWS
# ============================================================

class WheelActionSelect(discord.ui.Select):
    def __init__(self, view):
        self.wheel_view = view

        options = [
            discord.SelectOption(
                label="إخراج عشوائي",
                description="النظام يختار لاعبًا آخر عشوائيًا",
                value="random",
                emoji="🎲",
            ),
            discord.SelectOption(
                label="اختيار لاعب لإخراجه",
                description="اختر بنفسك لاعبًا آخر",
                value="choose",
                emoji="👤",
            ),
        ]

        super().__init__(
            placeholder="اختر طريقة الإخراج",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.wheel_view

        if interaction.user.id != view.selected_player.id:
            await interaction.response.send_message(
                "❌ هذا الخيار للاعب الذي اختارته العجلة فقط.",
                ephemeral=True,
            )
            return

        action = self.values[0]

        if action in view.action_ready_round:
            ready_round = view.action_ready_round[action]

            if view.round_number < ready_round:
                remaining = ready_round - view.round_number
                await interaction.response.send_message(
                    f"⏳ استخدمت هذا الخيار مؤخرًا. "
                    f"انتظر {remaining} جولة قبل استخدامه مجددًا.",
                    ephemeral=True,
                )
                return

        if action == "random":
            candidates = [
                player for player in view.players
                if player.id != view.selected_player.id
            ]

            if not candidates:
                await interaction.response.send_message(
                    "لا يوجد لاعب آخر لاختياره.",
                    ephemeral=True,
                )
                return

            target = random.choice(candidates)
            view.chosen_action = "random"
            view.target = target

            # يمنع هذا الخيار خلال الجولتين التاليتين.
            view.action_ready_round["random"] = view.round_number + 3

            await interaction.response.send_message(
                f"🎲 اخترت الإخراج العشوائي. الهدف: {target.display_name}",
                ephemeral=True,
            )
            view.stop()
            return

        if action == "choose":
            candidates = [
                player for player in view.players
                if player.id != view.selected_player.id
            ]

            if not candidates:
                await interaction.response.send_message(
                    "لا يوجد لاعب آخر لاختياره.",
                    ephemeral=True,
                )
                return

            view.chosen_action = "choose"
            view.action_ready_round["choose"] = view.round_number + 3

            target_view = WheelTargetView(view, candidates)

            await interaction.response.send_message(
                "👤 اختر اللاعب الذي تريد إخراجه:",
                view=target_view,
                ephemeral=True,
            )

            await target_view.wait()

            if target_view.target is not None:
                view.target = target_view.target
                view.stop()


class WheelActionView(discord.ui.View):
    def __init__(self, players, selected_player, round_number, action_ready_round):
        super().__init__(timeout=60)

        self.players = players
        self.selected_player = selected_player
        self.round_number = round_number
        self.action_ready_round = action_ready_round

        self.chosen_action = None
        self.target = None

        self.add_item(WheelActionSelect(self))


class WheelTargetSelect(discord.ui.Select):
    def __init__(self, wheel_view, candidates):
        self.wheel_view = wheel_view
        self.candidates = candidates

        options = [
            discord.SelectOption(
                label=player.display_name[:100],
                value=str(player.id),
                description=f"اختيار {player.display_name}"[:100],
            )
            for player in candidates[:25]
        ]

        super().__init__(
            placeholder="اختر لاعبًا لإخراجه",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.wheel_view

        if interaction.user.id != view.selected_player.id:
            await interaction.response.send_message(
                "❌ اللاعب الذي اختارته العجلة فقط يستطيع الاختيار.",
                ephemeral=True,
            )
            return

        target_id = int(self.values[0])

        target = next(
            (
                player for player in view.players
                if player.id == target_id
            ),
            None,
        )

        if target is None or target.id == view.selected_player.id:
            await interaction.response.send_message(
                "❌ اختيار غير صالح.",
                ephemeral=True,
            )
            return

        self.wheel_view.target = target
        await interaction.response.send_message(
            f"✅ اخترت {target.display_name}.",
            ephemeral=True,
        )
        self.view.stop()


class WheelTargetView(discord.ui.View):
    def __init__(self, wheel_view, candidates):
        super().__init__(timeout=45)
        self.target = None
        self.add_item(WheelTargetSelect(wheel_view, candidates))


# ============================================================
# GAME SYSTEM
# ============================================================

class GameSystem:
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}
        self.guild_setups = {}
        self.points = {}
        self.log_cooldowns = {}
        self.listener_added = False
        self.commands_added = False
        self.slash_added = False

    # ========================================================
    # REGISTER COMMANDS
    # ========================================================

    async def setup(self):
        if self.bot.get_command("العاب") is None:
            async def games_callback(ctx: commands.Context):
                await self.games_command(ctx)

            self.bot.add_command(
                commands.Command(
                    games_callback,
                    name="العاب",
                    help="عرض أوامر الألعاب",
                )
            )

        if self.bot.get_command("حدد_امر") is None:
            async def setup_callback(
                ctx: commands.Context,
                slot: int = None,
                channel: discord.TextChannel = None,
                role: discord.Role = None,
            ):
                await self.setup_command(ctx, slot, channel, role)

            self.bot.add_command(
                commands.Command(
                    setup_callback,
                    name="حدد_امر",
                    help="إعداد روم ورتبة الألعاب",
                )
            )

        if self.bot.get_command("stop") is None:
            async def stop_callback(ctx: commands.Context):
                await self.stop_command(ctx)

            self.bot.add_command(
                commands.Command(
                    stop_callback,
                    name="stop",
                    help="إيقاف اللعبة الحالية (للمسؤولين فقط)",
                )
            )

        for game_key, emoji, title, command_name in GAMES:
            if self.bot.get_command(command_name) is not None:
                continue

            async def game_callback(ctx: commands.Context, key=game_key):
                await self.command_start_game(ctx, key)

            self.bot.add_command(
                commands.Command(
                    game_callback,
                    name=command_name,
                    help=f"تشغيل لعبة {title}",
                )
            )

        if not self.listener_added:
            self.bot.add_listener(self.on_message, "on_message")
            self.listener_added = True

        self._register_slash_commands()

    # ========================================================
    # SLASH COMMANDS
    # ========================================================

    def _register_slash_commands(self):
        if self.slash_added:
            return

        async def setupgames_callback(
            interaction: discord.Interaction,
            slot: app_commands.Range[int, 1, 10],
            channel: discord.TextChannel,
            role: discord.Role,
        ):
            await self.slash_setupgames(interaction, int(slot), channel, role)

        async def setexploitlog_callback(
            interaction: discord.Interaction,
            channel: discord.TextChannel,
        ):
            await self.slash_set_log_channel(interaction, channel)

        async def gamesettings_callback(interaction: discord.Interaction):
            await self.slash_gamesettings(interaction)

        slash_commands = [
            app_commands.Command(
                name="setupgames",
                description="Set a game channel and required role",
                callback=setupgames_callback,
            ),
            app_commands.Command(
                name="setexploitlog",
                description="Set the denied game attempts log channel",
                callback=setexploitlog_callback,
            ),
            app_commands.Command(
                name="gamesettings",
                description="Show game setup settings",
                callback=gamesettings_callback,
            ),
        ]

        for command in slash_commands:
            try:
                if self.bot.tree.get_command(command.name) is None:
                    self.bot.tree.add_command(command)
            except Exception as error:
                print(f"[SLASH REGISTER ERROR] {command.name}: {error}")

        self.slash_added = True

    # ========================================================
    # ADMIN CHECK
    # ========================================================

    @staticmethod
    def is_admin(member):
        permissions = getattr(member, "guild_permissions", None)
        return bool(permissions and permissions.administrator)

    # ========================================================
    # LOAD SETUPS
    # ========================================================

    def load_setups(self, guild_id):
        guild_id = int(guild_id)

        if guild_id in self.guild_setups:
            return self.guild_setups[guild_id]

        setups = {}

        try:
            rows = self.bot.database.get_setups(guild_id)

            for row in rows:
                slot = int(row["slot"])
                setups[slot] = {
                    "channel_id": int(row["channel_id"]),
                    "role_id": int(row["role_id"]),
                }

        except Exception:
            traceback.print_exc()

        self.guild_setups[guild_id] = setups
        return setups

    # ========================================================
    # SAVE SETUP
    # ========================================================

    def set_setup(self, guild_id, slot, channel_id, role_id):
        slot = int(slot)

        if not 1 <= slot <= MAX_SETUP_SLOTS:
            return False

        try:
            self.bot.database.save_setup(
                int(guild_id),
                slot,
                int(channel_id),
                int(role_id),
            )
        except Exception:
            traceback.print_exc()
            return False

        self.guild_setups.setdefault(int(guild_id), {})
        self.guild_setups[int(guild_id)][slot] = {
            "channel_id": int(channel_id),
            "role_id": int(role_id),
        }

        return True

    # ========================================================
    # ACCESS CHECK
    # ========================================================

    def can_use_games(self, guild_id, channel_id, member):
        if ADMIN_BYPASS_SETUP and self.is_admin(member):
            return True

        setups = self.load_setups(guild_id)

        if not setups:
            return False

        matching_channel_setups = [
            setup for setup in setups.values()
            if setup["channel_id"] == int(channel_id)
        ]

        if not matching_channel_setups:
            return False

        member_roles = {
            role.id for role in getattr(member, "roles", [])
        }

        return any(
            setup["role_id"] in member_roles
            for setup in matching_channel_setups
        )

    # ========================================================
    # SECURITY LOGGING
    # ========================================================

    async def log_denied_attempt(
        self, guild, channel, member, game_key, reason
    ):
        if not EXPLOIT_LOGGING_ENABLED:
            return

        cooldown_key = (
            guild.id,
            member.id,
            channel.id,
            game_key,
        )

        now = time.monotonic()
        previous = self.log_cooldowns.get(cooldown_key, 0)

        if now - previous < EXPLOIT_LOG_COOLDOWN_SECONDS:
            return

        self.log_cooldowns[cooldown_key] = now

        try:
            self.bot.database.add_exploit_log(
                guild.id,
                member.id,
                channel.id,
                GAME_NAMES.get(game_key, game_key),
                reason,
            )
        except Exception:
            traceback.print_exc()

        log_channel_id = None

        try:
            log_channel_id = self.bot.database.get_log_channel(guild.id)
        except Exception:
            traceback.print_exc()

        if not log_channel_id:
            log_channel_id = EXPLOIT_LOG_CHANNEL_ID

        if not log_channel_id:
            return

        log_channel = guild.get_channel(int(log_channel_id))

        if log_channel is None:
            try:
                log_channel = await self.bot.fetch_channel(int(log_channel_id))
            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException,
            ):
                return

        report = embed(
            "🚨 محاولة تشغيل لعبة مرفوضة",
            f"👤 المستخدم: {member.mention}\n"
            f"🎮 اللعبة: **{GAME_NAMES.get(game_key, game_key)}**\n"
            f"📢 الروم: {channel.mention}\n"
            f"📝 السبب: **{reason}**\n"
            f"🕒 الوقت: <t:{int(time.time())}:F>",
            discord.Color.red(),
        )

        try:
            await log_channel.send(
                embed=report,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

    # ========================================================
    # START COMMAND
    # ========================================================

    async def command_start_game(self, ctx, game_key):
        if ctx.guild is None:
            await ctx.send("❌ الألعاب تعمل داخل السيرفر فقط.")
            return

        if not self.can_use_games(
            ctx.guild.id,
            ctx.channel.id,
            ctx.author,
        ):
            setups = self.load_setups(ctx.guild.id)

            channel_has_setup = any(
                setup["channel_id"] == ctx.channel.id
                for setup in setups.values()
            )

            reason = (
                "لا يملك الرتبة المطلوبة"
                if channel_has_setup
                else "محاولة تشغيل اللعبة في روم غير مخصص"
            )

            await self.log_denied_attempt(
                ctx.guild,
                ctx.channel,
                ctx.author,
                game_key,
                reason,
            )

            await ctx.send(
                "❌ ما عندك الصلاحية المطلوبة لتشغيل الألعاب في هذا الروم."
            )
            return

        if ctx.channel.id in self.active_games:
            await ctx.send("⚠️ توجد لعبة شغالة حاليًا في هذا الروم.")
            return

        state = {
            "game": game_key,
            "starter": ctx.author.id,
            "task": None,
            "ended": asyncio.Event(),
            "answer": None,
            "aliases": [],
            "winner": None,
        }

        self.active_games[ctx.channel.id] = state

        task = asyncio.create_task(self._run_game(ctx, game_key))
        state["task"] = task

    async def _run_game(self, ctx, game_key):
        channel_id = ctx.channel.id
        state = self.active_games.get(channel_id)

        if not state:
            return

        try:
            method = getattr(self, f"game_{game_key}", None)

            if method is None:
                await ctx.send("❌ اللعبة غير موجودة.")
                return

            await method(ctx.channel)

        except asyncio.CancelledError:
            try:
                await ctx.channel.send("🛑 تم إيقاف اللعبة.")
            except discord.HTTPException:
                pass
            raise

        except Exception as error:
            print(f"[GAME ERROR] {game_key}: {error}")
            traceback.print_exc()

            try:
                await ctx.send("❌ حدث خطأ أثناء اللعبة.")
            except discord.HTTPException:
                pass

        finally:
            current = self.active_games.get(channel_id)

            if current is state:
                self.active_games.pop(channel_id, None)

    # ========================================================
    # -العاب
    # ========================================================

    async def games_command(self, ctx):
        if ctx.guild is None:
            await ctx.send("❌ هذا الأمر داخل السيرفر فقط.")
            return

        if not self.can_use_games(
            ctx.guild.id,
            ctx.channel.id,
            ctx.author,
        ):
            await ctx.send("❌ ما عندك الصلاحية المطلوبة لعرض الألعاب هنا.")
            return

        lines = ["🎮 **أوامر الألعاب:**", ""]

        for key, emoji, title, command_name in GAMES:
            lines.append(f"{emoji} `{PREFIX}{command_name}` — {title}")

        lines.extend(["", f"لإيقاف اللعبة الحالية: `{PREFIX}stop`"])
        await ctx.send("\n".join(lines))

    # ========================================================
    # -حدد_امر
    # ========================================================

    async def setup_command(self, ctx, slot=None, channel=None, role=None):
        if ctx.guild is None:
            await ctx.send("❌ هذا الأمر داخل السيرفر فقط.")
            return

        if not self.is_admin(ctx.author):
            await ctx.send("❌ هذا الأمر للمسؤولين فقط.")
            return

        if slot is None or channel is None or role is None:
            await ctx.send(
                "طريقة الاستخدام:\n"
                f"`{PREFIX}حدد_امر رقم_الإعداد #الروم @الرتبة`\n\n"
                "مثال:\n"
                f"`{PREFIX}حدد_امر 1 #الألعاب @لاعب`\n\n"
                f"يمكنك إعداد حتى **{MAX_SETUP_SLOTS}** إعدادات."
            )
            return

        if not 1 <= int(slot) <= MAX_SETUP_SLOTS:
            await ctx.send(
                f"❌ رقم الإعداد يجب أن يكون من 1 إلى {MAX_SETUP_SLOTS}."
            )
            return

        saved = self.set_setup(
            ctx.guild.id,
            slot,
            channel.id,
            role.id,
        )

        if not saved:
            await ctx.send("❌ تعذر حفظ الإعداد في قاعدة البيانات.")
            return

        await ctx.send(
            f"✅ تم حفظ الإعداد **{slot}**.\n"
            f"📢 الروم: {channel.mention}\n"
            f"👤 الرتبة: {role.mention}"
        )

    # ========================================================
    # /setupgames
    # ========================================================

    async def slash_setupgames(self, interaction, slot, channel, role):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ هذا الأمر داخل السيرفر فقط.",
                ephemeral=True,
            )
            return

        if not self.is_admin(interaction.user):
            await interaction.response.send_message(
                "❌ هذا الأمر للمسؤولين فقط.",
                ephemeral=True,
            )
            return

        if not 1 <= int(slot) <= MAX_SETUP_SLOTS:
            await interaction.response.send_message(
                f"❌ اختر رقمًا بين 1 و{MAX_SETUP_SLOTS}.",
                ephemeral=True,
            )
            return

        saved = self.set_setup(
            interaction.guild.id,
            slot,
            channel.id,
            role.id,
        )

        if not saved:
            await interaction.response.send_message(
                "❌ تعذر حفظ الإعداد.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ تم إعداد رقم **{slot}**.\n"
            f"📢 الروم: {channel.mention}\n"
            f"👤 الرتبة المطلوبة: {role.mention}",
            ephemeral=True,
        )

    # ========================================================
    # /setexploitlog
    # ========================================================

    async def slash_set_log_channel(self, interaction, channel):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ هذا الأمر داخل السيرفر فقط.",
                ephemeral=True,
            )
            return

        if not self.is_admin(interaction.user):
            await interaction.response.send_message(
                "❌ هذا الأمر للمسؤولين فقط.",
                ephemeral=True,
            )
            return

        try:
            self.bot.database.set_log_channel(
                interaction.guild.id,
                channel.id,
            )
        except Exception:
            traceback.print_exc()
            await interaction.response.send_message(
                "❌ تعذر حفظ روم السجلات.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ تم تعيين روم سجلات المحاولات المرفوضة: {channel.mention}",
            ephemeral=True,
        )

    # ========================================================
    # /gamesettings
    # ========================================================

    async def slash_gamesettings(self, interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ هذا الأمر داخل السيرفر فقط.",
                ephemeral=True,
            )
            return

        if not self.is_admin(interaction.user):
            await interaction.response.send_message(
                "❌ هذا الأمر للمسؤولين فقط.",
                ephemeral=True,
            )
            return

        setups = self.load_setups(interaction.guild.id)
        lines = []

        for slot, setup in sorted(setups.items()):
            lines.append(
                f"**الإعداد {slot}:** "
                f"<#{setup['channel_id']}> — "
                f"<@&{setup['role_id']}>"
            )

        if not lines:
            lines.append("لا توجد إعدادات ألعاب محفوظة.")

        try:
            log_id = self.bot.database.get_log_channel(interaction.guild.id)
        except Exception:
            log_id = None

        lines.extend([
            "",
            f"**روم السجلات:** {f'<#{log_id}>' if log_id else 'غير محدد'}",
        ])

        await interaction.response.send_message(
            embed=embed("⚙️ إعدادات الألعاب", "\n".join(lines)),
            ephemeral=True,
        )

    # ========================================================
    # -stop
    # ========================================================

    async def stop_command(self, ctx):
        if ctx.guild is None:
            await ctx.send("❌ هذا الأمر داخل السيرفر فقط.")
            return

        if not self.is_admin(ctx.author):
            await ctx.send(f"❌ أمر `{PREFIX}stop` للمسؤولين فقط.")
            return

        state = self.active_games.get(ctx.channel.id)

        if not state:
            await ctx.send("ℹ️ لا توجد لعبة شغالة في هذا الروم.")
            return

        task = state.get("task")

        if task and not task.done():
            task.cancel()

        await ctx.send("🛑 تم طلب إيقاف اللعبة.")

    # ========================================================
    # MESSAGE ANSWERS
    # ========================================================

    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return

        if message.content.startswith(PREFIX):
            return

        state = self.active_games.get(message.channel.id)

        if not state or state.get("ended").is_set():
            return

        answer = state.get("answer")

        if answer is None:
            return

        if matches_answer(message.content, answer, state.get("aliases")):
            state["winner"] = message.author
            state["ended"].set()

    # ========================================================
    # ANSWER ROUND HELPER
    # ========================================================

    async def text_round(
        self,
        channel,
        title,
        description,
        answer,
        aliases=None,
        timeout=TEXT_GAME_TIME,
        image=None,
    ):
        state = self.active_games.get(channel.id)

        if not state:
            return None

        state["answer"] = answer
        state["aliases"] = aliases or []
        state["winner"] = None
        state["ended"] = asyncio.Event()

        game_embed = embed(title, description)

        if image:
            game_embed.set_image(url=image)

        await channel.send(embed=game_embed)

        try:
            await asyncio.wait_for(state["ended"].wait(), timeout=timeout)
        except asyncio.TimeoutError:
            pass

        winner = state.get("winner")

        if winner:
            await self.winner(channel, winner)
        else:
            await channel.send(f"⏰ انتهى الوقت! الإجابة: **{answer}**")

        return winner

    # ========================================================
    # WINNER + POINTS
    # ========================================================

    async def winner(self, channel, member, points=WIN_POINTS):
        if member is None:
            return

        self.points[member.id] = self.points.get(member.id, 0) + points

        await channel.send(
            embed=embed(
                "🏆 الفائز!",
                f"🎉 الفائز: {member.mention}\n⭐ النقاط: **+{points}**",
                discord.Color.green(),
            )
        )

        guild = getattr(channel, "guild", None)

        if guild is None:
            return

        try:
            self.bot.database.add_win(guild.id, member.id, points)
        except Exception:
            traceback.print_exc()

        try:
            game_key = self.active_games.get(channel.id, {}).get("game", "unknown")
            self.bot.database.add_game_history(
                guild.id,
                channel.id,
                GAME_NAMES.get(game_key, game_key),
                member.id,
                points,
            )
        except Exception:
            traceback.print_exc()

    # ========================================================
    # MULTIPLAYER JOIN HELPER
    # ========================================================

    async def collect_players(
        self,
        channel,
        title,
        description,
        minimum=2,
        maximum=20,
        timeout=30,
    ):
        view = JoinView(
            minimum=minimum,
            maximum=maximum,
            timeout=timeout,
        )

        await channel.send(
            embed=embed(title, description + "\n\nاضغط زر الانضمام."),
            view=view,
        )

        await view.wait()
        players = list(view.players.values())

        if len(players) < minimum:
            await channel.send(
                f"❌ لم يكتمل العدد المطلوب. تحتاج {minimum} لاعبين على الأقل."
            )
            return []

        return players

    # ========================================================
    # GAME 1 - ROULETTE
    # ========================================================

    async def game_roulette(self, channel):
        players = await self.collect_players(
            channel, "🎯 روليت", "لعبة إقصاء عشوائي بدون رهانات.",
            2, 20, ROULETTE_TIME,
        )

        if not players:
            return

        while len(players) > 1:
            await asyncio.sleep(2)
            eliminated = random.choice(players)
            players.remove(eliminated)
            await channel.send(f"🎯 خرج {eliminated.mention} من الجولة!")

        await self.winner(channel, players[0])

    # ========================================================
    # GAME 2 - XO
    # ========================================================

    async def game_xo(self, channel):
        await self.play_xo(channel, fiery=False)

    # ========================================================
    # GAME 3 - MAFIA
    # ========================================================

    async def game_mafia(self, channel):
        players = await self.collect_players(
            channel, "🕵️ مافيا", "انضم للعبة. تحتاج 4 لاعبين على الأقل.",
            4, 12, 30,
        )

        if not players:
            return

        mafia_count = max(1, len(players) // 4)
        mafia = random.sample(players, mafia_count)
        mafia_ids = {player.id for player in mafia}

        for player in players:
            try:
                if player.id in mafia_ids:
                    await player.send("🕵️ دورك: **مافيا**. حاول ألا تكشف هويتك.")
                else:
                    await player.send("👤 دورك: **مواطن**. حاول اكتشاف المافيا.")
            except discord.HTTPException:
                pass

        await channel.send(
            f"🕵️ بدأت المافيا!\n👥 اللاعبون: **{len(players)}**\n"
            f"🕵️ المافيا: **{mafia_count}**\n"
            f"⏱️ تنتهي الجولة خلال {MAFIA_TIME} ثانية."
        )

        await asyncio.sleep(MAFIA_TIME)

        survivors = [p for p in players if p.id not in mafia_ids]
        winner = random.choice(survivors or players)

        await channel.send(
            "🔎 انتهت الجولة. تم كشف الأدوار:\n"
            + "\n".join(
                f"{'🕵️ مافيا' if p.id in mafia_ids else '👤 مواطن'}: {p.mention}"
                for p in players
            )
        )

        await self.winner(channel, winner)

    # ========================================================
    # GAME 4 - MUSICAL CHAIRS
    # ========================================================

    async def game_musical_chairs(self, channel):
        players = await self.collect_players(
            channel, "🪑 الكراسي الموسيقية", "ابقَ حتى تكون آخر لاعب.",
            3, 20, 30,
        )

        if not players:
            return

        while len(players) > 1:
            await channel.send("🎵 الموسيقى شغالة...")
            await asyncio.sleep(2)
            eliminated = random.choice(players)
            players.remove(eliminated)
            await channel.send(f"🪑 توقفت الموسيقى! خرج {eliminated.mention}.")
            await asyncio.sleep(1)

        await self.winner(channel, players[0])

    # ========================================================
    # GAME 5 - ROCK PAPER SCISSORS
    # ========================================================

    async def game_rps(self, channel):
        players = await self.collect_players(
            channel, "🪨 حجر ورق مقص", "أول لاعبين ينضمان يدخلان الجولة.",
            2, 2, 30,
        )

        if len(players) != 2:
            return

        choices = {}
        allowed = {
            "حجر": "rock", "ورق": "paper", "مقص": "scissors",
            "rock": "rock", "paper": "paper", "scissors": "scissors",
        }

        await channel.send("اكتبوا اختياركم برسالة:\n`حجر` أو `ورق` أو `مقص`.")

        async def get_choice(player):
            def check(message):
                return (
                    message.author.id == player.id
                    and message.channel.id == channel.id
                    and normalize(message.content) in {
                        normalize(k) for k in allowed
                    }
                )

            message = await self.bot.wait_for(
                "message", timeout=FAST_GAME_TIME, check=check,
            )
            choices[player.id] = allowed[normalize(message.content)]

        try:
            await asyncio.gather(get_choice(players[0]), get_choice(players[1]))
        except asyncio.TimeoutError:
            await channel.send("⏰ انتهى الوقت قبل أن يختار اللاعبان.")
            return

        a = choices[players[0].id]
        b = choices[players[1].id]

        if a == b:
            await channel.send("🤝 تعادل! أعد تشغيل اللعبة لجولة جديدة.")
            return

        wins = {
            ("rock", "scissors"),
            ("paper", "rock"),
            ("scissors", "paper"),
        }

        await self.winner(channel, players[0] if (a, b) in wins else players[1])

    # ========================================================
    # GAME 6 - FIERY XO
    # ========================================================

    async def game_fiery_xo(self, channel):
        await self.play_xo(channel, fiery=True)

    # ========================================================
    # XO ENGINE
    # ========================================================

    async def play_xo(self, channel, fiery=False):
        players = await self.collect_players(
            channel,
            "🔥 إكس أو النارية" if fiery else "❌⭕ إكس أو",
            "تحتاج لاعبين اثنين.",
            2, 2, 30,
        )

        if len(players) != 2:
            return

        board = ["⬜"] * 9
        symbols = {players[0].id: "❌", players[1].id: "⭕"}
        current_index = 0
        fire_cells = set(random.sample(range(9), 2)) if fiery else set()

        combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6),
        ]

        def render():
            shown = [
                "🔥" if fiery and i in fire_cells and board[i] == "⬜" else board[i]
                for i in range(9)
            ]
            return (
                f"{shown[0]} {shown[1]} {shown[2]}\n"
                f"{shown[3]} {shown[4]} {shown[5]}\n"
                f"{shown[6]} {shown[7]} {shown[8]}"
            )

        await channel.send(
            f"**{'🔥 إكس أو النارية' if fiery else '❌⭕ إكس أو'}**\n"
            f"{render()}\n\nاكتب رقم الخانة من 1 إلى 9."
        )

        for _ in range(9):
            player = players[current_index]

            def check(message):
                return (
                    message.channel.id == channel.id
                    and message.author.id == player.id
                    and message.content.strip() in {str(i) for i in range(1, 10)}
                )

            try:
                message = await self.bot.wait_for("message", timeout=120, check=check)
            except asyncio.TimeoutError:
                await channel.send("⏰ انتهى وقت اللعبة.")
                return

            index = int(message.content.strip()) - 1

            if board[index] != "⬜":
                await channel.send("❌ الخانة مستخدمة. انتهت فرصتك لهذا الدور.")
                current_index = 1 - current_index
                continue

            if fiery and index in fire_cells:
                winner = players[1 - current_index]
                await channel.send(
                    f"🔥 ضغط {player.mention} على خانة نارية وخسر!\n"
                    f"🏆 الفائز: {winner.mention}"
                )
                await self.winner(channel, winner)
                return

            board[index] = symbols[player.id]

            for a, b, c in combinations:
                if board[a] == board[b] == board[c] and board[a] in ("❌", "⭕"):
                    await channel.send(f"{render()}\n\n🏆 الفائز: {player.mention}")
                    await self.winner(channel, player)
                    return

            await channel.send(render())
            current_index = 1 - current_index

        await channel.send("🤝 انتهت اللعبة بالتعادل.")

    # ========================================================
    # GAME 7 - HIDE AND SEEK
    # ========================================================

    async def game_hide_seek(self, channel):
        players = await self.collect_players(
            channel, "👀 الغميضة", "انضم للعبة.",
            3, 15, 30,
        )

        if len(players) < 3:
            return

        seeker = random.choice(players)
        hidden = random.choice([p for p in players if p.id != seeker.id])

        await channel.send(
            f"👀 الباحث: {seeker.mention}\n"
            f"🙈 تم اختيار المختبئ. أمام الباحث {HIDE_SEEK_TIME} ثانية."
        )

        await asyncio.sleep(HIDE_SEEK_TIME)
        await channel.send(f"🔎 كان المختبئ: {hidden.mention}")
        await self.winner(channel, seeker)

    # ========================================================
    # GAME 8 - REPLIKA
    # ========================================================

    async def game_replika(self, channel):
        sentence = random.choice([
            "انا احب البرمجة", "اليوم الجو جميل", "البوت سريع جدا",
            "الالعاب ممتعة", "هذا اختبار سرعة", "ديسكورد رائع",
        ])

        await self.text_round(
            channel, "🤖 ريبلكا",
            f"انسخ الجملة كما هي:\n\n**{sentence}**",
            sentence, timeout=TEXT_GAME_TIME,
        )

    # ========================================================
    # GAME 9 - GUESS COUNTRY
    # ========================================================

    async def game_guess_country(self, channel):
        country, aliases, code, clue = random.choice(FLAGS)

        await self.text_round(
            channel, "🌍 خمن الدولة", f"💡 التلميح: {clue}",
            country, aliases, GUESS_TIME,
        )

    # ========================================================
    # GAME 10 - GUESS DRAWING
    # ========================================================

    async def game_guess_drawing(self, channel):
        item = random.choice(DRAWINGS)

        await self.text_round(
            channel, "🎨 خمن الرسمة",
            f"ما الموجود في الصورة؟\n"
            f"🔤 عدد الحروف: **{len(item['answer'].replace(' ', ''))}**",
            item["answer"], item["aliases"], GUESS_TIME, item["image"],
        )

    # ========================================================
    # GAME 11 - GUESS WORD
    # ========================================================

    async def game_guess_word(self, channel):
        word, aliases = random.choice(WORDS)
        masked = " ".join("⬜" if not char.isspace() else " " for char in word)

        await self.text_round(
            channel, "📝 خمن الكلمة",
            f"الكلمة:\n\n{masked}\n\n🔤 عدد الحروف: **{len(word)}**",
            word, aliases, GUESS_TIME,
        )

    # ========================================================
    # GAME 12 - FAST CLICK
    # ========================================================

    async def game_fast_click(self, channel):
        await channel.send("⚡ استعد...")
        await asyncio.sleep(random.uniform(2, 5))

        view = FastClickView()

        await channel.send(
            embed=embed("⚡ اضغط الآن!", "أول شخص يضغط الزر يفوز."),
            view=view,
        )

        await view.wait()

        if view.winner:
            await self.winner(channel, view.winner)
        else:
            await channel.send("⏰ لم يضغط أحد في الوقت المحدد.")

    # ========================================================
    # GAME 13 - FAST TYPE
    # ========================================================

    async def game_fast_type(self, channel):
        text = random.choice([
            "سرعة", "ديسكورد", "العاب", "برمجة",
            "بوت", "مسابقة", "تحدي", "سرعة الكتابة",
        ])

        await self.text_round(
            channel, "⌨️ الكتابة السريعة",
            f"اكتب الكلمة بالضبط:\n\n**{text}**",
            text, timeout=TEXT_GAME_TIME,
        )

    # ========================================================
    # GAME 14 - TEXT SPLIT
    # ========================================================

    async def game_text_split(self, channel):
        word = random.choice([
            "ديسكورد", "برمجة", "مسابقة", "روبوت", "العاب", "تحدي",
        ])
        answer = " ".join(word)

        await self.text_round(
            channel, "✂️ فصل النص",
            f"افصل الحروف بمسافات:\n\n**{word}**\n\nمثال: `{answer}`",
            answer, timeout=TEXT_GAME_TIME,
        )

    # ========================================================
    # GAME 15 - MERGE TEXT
    # ========================================================

    async def game_merge_text(self, channel):
        word = random.choice([
            "د ي س ك و ر د", "ب ر م ج ة", "م س ا ب ق ة",
            "ا ل ع ا ب", "ت ح د ي",
        ])
        answer = word.replace(" ", "")

        await self.text_round(
            channel, "🔗 دمج النص",
            f"ادمج الحروف:\n\n**{word}**",
            answer, timeout=TEXT_GAME_TIME,
        )

    # ========================================================
    # GAME 16 - GUESS FLAG
    # ========================================================

    async def game_guess_flag(self, channel):
        country, aliases, code, clue = random.choice(FLAGS)

        await self.text_round(
            channel, "🏳️ خمن العلم", "ما الدولة صاحبة هذا العلم؟",
            country, aliases, GUESS_TIME,
            f"https://flagcdn.com/w640/{code}.png",
        )

    # ========================================================
    # GAME 17 - TEXT REVERSE
    # ========================================================

    async def game_text_reverse(self, channel):
        word = random.choice([
            "ديسكورد", "العاب", "مسابقة", "برمجة", "بوت", "تحدي",
        ])

        await self.text_round(
            channel, "🔄 عكس النص",
            f"اعكس النص:\n\n**{word}**",
            word[::-1], timeout=TEXT_GAME_TIME,
        )

    # ========================================================
    # GAME 18 - FIND LETTER
    # ========================================================

    async def game_find_letter(self, channel):
        letters = list("ابتثجحخدذرزسشصضطظعغفقكلمنهوي")
        target = random.choice(letters)
        other_letters = [x for x in letters if x != target]
        sequence = [random.choice(other_letters) for _ in range(49)]
        sequence.insert(random.randint(0, 49), target)

        await self.text_round(
            channel, "🔤 ابحث عن الحرف",
            f"الحرف المطلوب: **{target}**\n\n" + " ".join(sequence),
            target, timeout=TEXT_GAME_TIME,
        )

    # ========================================================
    # GAME 19 - CORRECT LETTER
    # ========================================================

    async def game_correct_letter(self, channel):
        letters = list("ابتثجحخدذرزسشصضطظعغفقكلمنهوي")
        target = random.choice(letters)
        fake = random.choice([x for x in letters if x != target])
        sequence = [fake for _ in range(30)]
        correct_index = random.randrange(30)
        sequence[correct_index] = target

        await self.text_round(
            channel, "✅ الحرف الصحيح",
            f"الحرف المطلوب: **{target}**\n\n"
            + " ".join(sequence)
            + "\n\nأرسل رقم مكانه من 1 إلى 30.",
            str(correct_index + 1), timeout=TEXT_GAME_TIME,
        )

    # ========================================================
    # GAME 20 - SORT NUMBERS
    # ========================================================

    async def game_sort_numbers(self, channel):
        numbers = random.sample(range(1, 50), 6)
        scrambled = numbers[:]
        random.shuffle(scrambled)
        answer = " ".join(str(n) for n in sorted(numbers))

        await self.text_round(
            channel, "🔢 ترتيب الأرقام",
            "رتب الأرقام من الأصغر إلى الأكبر:\n\n"
            + " — ".join(str(n) for n in scrambled)
            + "\n\nمثال: `1 2 3 4 5 6`",
            answer, timeout=TEXT_GAME_TIME,
        )

    # ========================================================
    # GAME 21 - GUESS COLOR
    # ========================================================

    async def game_guess_color(self, channel):
        name, aliases, emoji = random.choice(COLORS)

        await self.text_round(
            channel, "🎨 خمن اللون",
            f"اللون الظاهر:\n\n# {emoji}\n\nاكتب اسم اللون.",
            name, aliases, GUESS_TIME,
        )

    # ========================================================
    # GAME 22 - FIND EMOJI
    # ========================================================

    async def game_find_emoji(self, channel):
        emojis = [
            "😀", "😂", "😎", "🤖", "🐱",
            "🐶", "🍎", "🍕", "⚽", "🔥",
        ]

        target = random.choice(emojis)
        others = [x for x in emojis if x != target]
        sequence = [random.choice(others) for _ in range(49)]
        sequence.insert(random.randint(0, 49), target)

        await self.text_round(
            channel, "🔎 ابحث عن الإيموجي",
            f"الإيموجي المطلوب: **{target}**\n\n" + " ".join(sequence),
            target, timeout=TEXT_GAME_TIME,
        )

    # ========================================================
    # GAME 23 - TEXT REVEAL
    # ========================================================

    async def game_text_reveal(self, channel):
        word, aliases = random.choice(WORDS)
        visible = set()
        state = self.active_games.get(channel.id)

        if not state:
            return

        state["answer"] = word
        state["aliases"] = aliases
        state["winner"] = None
        state["ended"] = asyncio.Event()

        def masked():
            output = []

            for index, char in enumerate(word):
                if char.isspace():
                    output.append(" ")
                elif index in visible:
                    output.append(char)
                else:
                    output.append("⬜")

            return " ".join(output)

        message = await channel.send(
            embed=embed(
                "👁️ كشف النص",
                f"الكلمة تحتوي على **{len(word)} حروف**.\n\n"
                f"{masked()}\n\nسيتم كشف حروف تدريجيًا.",
            )
        )

        reveal_count = min(3, len([c for c in word if not c.isspace()]))

        for _ in range(reveal_count):
            try:
                await asyncio.wait_for(state["ended"].wait(), timeout=5)
                break
            except asyncio.TimeoutError:
                pass

            if self.active_games.get(channel.id) is not state:
                return

            available = [
                i for i, char in enumerate(word)
                if not char.isspace() and i not in visible
            ]

            if not available:
                break

            visible.add(random.choice(available))

            try:
                await message.edit(
                    embed=embed(
                        "👁️ كشف النص",
                        f"الكلمة تحتوي على **{len(word)} حروف**.\n\n"
                        f"{masked()}\n\n💡 حاول التخمين!",
                    )
                )
            except discord.HTTPException:
                pass

        if not state["ended"].is_set():
            try:
                await asyncio.wait_for(
                    state["ended"].wait(),
                    timeout=max(1, TEXT_GAME_TIME - reveal_count * 5),
                )
            except asyncio.TimeoutError:
                pass

        winner = state.get("winner")

        if winner:
            await self.winner(channel, winner)
        else:
            await channel.send(f"⏰ الإجابة: **{word}**")

    # ========================================================
    # GAME 24 - WHEEL
    # ========================================================

    async def game_wheel(self, channel):
        players = await self.collect_players(
            channel,
            "🎡 عجلة الإقصاء",
            "انضم للعجلة!\n"
            "🎯 تحتاج 4 لاعبين على الأقل.\n"
            "🎲 في كل جولة تختار العجلة لاعبًا واحدًا ليقرر طريقة الإقصاء.\n"
            "🛡️ إذا تجاوز العدد 5 لاعبين، يحصل لاعب عشوائي على حصانة مرة واحدة.",
            minimum=4,
            maximum=20,
            timeout=45,
        )

        if len(players) < 4:
            return

        # الحصانة تظهر فقط عندما يكون عدد اللاعبين أكثر من خمسة.
        immune_player = random.choice(players) if len(players) > 5 else None
        immunity_used = False

        if immune_player:
            try:
                await immune_player.send(
                    "🛡️ **حصانة عجلة الإقصاء**\n"
                    "أنت حصلت على حصانة سرية لمرة واحدة.\n"
                    "إذا اختارك لاعب للإخراج، ستمنع خروجك وتُستهلك الحصانة."
                )
            except discord.HTTPException:
                # لا نكشف هوية صاحب الحصانة في الروم العام.
                pass

        # cooldown لكل خيار، خاص بهذه اللعبة فقط.
        action_ready_round = {}
        round_number = 1

        await channel.send(
            embed=embed(
                "🎡 بدأت عجلة الإقصاء!",
                f"👥 عدد اللاعبين: **{len(players)}**\n"
                "🎡 ستدور العجلة في كل جولة حتى يبقى لاعب واحد.\n"
                "🛡️ الحصانة - إن وُجدت - سرية.",
            )
        )

        while len(players) > 1:
            # تحديث حالة اللعبة: لا نسمح بتشغيل عجلة أخرى في الروم.
            state = self.active_games.get(channel.id)
            if not state:
                return

            await channel.send(
                embed=embed(
                    "🎡 العجلة تدور...",
                    "🔄 يجري اختيار لاعب عشوائيًا...",
                )
            )

            # حركة مرئية متتابعة توحي بدوران العجلة.
            animation_steps = min(12, max(6, len(players) + 4))

            for step in range(animation_steps):
                shown_player = random.choice(players)

                try:
                    await channel.send(
                        f"🎡 {'🔄' if step % 2 == 0 else '✨'} "
                        f"**{shown_player.display_name}**"
                    )
                except discord.HTTPException:
                    pass

                await asyncio.sleep(0.25 + step * 0.025)

            selected_player = random.choice(players)

            await channel.send(
                embed=embed(
                    "🎯 توقفت العجلة!",
                    f"اختارت العجلة: {selected_player.mention}\n"
                    "هذا اللاعب وحده يحق له اختيار طريقة الإخراج.",
                    discord.Color.gold(),
                )
            )

            view = WheelActionView(
                players=players,
                selected_player=selected_player,
                round_number=round_number,
                action_ready_round=action_ready_round,
            )

            await channel.send(
                f"🎮 {selected_player.mention}، اختر الإجراء من القائمة:",
                view=view,
            )

            await view.wait()

            if view.target is None:
                # إذا لم يختَر اللاعب خلال المهلة، نختار لاعبًا آخر عشوائيًا.
                candidates = [
                    player for player in players
                    if player.id != selected_player.id
                ]

                if not candidates:
                    break

                target = random.choice(candidates)

                await channel.send(
                    f"⏰ لم يختر {selected_player.mention} خلال المهلة.\n"
                    f"🎲 تم اختيار {target.mention} عشوائيًا للإقصاء."
                )
            else:
                target = view.target

            if target not in players:
                round_number += 1
                continue

            # الحصانة تمنع الإقصاء مرة واحدة فقط.
            if (
                immune_player is not None
                and target.id == immune_player.id
                and not immunity_used
            ):
                immunity_used = True

                await channel.send(
                    embed=embed(
                        "🛡️ الحصانة فعّالة!",
                        f"تم اختيار {target.mention} للإقصاء، "
                        "لكن لديه حصانة!\n"
                        "لن يخرج في هذه المرة، وقد استُهلكت حصانته.",
                        discord.Color.green(),
                    )
                )
            else:
                players.remove(target)

                await channel.send(
                    embed=embed(
                        "🚪 تم إقصاء لاعب",
                        f"خرج {target.mention} من العجلة.\n"
                        f"👥 اللاعبون المتبقون: **{len(players)}**",
                        discord.Color.red(),
                    )
                )

            round_number += 1

            if len(players) > 1:
                await asyncio.sleep(1)

        if len(players) == 1:
            await channel.send(
                embed=embed(
                    "🏆 انتهت عجلة الإقصاء!",
                    f"🎉 الفائز الأخير هو: {players[0].mention}",
                    discord.Color.green(),
                )
            )
            await self.winner(channel, players[0])
        else:
            await channel.send("انتهت اللعبة دون وجود فائز.")


# ============================================================
# EXPORT
# ============================================================

__all__ = ["GameSystem"]
