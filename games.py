# ============================================================
# GAME BOT - GAMES.PY
# FULL VERSION - 24 GAMES INCLUDING WHEEL
# Python 3.14+ / discord.py 2.7+
# ============================================================

import asyncio
import io
import random
import re
import time
import traceback

import discord
from discord import app_commands
from discord.ext import commands

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
except ImportError:
    Image = None
    ImageDraw = None
    ImageFilter = None
    ImageEnhance = None

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
EXPLOIT_LOG_COOLDOWN_SECONDS = getattr(
    cfg, "EXPLOIT_LOG_COOLDOWN_SECONDS", 5
)
EXPLOIT_LOGGING_ENABLED = getattr(
    cfg, "EXPLOIT_LOGGING_ENABLED", True
)
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

GAME_NAMES = {
    key: name for key, emoji, name, command in GAMES
}
GAME_COMMANDS = {
    key: command for key, emoji, name, command in GAMES
}


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
    {"answer": "تفاحة", "aliases": ["تفاح", "apple"], "kind": "apple"},
    {"answer": "قطة", "aliases": ["قط", "بس", "cat"], "kind": "cat"},
    {"answer": "كلب", "aliases": ["dog"], "kind": "dog"},
    {"answer": "بيتزا", "aliases": ["pizza"], "kind": "pizza"},
    {"answer": "سيارة", "aliases": ["سياره", "car"], "kind": "car"},
    {"answer": "طائرة", "aliases": ["طياره", "plane", "airplane"], "kind": "airplane"},
    {"answer": "دراجة", "aliases": ["دراجه", "bike", "bicycle"], "kind": "bicycle"},
    {"answer": "كرة", "aliases": ["كره", "ball", "football"], "kind": "ball"},
    {"answer": "شجرة", "aliases": ["شجره", "tree"], "kind": "tree"},
    {"answer": "بيت", "aliases": ["house"], "kind": "house"},
    {"answer": "سمكة", "aliases": ["سمكه", "fish"], "kind": "fish"},
]

