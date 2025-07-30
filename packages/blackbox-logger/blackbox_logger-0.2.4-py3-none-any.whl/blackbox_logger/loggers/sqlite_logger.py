# blackbox_logger/loggers/sqlite_logger.py

import os
import json
from datetime import datetime

DB_TYPE = os.getenv("BLACKBOX_DB_TYPE", "sqlite")

if DB_TYPE == "postgres":
    import psycopg2
    from psycopg2.extras import Json

    class SQLiteLogger:
        def __init__(self):
            self.conn = psycopg2.connect(
                dbname=os.getenv("BLACKBOX_PG_DB", "blackbox_logs"),
                user=os.getenv("BLACKBOX_PG_USER", "postgres"),
                password=os.getenv("BLACKBOX_PG_PASSWORD", "postgres"),
                host=os.getenv("BLACKBOX_PG_HOST", "localhost"),
                port=os.getenv("BLACKBOX_PG_PORT", "5432")
            )
            self._create_table()

        def _create_table(self):
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS logs (
                        id SERIAL PRIMARY KEY,
                        type TEXT,
                        method TEXT,
                        path TEXT,
                        user TEXT,
                        ip TEXT,
                        user_agent TEXT,
                        payload JSONB,
                        status_code INTEGER,
                        timestamp TIMESTAMPTZ
                    )
                """)
                self.conn.commit()

        def log(self, log_type, method, path, user, ip, user_agent, payload, status_code=None):
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO logs (type, method, path, user, ip, user_agent, payload, status_code, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    log_type,
                    method,
                    path,
                    user,
                    ip,
                    user_agent,
                    Json(payload),
                    status_code,
                    datetime.utcnow()
                ))
                self.conn.commit()

else:
    import sqlite3

    class SQLiteLogger:
        def __init__(self):
            db_path = "log/blackbox_logs.db"
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self._create_table()
            self._set_permissions(db_path)

        def _set_permissions(self, db_path):
            try:
                os.chmod(db_path, 0o664)
            except OSError as e:
                print(f"Error setting permissions: {e}")

        def _create_table(self):
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    method TEXT,
                    path TEXT,
                    user TEXT,
                    ip TEXT,
                    user_agent TEXT,
                    payload TEXT,
                    status_code INTEGER,
                    timestamp TEXT
                )
            """)
            self.conn.commit()

        def log(self, log_type, method, path, user, ip, user_agent, payload, status_code=None):
            self.conn.execute("""
                INSERT INTO logs (type, method, path, user, ip, user_agent, payload, status_code, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_type,
                method,
                path,
                user,
                ip,
                user_agent,
                json.dumps(payload),
                status_code,
                datetime.utcnow().isoformat()
            ))
            self.conn.commit()