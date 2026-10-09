
# ============================================================
# GAME BOT - DATABASE.PY
# Complete Database + Security Logs + Persistent No-Repeat
# Python 3.14+
# ============================================================

import sqlite3
import threading
import random
from datetime import datetime, timezone

# ============================================================
# DATABASE SETTINGS
# ============================================================

DB_FILE = "games.db"


# ============================================================
# DATABASE
# ============================================================

class Database:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self.lock = threading.RLock()

        self.connection = sqlite3.connect(
            self.db_file,
            check_same_thread=False,
            timeout=30
        )

        self.connection.row_factory = sqlite3.Row

        with self.lock:
            self.connection.execute("PRAGMA busy_timeout = 30000")
            self.connection.execute("PRAGMA journal_mode = WAL")

        self._create_tables()

    # ========================================================
    # TIME
    # ========================================================

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()

    # ========================================================
    # CREATE TABLES
    # ========================================================

    def _create_tables(self):
        with self.lock:
            cursor = self.connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_stats (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    points INTEGER NOT NULL DEFAULT 0,
                    wins INTEGER NOT NULL DEFAULT 0,
                    games_played INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    game_name TEXT NOT NULL,
                    winner_id INTEGER,
                    points INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_setups (
                    guild_id INTEGER NOT NULL,
                    slot INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (guild_id, slot)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_settings (
                    guild_id INTEGER PRIMARY KEY,
                    log_channel_id INTEGER,
                    updated_at TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exploit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    game_name TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Persistent no-repeat storage.
            # Each guild, channel and pool has its own cycle.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS used_game_items (
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    pool_key TEXT NOT NULL,
                    item_key TEXT NOT NULL,
                    used_at TEXT NOT NULL,
                    PRIMARY KEY (
                        guild_id,
                        channel_id,
                        pool_key,
                        item_key
                    )
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_exploit_logs_guild
                ON exploit_logs (guild_id, created_at)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_guild
                ON game_history (guild_id, created_at)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_used_items_pool
                ON used_game_items (
                    guild_id,
                    channel_id,
                    pool_key
                )
            """)

            self.connection.commit()

    # ========================================================
    # PERSISTENT NO-REPEAT SYSTEM
    # ========================================================

    def pick_nonrepeating_item(
        self,
        guild_id,
        channel_id,
        pool_key,
        items
    ):
        """
        Select an unused item and save it permanently.

        items must be a list of unique string keys.
        Returns the selected key, or None if the list is empty.

        A new cycle starts only after every available item
        in this pool has been used.
        """

        available = list(dict.fromkeys(
            str(item) for item in items
        ))

        if not available:
            return None

        guild_id = int(guild_id)
        channel_id = int(channel_id)
        pool_key = str(pool_key)

        with self.lock:
            cursor = self.connection.cursor()

            cursor.execute("""
                SELECT item_key
                FROM used_game_items
                WHERE guild_id = ?
                  AND channel_id = ?
                  AND pool_key = ?
            """, (guild_id, channel_id, pool_key))

            used = {
                row["item_key"]
                for row in cursor.fetchall()
            }

            unused = [
                item for item in available
                if item not in used
            ]

            # All available items have been used:
            # start a fresh cycle.
            if not unused:
                cursor.execute("""
                    DELETE FROM used_game_items
                    WHERE guild_id = ?
                      AND channel_id = ?
                      AND pool_key = ?
                """, (guild_id, channel_id, pool_key))

                unused = available

            selected = random.choice(unused)

            cursor.execute("""
                INSERT OR IGNORE INTO used_game_items (
                    guild_id,
                    channel_id,
                    pool_key,
                    item_key,
                    used_at
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                guild_id,
                channel_id,
                pool_key,
                selected,
                self._now()
            ))

            self.connection.commit()

            return selected

    def get_used_game_items(
        self,
        guild_id,
        channel_id,
        pool_key
    ):
        """Return the keys already used in a particular pool."""

        with self.lock:
            rows = self.connection.execute("""
                SELECT item_key
                FROM used_game_items
                WHERE guild_id = ?
                  AND channel_id = ?
                  AND pool_key = ?
                ORDER BY used_at ASC
            """, (
                int(guild_id),
                int(channel_id),
                str(pool_key)
            )).fetchall()

        return [row["item_key"] for row in rows]

    def mark_game_item_used(
        self,
        guild_id,
        channel_id,
        pool_key,
        item_key
    ):
        """Manually mark an item as used."""

        with self.lock:
            self.connection.execute("""
                INSERT OR IGNORE INTO used_game_items (
                    guild_id,
                    channel_id,
                    pool_key,
                    item_key,
                    used_at
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                int(guild_id),
                int(channel_id),
                str(pool_key),
                str(item_key),
                self._now()
            ))

            self.connection.commit()

    def reset_used_game_items(
        self,
        guild_id,
        channel_id=None,
        pool_key=None
    ):
        """
        Reset used items.

        Optional channel_id and pool_key limit the reset.
        If both are omitted, all pools in the guild are reset.
        """

        query = "DELETE FROM used_game_items WHERE guild_id = ?"
        params = [int(guild_id)]

        if channel_id is not None:
            query += " AND channel_id = ?"
            params.append(int(channel_id))

        if pool_key is not None:
            query += " AND pool_key = ?"
            params.append(str(pool_key))

        with self.lock:
            self.connection.execute(query, params)
            self.connection.commit()

    # ========================================================
    # ENSURE PLAYER
    # ========================================================

    def ensure_player(self, guild_id, user_id):
        now = self._now()

        with self.lock:
            self.connection.execute("""
                INSERT OR IGNORE INTO player_stats (
                    guild_id, user_id, points, wins,
                    games_played, created_at, updated_at
                )
                VALUES (?, ?, 0, 0, 0, ?, ?)
            """, (guild_id, user_id, now, now))

            self.connection.commit()

    # ========================================================
    # ADD POINTS
    # ========================================================

    def add_points(self, guild_id, user_id, points):
        self.ensure_player(guild_id, user_id)
        now = self._now()

        with self.lock:
            self.connection.execute("""
                UPDATE player_stats
                SET points = points + ?, updated_at = ?
                WHERE guild_id = ? AND user_id = ?
            """, (
                int(points), now, guild_id, user_id
            ))

            self.connection.commit()

    # ========================================================
    # ADD WIN
    # ========================================================

    def add_win(self, guild_id, user_id, points=10):
        self.ensure_player(guild_id, user_id)
        now = self._now()

        with self.lock:
            self.connection.execute("""
                UPDATE player_stats
                SET points = points + ?,
                    wins = wins + 1,
                    games_played = games_played + 1,
                    updated_at = ?
                WHERE guild_id = ? AND user_id = ?
            """, (
                int(points), now, guild_id, user_id
            ))

            self.connection.commit()

    # ========================================================
    # ADD GAME PLAYED
    # ========================================================

    def add_game_played(self, guild_id, user_id):
        self.ensure_player(guild_id, user_id)
        now = self._now()

        with self.lock:
            self.connection.execute("""
                UPDATE player_stats
                SET games_played = games_played + 1,
                    updated_at = ?
                WHERE guild_id = ? AND user_id = ?
            """, (now, guild_id, user_id))

            self.connection.commit()

    # ========================================================
    # GET PLAYER STATS
    # ========================================================

    def get_stats(self, guild_id, user_id):
        self.ensure_player(guild_id, user_id)

        with self.lock:
            row = self.connection.execute("""
                SELECT guild_id, user_id, points, wins,
                       games_played, created_at, updated_at
                FROM player_stats
                WHERE guild_id = ? AND user_id = ?
            """, (guild_id, user_id)).fetchone()

        return dict(row) if row else None

    # ========================================================
    # GET POINTS
    # ========================================================

    def get_points(self, guild_id, user_id):
        stats = self.get_stats(guild_id, user_id)
        return stats["points"] if stats else 0

    # ========================================================
    # GET WINS
    # ========================================================

    def get_wins(self, guild_id, user_id):
        stats = self.get_stats(guild_id, user_id)
        return stats["wins"] if stats else 0

    # ========================================================
    # GET GAMES PLAYED
    # ========================================================

    def get_games_played(self, guild_id, user_id):
        stats = self.get_stats(guild_id, user_id)
        return stats["games_played"] if stats else 0

    # ========================================================
    # LEVEL
    # ========================================================

    def get_level(self, guild_id, user_id):
        points = self.get_points(guild_id, user_id)
        return max(1, (points // 100) + 1)

    # ========================================================
    # LEADERBOARD
    # ========================================================

    def get_leaderboard(self, guild_id, limit=10):
        limit = max(1, min(int(limit), 100))

        with self.lock:
            rows = self.connection.execute("""
                SELECT user_id, points, wins, games_played
                FROM player_stats
                WHERE guild_id = ?
                ORDER BY points DESC, wins DESC
                LIMIT ?
            """, (guild_id, limit)).fetchall()

        return [dict(row) for row in rows]

    # ========================================================
    # PLAYER RANK
    # ========================================================

    def get_rank(self, guild_id, user_id):
        points = self.get_points(guild_id, user_id)

        with self.lock:
            row = self.connection.execute("""
                SELECT COUNT(*) + 1 AS rank
                FROM player_stats
                WHERE guild_id = ? AND points > ?
            """, (guild_id, points)).fetchone()

        return row["rank"] if row else 1

    # ========================================================
    # GAME HISTORY
    # ========================================================

    def add_game_history(
        self,
        guild_id,
        channel_id,
        game_name,
        winner_id=None,
        points=0
    ):
        with self.lock:
            self.connection.execute("""
                INSERT INTO game_history (
                    guild_id, channel_id, game_name,
                    winner_id, points, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                guild_id,
                channel_id,
                str(game_name),
                winner_id,
                int(points),
                self._now()
            ))

            self.connection.commit()

    def get_game_history(self, guild_id, limit=20):
        limit = max(1, min(int(limit), 100))

        with self.lock:
            rows = self.connection.execute("""
                SELECT *
                FROM game_history
                WHERE guild_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (guild_id, limit)).fetchall()

        return [dict(row) for row in rows]

    # ========================================================
    # SAVE GAME SETUP
    # ========================================================

    def save_setup(self, guild_id, slot, channel_id, role_id):
        now = self._now()

        with self.lock:
            self.connection.execute("""
                INSERT INTO game_setups (
                    guild_id, slot, channel_id, role_id,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (guild_id, slot)
                DO UPDATE SET
                    channel_id = excluded.channel_id,
                    role_id = excluded.role_id,
                    updated_at = excluded.updated_at
            """, (
                guild_id,
                int(slot),
                channel_id,
                role_id,
                now,
                now
            ))

            self.connection.commit()

    # ========================================================
    # GET GAME SETUPS
    # ========================================================

    def get_setups(self, guild_id):
        with self.lock:
            rows = self.connection.execute("""
                SELECT slot, channel_id, role_id
                FROM game_setups
                WHERE guild_id = ?
                ORDER BY slot ASC
            """, (guild_id,)).fetchall()

        return [dict(row) for row in rows]

    # ========================================================
    # GET ONE SETUP
    # ========================================================

    def get_setup(self, guild_id, slot):
        with self.lock:
            row = self.connection.execute("""
                SELECT slot, channel_id, role_id
                FROM game_setups
                WHERE guild_id = ? AND slot = ?
            """, (guild_id, slot)).fetchone()

        return dict(row) if row else None

    # ========================================================
    # DELETE SETUP
    # ========================================================

    def delete_setup(self, guild_id, slot):
        with self.lock:
            self.connection.execute("""
                DELETE FROM game_setups
                WHERE guild_id = ? AND slot = ?
            """, (guild_id, slot))

            self.connection.commit()

    def delete_all_setups(self, guild_id):
        with self.lock:
            self.connection.execute("""
                DELETE FROM game_setups
                WHERE guild_id = ?
            """, (guild_id,))

            self.connection.commit()

    # ========================================================
    # RESET PLAYER
    # ========================================================

    def reset_player(self, guild_id, user_id):
        now = self._now()

        with self.lock:
            self.connection.execute("""
                INSERT INTO player_stats (
                    guild_id, user_id, points, wins,
                    games_played, created_at, updated_at
                )
                VALUES (?, ?, 0, 0, 0, ?, ?)
                ON CONFLICT (guild_id, user_id)
                DO UPDATE SET
                    points = 0,
                    wins = 0,
                    games_played = 0,
                    updated_at = excluded.updated_at
            """, (guild_id, user_id, now, now))

            self.connection.commit()

    # ========================================================
    # SET EXPLOIT LOG CHANNEL
    # ========================================================

    def set_log_channel(self, guild_id, channel_id):
        now = self._now()

        with self.lock:
            self.connection.execute("""
                INSERT INTO security_settings (
                    guild_id, log_channel_id, updated_at
                )
                VALUES (?, ?, ?)
                ON CONFLICT (guild_id)
                DO UPDATE SET
                    log_channel_id = excluded.log_channel_id,
                    updated_at = excluded.updated_at
            """, (guild_id, channel_id, now))

            self.connection.commit()

    # ========================================================
    # GET EXPLOIT LOG CHANNEL
    # ========================================================

    def get_log_channel(self, guild_id):
        with self.lock:
            row = self.connection.execute("""
                SELECT log_channel_id
                FROM security_settings
                WHERE guild_id = ?
            """, (guild_id,)).fetchone()

        return row["log_channel_id"] if row else None

    # ========================================================
    # CLEAR EXPLOIT LOG CHANNEL
    # ========================================================

    def clear_log_channel(self, guild_id):
        with self.lock:
            self.connection.execute("""
                DELETE FROM security_settings
                WHERE guild_id = ?
            """, (guild_id,))

            self.connection.commit()

    # ========================================================
    # ADD EXPLOIT LOG
    # ========================================================

    def add_exploit_log(
        self,
        guild_id,
        user_id,
        channel_id,
        game_name,
        reason
    ):
        with self.lock:
            self.connection.execute("""
                INSERT INTO exploit_logs (
                    guild_id, user_id, channel_id,
                    game_name, reason, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                guild_id,
                user_id,
                channel_id,
                str(game_name),
                str(reason),
                self._now()
            ))

            self.connection.commit()

    # ========================================================
    # GET EXPLOIT LOGS
    # ========================================================

    def get_exploit_logs(self, guild_id, limit=20):
        limit = max(1, min(int(limit), 100))

        with self.lock:
            rows = self.connection.execute("""
                SELECT *
                FROM exploit_logs
                WHERE guild_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (guild_id, limit)).fetchall()

        return [dict(row) for row in rows]

    # ========================================================
    # CLEAR EXPLOIT LOGS
    # ========================================================

    def clear_exploit_logs(self, guild_id):
        with self.lock:
            self.connection.execute("""
                DELETE FROM exploit_logs
                WHERE guild_id = ?
            """, (guild_id,))

            self.connection.commit()

    # ========================================================
    # CLOSE DATABASE
    # ========================================================

    def close(self):
        with self.lock:
            try:
                self.connection.close()
            except sqlite3.Error:
                pass