FLAGS = [
    ("السعودية", ["السعوديه", "saudi", "saudi arabia"], "sa", "تقع في شبه الجزيرة العربية."),
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
# HARD-TO-GUESS DRAWING GENERATOR
# ============================================================

def make_drawing_file(kind):
    """ينشئ رسمة محلية متغيرة ومشوّشة باستخدام Pillow."""
    if Image is None or ImageDraw is None:
        raise RuntimeError(
            "مكتبة Pillow غير مثبتة. أضف Pillow إلى requirements.txt."
        )

    size = 512
    background_colors = [
        (238, 235, 229),
        (225, 237, 240),
        (231, 225, 240),
        (231, 238, 224),
        (244, 226, 216),
        (230, 230, 230),
        (219, 225, 234),
    ]
    line_colors = [
        (40, 45, 55),
        (65, 50, 65),
        (45, 65, 70),
        (75, 60, 45),
        (55, 55, 55),
    ]
    accent_colors = [
        (231, 76, 60),
        (46, 134, 193),
        (39, 174, 96),
        (142, 68, 173),
        (230, 126, 34),
        (225, 180, 40),
        (35, 155, 145),
        (190, 70, 130),
    ]

    image = Image.new("RGB", (size, size), random.choice(background_colors))
    draw = ImageDraw.Draw(image)
    outline = random.choice(line_colors)
    accent = random.choice(accent_colors)
    second_accent = random.choice(accent_colors)

    scale = random.uniform(0.70, 1.08)
    dx = random.randint(-45, 45)
    dy = random.randint(-40, 40)

    def point(x, y):
        return (
            int(256 + (x - 256) * scale + dx),
            int(256 + (y - 256) * scale + dy),
        )

    def box(x1, y1, x2, y2):
        return point(x1, y1) + point(x2, y2)

    def line(points, fill=None, width=8):
        transformed = [point(x, y) for x, y in points]
        draw.line(
            transformed,
            fill=fill or outline,
            width=max(2, int(width * random.uniform(0.65, 1.3))),
            joint="curve",
        )

    def ellipse(coords, fill, outline_color=None, width=7):
        draw.ellipse(
            box(*coords),
            fill=fill,
            outline=outline_color or outline,
            width=max(2, int(width * random.uniform(0.7, 1.3))),
        )

    def polygon(points, fill, outline_color=None):
        transformed = [point(x, y) for x, y in points]
        draw.polygon(transformed, fill=fill)
        draw.line(
            transformed + [transformed[0]],
            fill=outline_color or outline,
            width=random.randint(4, 10),
            joint="curve",
        )

    if kind == "apple":
        ellipse((155, 185, 270, 335), random.choice([(210, 65, 65), accent]))
        ellipse((240, 185, 355, 335), random.choice([(210, 65, 65), accent]))
        line([(255, 195), (265, 135)], (105, 65, 35), 12)
        ellipse((266, 133, 330, 165), (55, 160, 80), width=4)

    elif kind == "cat":
        polygon([(145, 200), (155, 110), (220, 170)], (220, 170, 115))
        polygon([(292, 170), (365, 110), (370, 205)], (220, 170, 115))
        ellipse((145, 155, 370, 370), (220, 170, 115))
        ellipse((195, 225, 220, 250), (40, 40, 40), width=2)
        ellipse((295, 225, 320, 250), (40, 40, 40), width=2)
        polygon([(244, 265), (270, 265), (257, 280)], (220, 90, 100))
        line([(257, 280), (257, 294)], width=4)
        line([(230, 295), (185, 285)], width=4)
        line([(285, 295), (330, 285)], width=4)

    elif kind == "dog":
        ellipse((150, 150, 360, 360), (190, 140, 90))
        ellipse((130, 180, 190, 300), (130, 85, 55))
        ellipse((320, 180, 380, 300), (130, 85, 55))
        ellipse((195, 225, 220, 250), (30, 30, 30), width=2)
        ellipse((290, 225, 315, 250), (30, 30, 30), width=2)
        ellipse((225, 265, 285, 310), (240, 215, 185))
        ellipse((243, 270, 270, 290), (30, 30, 30), width=2)

    elif kind == "pizza":
        polygon([(120, 125), (395, 170), (245, 390)], (235, 180, 80))
        line([(120, 125), (395, 170)], (155, 90, 40), 18)
        for px, py in [
            (225, 190), (310, 205), (270, 260),
            (235, 310), (335, 235),
        ]:
            ellipse((px, py, px + 28, py + 28), (195, 45, 45), width=3)

    elif kind == "car":
        draw.rounded_rectangle(
            box(95, 220, 420, 335),
            radius=random.randint(12, 30),
            fill=accent,
            outline=outline,
            width=7,
        )
        polygon(
            [(155, 220), (205, 155), (320, 155), (365, 220)],
            (110, 180, 205),
        )
        ellipse((135, 305, 205, 375), (45, 45, 50))
        ellipse((315, 305, 385, 375), (45, 45, 50))
        ellipse((155, 325, 185, 355), (210, 210, 210), width=3)
        ellipse((335, 325, 365, 355), (210, 210, 210), width=3)

    elif kind == "airplane":
        polygon(
            [
                (250, 95), (285, 220), (400, 290), (395, 320),
                (280, 285), (280, 375), (330, 410), (330, 430),
                (250, 405), (170, 430), (170, 410), (220, 375),
                (220, 285), (105, 320), (100, 290), (215, 220),
            ],
            (205, 215, 225),
        )

    elif kind == "bicycle":
        ellipse((95, 280, 215, 400), None, width=8)
        ellipse((300, 280, 420, 400), None, width=8)
        line([(155, 340), (240, 240), (350, 340), (155, 340)], accent, 9)
        line([(240, 240), (275, 340)], accent, 9)
        line([(250, 235), (290, 235)], width=8)
        line([(150, 335), (140, 310)], width=7)
        line([(335, 340), (360, 240)], width=8)

    elif kind == "ball":
        ellipse((115, 115, 395, 395), (230, 230, 230), width=8)
        polygon(
            [(235, 195), (280, 205), (300, 250), (265, 285), (220, 260)],
            (40, 40, 45),
        )
        line([(235, 195), (185, 155)], width=5)
        line([(280, 205), (350, 180)], width=5)
        line([(300, 250), (365, 280)], width=5)
        line([(265, 285), (260, 355)], width=5)
        line([(220, 260), (155, 300)], width=5)

    elif kind == "tree":
        draw.rectangle(
            box(225, 280, 290, 415),
            fill=(125, 80, 45),
            outline=outline,
            width=5,
        )
        ellipse((125, 125, 280, 300), (65, 145, 80))
        ellipse((225, 100, 375, 285), (50, 125, 70))
        ellipse((175, 180, 340, 330), (75, 160, 85))

    elif kind == "house":
        draw.rectangle(
            box(135, 220, 375, 405),
            fill=(225, 190, 130),
            outline=outline,
            width=7,
        )
        polygon([(110, 225), (255, 100), (400, 225)], (170, 65, 60))
        draw.rectangle(
            box(225, 305, 290, 405),
            fill=(110, 75, 50),
            outline=outline,
            width=5,
        )
        draw.rectangle(
            box(155, 260, 205, 310),
            fill=(120, 190, 220),
            outline=outline,
            width=4,
        )
        draw.rectangle(
            box(310, 260, 355, 310),
            fill=(120, 190, 220),
            outline=outline,
            width=4,
        )

    elif kind == "fish":
        ellipse((120, 180, 365, 335), (75, 160, 205))
        polygon([(360, 255), (425, 195), (425, 315)], (230, 150, 65))
        ellipse((165, 220, 195, 250), (30, 30, 30), width=2)
        line([(220, 205), (250, 255), (220, 305)], (45, 120, 175), 6)

    # تخفيض الدقة ثم تكبير الصورة.
    low_size = random.choice([64, 72, 80, 96, 112])
    image = image.resize((low_size, low_size), Image.Resampling.BILINEAR)
    image = image.resize((size, size), Image.Resampling.BICUBIC)

    if ImageFilter is not None and random.random() < 0.85:
        image = image.filter(
            ImageFilter.GaussianBlur(random.uniform(1.0, 3.5))
        )

    if ImageEnhance is not None:
        image = ImageEnhance.Contrast(image).enhance(random.uniform(0.55, 0.9))
        image = ImageEnhance.Color(image).enhance(random.uniform(0.45, 0.9))
        image = ImageEnhance.Brightness(image).enhance(random.uniform(0.85, 1.12))

    # خربشات عشوائية مع الحفاظ على ظهور الشكل بشكل عام.
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    scribble = ImageDraw.Draw(overlay)

    for _ in range(random.randint(35, 75)):
        x1 = random.randint(-40, size)
        y1 = random.randint(-40, size)
        x2 = x1 + random.randint(-160, 160)
        y2 = y1 + random.randint(-160, 160)

        color = random.choice([
            (*accent, random.randint(25, 95)),
            (*second_accent, random.randint(25, 90)),
            (30, 35, 45, random.randint(20, 75)),
        ])

        scribble.line(
            (x1, y1, x2, y2),
            fill=color,
            width=random.randint(1, 5),
        )

    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")

    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return discord.File(output, filename="game_drawing.png")


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
        ready_round = view.action_ready_round.get(action, 1)

        if view.round_number < ready_round:
            remaining = ready_round - view.round_number
            await interaction.response.send_message(
                f"⏳ هذا الخيار في فترة انتظار. يمكن استخدامه بعد {remaining} جولة.",
                ephemeral=True,
            )
            return

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

        if action == "random":
            target = random.choice(candidates)
            view.chosen_action = "random"
            view.target = target
            view.action_ready_round["random"] = view.round_number + 3

            await interaction.response.send_message(
                f"🎲 تم اختيار {target.display_name} للإقصاء.",
                ephemeral=True,
            )
            view.stop()
            return

        if action == "choose":
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
    def __init__(self, wheel_view, candidates, page=0):
        self.wheel_view = wheel_view
        self.candidates = candidates
        self.page = page

        start = page * 25
        page_candidates = candidates[start:start + 25]

        options = [
            discord.SelectOption(
                label=player.display_name[:100],
                value=str(player.id),
                description=f"اختيار {player.display_name}"[:100],
            )
            for player in page_candidates
        ]

        super().__init__(
            placeholder=f"اختر لاعبًا (صفحة {page + 1})",
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
            (player for player in view.players if player.id == target_id),
            None,
        )

        if target is None or target.id == view.selected_player.id:
            await interaction.response.send_message(
                "❌ اختيار غير صالح.",
                ephemeral=True,
            )
            return

        self.view.target = target
        await interaction.response.send_message(
            f"✅ اخترت {target.display_name}.",
            ephemeral=True,
        )
        self.view.stop()


class WheelTargetView(discord.ui.View):
    def __init__(self, wheel_view, candidates):
        super().__init__(timeout=45)
        self.target = None
        self.wheel_view = wheel_view
        self.candidates = candidates
        self.page = 0
        self.max_pages = max(1, (len(candidates) + 24) // 25)
        self._refresh_items()

    def _refresh_items(self):
        self.clear_items()
        self.add_item(
            WheelTargetSelect(
                self.wheel_view,
                self.candidates,
                self.page,
            )
        )

        if self.max_pages > 1:
            previous_button = discord.ui.Button(
                label="السابق",
                style=discord.ButtonStyle.secondary,
                disabled=self.page == 0,
            )
            next_button = discord.ui.Button(
                label="التالي",
                style=discord.ButtonStyle.secondary,
                disabled=self.page >= self.max_pages - 1,
            )

            async def previous_callback(interaction: discord.Interaction):
                if interaction.user.id != self.wheel_view.selected_player.id:
                    await interaction.response.send_message(
                        "هذه القائمة للاعب الذي اختارته العجلة فقط.",
                        ephemeral=True,
                    )
                    return

                self.page -= 1
                self._refresh_items()
                await interaction.response.edit_message(view=self)

            async def next_callback(interaction: discord.Interaction):
                if interaction.user.id != self.wheel_view.selected_player.id:
                    await interaction.response.send_message(
                        "هذه القائمة للاعب الذي اختارته العجلة فقط.",
                        ephemeral=True,
                    )
                    return

                self.page += 1
                self._refresh_items()
                await interaction.response.edit_message(view=self)

            previous_button.callback = previous_callback
            next_button.callback = next_callback
            self.add_item(previous_button)
            self.add_item(next_button)


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
        self.used_items = {}
        self.listener_added = False
        self.commands_added = False
        self.slash_added = False

    # ========================================================
    # NON-REPEATING ITEM PICKER
    # ========================================================

    def pick_nonrepeating(self, channel, key, items):
        guild = getattr(channel, "guild", None)
        pool_key = (
            guild.id if guild else 0,
            channel.id,
            key,
        )

        used = self.used_items.setdefault(pool_key, set())
        available = [
            item for item in items
            if self._item_key(item) not in used
        ]

        if not available:
            used.clear()
            available = list(items)

        selected = random.choice(available)
        used.add(self._item_key(selected))
        return selected

    @staticmethod
    def _item_key(item):
        if isinstance(item, dict):
            return str(item.get("answer", item))
        if isinstance(item, tuple):
            return str(item[0])
        return str(item)

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

        cooldown_key = (guild.id, member.id, channel.id, game_key)
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

        if not self.can_use_games(ctx.guild.id, ctx.channel.id, ctx.author):
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
        state["task"] = asyncio.create_task(self._run_game(ctx, game_key))

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

        if not self.can_use_games(ctx.guild.id, ctx.channel.id, ctx.author):
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
