import sqlite3
import os
from datetime import datetime, date, timedelta

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "productivity.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            start_timestamp TEXT NOT NULL,
            end_timestamp TEXT,
            start_time_display TEXT NOT NULL,
            end_time_display TEXT,
            duration_seconds INTEGER DEFAULT 0,
            duration_hours REAL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'running'
        )
    """)
    conn.commit()
    conn.close()

def start_session():
    """Starts a new productivity tracking session and logs start time."""
    init_db()
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    start_ts = now.isoformat()
    start_disp = now.strftime("%I:%M:%S %p")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (date, start_timestamp, start_time_display, status)
        VALUES (?, ?, ?, 'running')
    """, (today_str, start_ts, start_disp))
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id, now

def stop_session(session_id):
    """Stops the active session, calculates duration, and saves end time."""
    now = datetime.now()
    end_ts = now.isoformat()
    end_disp = now.strftime("%I:%M:%S %p")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT start_timestamp, start_time_display FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None

    start_dt = datetime.fromisoformat(row["start_timestamp"])
    duration_sec = int((now - start_dt).total_seconds())
    if duration_sec < 0:
        duration_sec = 0
    duration_hrs = round(duration_sec / 3600.0, 2)

    cursor.execute("""
        UPDATE sessions
        SET end_timestamp = ?,
            end_time_display = ?,
            duration_seconds = ?,
            duration_hours = ?,
            status = 'completed'
        WHERE id = ?
    """, (end_ts, end_disp, duration_sec, duration_hrs, session_id))
    conn.commit()
    conn.close()
    return {
        "id": session_id,
        "duration_seconds": duration_sec,
        "duration_hours": duration_hrs,
        "start_time_display": row["start_time_display"],
        "end_time_display": end_disp
    }

def get_active_session():
    """Retrieves any session that is currently running."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE status = 'running' ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_sessions_by_date(target_date_str):
    """Retrieves all sessions on a given date (YYYY-MM-DD)."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM sessions 
        WHERE date = ? AND status = 'completed'
        ORDER BY id DESC
    """, (target_date_str,))
    rows = [dict(r) for r in cursor.fetchall()]
    
    total_sec = sum(r["duration_seconds"] for r in rows)
    total_hours = round(total_sec / 3600.0, 2)
    conn.close()
    return {
        "date": target_date_str,
        "sessions": rows,
        "total_seconds": total_sec,
        "total_hours": total_hours,
        "count": len(rows)
    }

def get_sessions_by_date_range(start_date_str, end_date_str):
    """Retrieves all sessions between start_date and end_date (inclusive)."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM sessions 
        WHERE date >= ? AND date <= ? AND status = 'completed'
        ORDER BY date DESC, id DESC
    """, (start_date_str, end_date_str))
    rows = [dict(r) for r in cursor.fetchall()]
    
    total_sec = sum(r["duration_seconds"] for r in rows)
    total_hours = round(total_sec / 3600.0, 2)
    conn.close()
    return {
        "start_date": start_date_str,
        "end_date": end_date_str,
        "sessions": rows,
        "total_seconds": total_sec,
        "total_hours": total_hours,
        "count": len(rows)
    }

def delete_session(session_id):
    """Deletes a specific session."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()

def format_duration(seconds):
    """Formats seconds into 'Xh Ym Zs' or 'Xh Ym'."""
    hrs = seconds // 3600
    rem = seconds % 3600
    mins = rem // 60
    secs = rem % 60
    if hrs > 0:
        return f"{hrs}h {mins:02d}m {secs:02d}s"
    elif mins > 0:
        return f"{mins}m {secs:02d}s"
    else:
        return f"{secs}s"
