"""
Database layer — SQLite (free, no server needed)
Stores: businesses, contacts, campaigns, call logs
"""

import sqlite3
import os
import json
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "voiceai.db")


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create all tables. Run once on startup."""
    with get_db_session() as conn:
        conn.executescript("""
            -- SME Business accounts (tenants)
            CREATE TABLE IF NOT EXISTS businesses (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                industry TEXT NOT NULL DEFAULT 'general',
                owner_name TEXT NOT NULL,
                owner_phone TEXT NOT NULL,
                owner_email TEXT DEFAULT '',
                language TEXT NOT NULL DEFAULT 'hi',
                agent_prompt TEXT DEFAULT '',
                plan TEXT NOT NULL DEFAULT 'starter',
                monthly_minutes_limit INTEGER DEFAULT 500,
                minutes_used INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            -- Customer contacts for each business
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                business_id TEXT NOT NULL,
                name TEXT DEFAULT '',
                phone TEXT NOT NULL,
                email TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                dnd_status INTEGER DEFAULT 0,
                opted_out INTEGER DEFAULT 0,
                consent_given INTEGER DEFAULT 0,
                consent_timestamp TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (business_id) REFERENCES businesses(id)
            );

            -- Outbound call campaigns
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                business_id TEXT NOT NULL,
                name TEXT NOT NULL,
                call_type TEXT NOT NULL DEFAULT 'service',
                status TEXT NOT NULL DEFAULT 'draft',
                script_template TEXT DEFAULT '',
                language TEXT DEFAULT 'hi',
                scheduled_date TEXT DEFAULT '',
                scheduled_time_start TEXT DEFAULT '10:30',
                scheduled_time_end TEXT DEFAULT '18:30',
                total_contacts INTEGER DEFAULT 0,
                calls_made INTEGER DEFAULT 0,
                calls_answered INTEGER DEFAULT 0,
                calls_converted INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (business_id) REFERENCES businesses(id)
            );

            -- Call logs (TRAI audit trail)
            CREATE TABLE IF NOT EXISTS call_logs (
                id TEXT PRIMARY KEY,
                business_id TEXT NOT NULL,
                campaign_id TEXT DEFAULT '',
                contact_phone TEXT NOT NULL,
                call_type TEXT NOT NULL DEFAULT 'service',
                direction TEXT NOT NULL DEFAULT 'outbound',
                started_at TEXT DEFAULT (datetime('now')),
                duration_seconds INTEGER DEFAULT 0,
                outcome TEXT DEFAULT 'pending',
                ai_disclosed INTEGER DEFAULT 1,
                opt_out_offered INTEGER DEFAULT 1,
                opt_out_requested INTEGER DEFAULT 0,
                consent_verified INTEGER DEFAULT 0,
                language TEXT DEFAULT 'hi',
                transcript TEXT DEFAULT '',
                sentiment TEXT DEFAULT '',
                lead_score INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                FOREIGN KEY (business_id) REFERENCES businesses(id)
            );

            -- Analytics aggregates (updated periodically)
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id TEXT NOT NULL,
                date TEXT NOT NULL,
                total_calls INTEGER DEFAULT 0,
                calls_answered INTEGER DEFAULT 0,
                calls_missed INTEGER DEFAULT 0,
                calls_opted_out INTEGER DEFAULT 0,
                avg_duration_seconds REAL DEFAULT 0,
                leads_qualified INTEGER DEFAULT 0,
                total_minutes_used REAL DEFAULT 0,
                UNIQUE(business_id, date),
                FOREIGN KEY (business_id) REFERENCES businesses(id)
            );
        """)
    print("Database initialized at:", DB_PATH)


# ===== BUSINESS CRUD =====

def create_business(
    name: str,
    industry: str,
    owner_name: str,
    owner_phone: str,
    owner_email: str = "",
    language: str = "hi",
    plan: str = "starter",
) -> dict:
    """Register a new SME business."""
    import uuid
    biz_id = f"biz_{uuid.uuid4().hex[:12]}"

    with get_db_session() as conn:
        conn.execute(
            """INSERT INTO businesses 
               (id, name, industry, owner_name, owner_phone, owner_email, language, plan)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (biz_id, name, industry, owner_name, owner_phone, owner_email, language, plan),
        )

    return {
        "id": biz_id,
        "name": name,
        "industry": industry,
        "plan": plan,
        "status": "active",
    }


def get_business(business_id: str) -> dict | None:
    """Get business by ID."""
    with get_db_session() as conn:
        row = conn.execute(
            "SELECT * FROM businesses WHERE id = ?", (business_id,)
        ).fetchone()
        return dict(row) if row else None


def list_businesses() -> list[dict]:
    """List all businesses."""
    with get_db_session() as conn:
        rows = conn.execute(
            "SELECT id, name, industry, plan, is_active, created_at FROM businesses ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


# ===== CONTACT CRUD =====

def add_contact(
    business_id: str, phone: str, name: str = "", tags: list[str] = None
) -> dict:
    """Add a contact for a business."""
    import uuid
    contact_id = f"con_{uuid.uuid4().hex[:12]}"

    with get_db_session() as conn:
        conn.execute(
            """INSERT INTO contacts (id, business_id, name, phone, tags)
               VALUES (?, ?, ?, ?, ?)""",
            (contact_id, business_id, name, phone, json.dumps(tags or [])),
        )

    return {"id": contact_id, "phone": phone, "name": name}


def get_contacts(business_id: str) -> list[dict]:
    """Get all contacts for a business."""
    with get_db_session() as conn:
        rows = conn.execute(
            "SELECT * FROM contacts WHERE business_id = ? ORDER BY created_at DESC",
            (business_id,),
        ).fetchall()
        return [dict(r) for r in rows]


# ===== CAMPAIGN CRUD =====

def create_campaign(
    business_id: str,
    name: str,
    call_type: str = "service",
    script_template: str = "",
    language: str = "hi",
) -> dict:
    """Create a new outbound campaign."""
    import uuid
    camp_id = f"camp_{uuid.uuid4().hex[:12]}"

    with get_db_session() as conn:
        conn.execute(
            """INSERT INTO campaigns (id, business_id, name, call_type, script_template, language)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (camp_id, business_id, name, call_type, script_template, language),
        )

    return {"id": camp_id, "name": name, "status": "draft"}


def get_campaigns(business_id: str) -> list[dict]:
    """Get all campaigns for a business."""
    with get_db_session() as conn:
        rows = conn.execute(
            "SELECT * FROM campaigns WHERE business_id = ? ORDER BY created_at DESC",
            (business_id,),
        ).fetchall()
        return [dict(r) for r in rows]


# ===== CALL LOG =====

def log_call(
    business_id: str,
    contact_phone: str,
    duration_seconds: int = 0,
    outcome: str = "completed",
    call_type: str = "service",
    direction: str = "inbound",
    transcript: str = "",
    campaign_id: str = "",
) -> dict:
    """Log a call for TRAI audit trail."""
    import uuid
    log_id = f"call_{uuid.uuid4().hex[:12]}"

    with get_db_session() as conn:
        conn.execute(
            """INSERT INTO call_logs 
               (id, business_id, campaign_id, contact_phone, call_type, direction,
                duration_seconds, outcome, transcript)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (log_id, business_id, campaign_id, contact_phone, call_type,
             direction, duration_seconds, outcome, transcript),
        )

    return {"id": log_id, "outcome": outcome}


# ===== ANALYTICS =====

def get_analytics(business_id: str) -> dict:
    """Get call analytics for a business."""
    with get_db_session() as conn:
        stats = conn.execute(
            """SELECT 
                COUNT(*) as total_calls,
                SUM(CASE WHEN outcome = 'completed' THEN 1 ELSE 0 END) as answered,
                SUM(CASE WHEN outcome = 'no_answer' THEN 1 ELSE 0 END) as missed,
                SUM(CASE WHEN opt_out_requested = 1 THEN 1 ELSE 0 END) as opted_out,
                AVG(duration_seconds) as avg_duration,
                SUM(duration_seconds) / 60.0 as total_minutes,
                SUM(CASE WHEN lead_score >= 7 THEN 1 ELSE 0 END) as hot_leads
               FROM call_logs WHERE business_id = ?""",
            (business_id,),
        ).fetchone()

        return {
            "total_calls": stats["total_calls"] or 0,
            "calls_answered": stats["answered"] or 0,
            "calls_missed": stats["missed"] or 0,
            "calls_opted_out": stats["opted_out"] or 0,
            "avg_duration_seconds": round(stats["avg_duration"] or 0, 1),
            "total_minutes_used": round(stats["total_minutes"] or 0, 1),
            "hot_leads": stats["hot_leads"] or 0,
            "answer_rate": f"{((stats['answered'] or 0) / max(stats['total_calls'] or 1, 1) * 100):.1f}%",
        }


# Initialize on import
if not os.path.exists(DB_PATH):
    init_db()