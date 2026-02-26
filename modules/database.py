import sqlite3, json, hashlib, os
from datetime import datetime, timedelta
from contextlib import contextmanager

# Ruta donde se guardará el archivo físico de la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'korhex.db')
CACHE_TTL_HOURS = 24

@contextmanager
def get_connection():
    """Manejador thread-safe con WAL mode para lecturas concurrentes."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA foreign_keys=ON')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize_database():
    """Crea todas las tablas al primer arranque. Idempotente."""
    with get_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS account_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_key TEXT UNIQUE NOT NULL,
            company_name TEXT NOT NULL,
            company_url TEXT, industry TEXT,
            raw_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            hit_count INTEGER DEFAULT 0)''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS analysis_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_key TEXT NOT NULL,
            years_inactive INTEGER NOT NULL,
            research TEXT, sales_speech TEXT,
            word_count INTEGER,
            audit_passed INTEGER DEFAULT 0,
            audit_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (company_key, years_inactive))''')
            
        conn.execute('''CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            company_name TEXT,
            tokens_used INTEGER DEFAULT 0,
            cloud_cost_usd REAL DEFAULT 0.0,
            bytes_to_cloud INTEGER DEFAULT 0,
            processing_ms INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
        conn.execute('''CREATE TABLE IF NOT EXISTS lead_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            company_url TEXT, industry TEXT,
            lead_score INTEGER, priority TEXT,
            years_inactive INTEGER,
            is_net_new INTEGER DEFAULT 0,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
        conn.execute('CREATE INDEX IF NOT EXISTS idx_key ON account_cache (company_key)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_score ON lead_scores (lead_score DESC)')

def make_company_key(name: str, url: str) -> str:
    normalized = f'{name.lower().strip()}:{url.lower().strip()}'
    return hashlib.md5(normalized.encode()).hexdigest()

def get_cached_account(name: str, url: str) -> dict | None:
    key = make_company_key(name, url)
    with get_connection() as conn:
        row = conn.execute('''SELECT raw_data FROM account_cache 
                              WHERE company_key=? AND expires_at>CURRENT_TIMESTAMP''', (key,)).fetchone()
        if row:
            conn.execute('UPDATE account_cache SET hit_count=hit_count+1 WHERE company_key=?', (key,))
            return json.loads(row['raw_data'])
    return None

def save_account_cache(name: str, url: str, industry: str, data: dict):
    key = make_company_key(name, url)
    expires = datetime.now() + timedelta(hours=CACHE_TTL_HOURS)
    with get_connection() as conn:
        conn.execute('''INSERT INTO account_cache 
                        (company_key,company_name,company_url,industry,raw_data,expires_at) 
                        VALUES (?,?,?,?,?,?) 
                        ON CONFLICT (company_key) DO UPDATE SET 
                        raw_data=excluded.raw_data, expires_at=excluded.expires_at, hit_count=0''',
                     (key, name, url, industry, json.dumps(data), expires))

def save_analysis(name, url, years, research, speech, wc, passed, notes):
    key = make_company_key(name, url)
    with get_connection() as conn:
        conn.execute('''INSERT INTO analysis_cache 
                        (company_key, years_inactive, research, sales_speech, word_count, audit_passed, audit_notes) 
                        VALUES (?,?,?,?,?,?,?) 
                        ON CONFLICT (company_key,years_inactive) DO UPDATE SET 
                        research=excluded.research, sales_speech=excluded.sales_speech, 
                        word_count=excluded.word_count, audit_passed=excluded.audit_passed, 
                        audit_notes=excluded.audit_notes''',
                     (key, years, research, speech, wc, int(passed), notes))

def get_cached_analysis(name, url, years) -> dict | None:
    key = make_company_key(name, url)
    with get_connection() as conn:
        row = conn.execute('''SELECT research, sales_speech, word_count, audit_passed, audit_notes 
                              FROM analysis_cache WHERE company_key=? AND years_inactive=?''', (key, years)).fetchone()
    return dict(row) if row else None

def save_lead_score(name, url, industry, score, priority, years, is_net_new):
    with get_connection() as conn:
        conn.execute('''INSERT INTO lead_scores 
                        (company_name,company_url,industry,lead_score,priority,years_inactive,is_net_new) 
                        VALUES (?,?,?,?,?,?,?)''', 
                     (name, url, industry, score, priority, years, int(is_net_new)))

def get_top5() -> list:
    with get_connection() as conn:
        rows = conn.execute('''SELECT company_name,company_url,industry, 
                               MAX(lead_score) as lead_score,priority, years_inactive,is_net_new 
                               FROM lead_scores GROUP BY company_name 
                               ORDER BY lead_score DESC LIMIT 5''').fetchall()
    return [dict(r) for r in rows]

def log_audit_event(event_type, company_name='', tokens=0, processing_ms=0):
    cost = tokens * 0.00003
    with get_connection() as conn:
        conn.execute('''INSERT INTO audit_log 
                        (event_type,company_name,tokens_used,cloud_cost_usd,bytes_to_cloud,processing_ms) 
                        VALUES (?,?,?,?,0,?)''', 
                     (event_type, company_name, tokens, cost, processing_ms))

def get_audit_summary() -> dict:
    with get_connection() as conn:
        row = conn.execute('''SELECT COUNT(*) as total_analyses, 
                              SUM(tokens_used) as total_tokens, 
                              SUM(cloud_cost_usd) as total_cost_saved, 
                              SUM(bytes_to_cloud) as bytes_to_cloud, 
                              MIN(timestamp) as first_use FROM audit_log''').fetchone()
    return dict(row) if row else {}


def purge_company_data(company_name: str) -> None:
    """
    Elimina permanentemente los datos locales de una empresa específica.
    - Borra filas en account_cache y lead_scores con ese company_name.
    - Mantiene el audit_log pero sobrescribe company_name con 'REDACTED'
      para cumplir con privacidad sin perder el historial financiero.
    """
    if not company_name:
        return

    with get_connection() as conn:
        # Borrar caché de cuenta y scores asociados a esa empresa
        conn.execute(
            'DELETE FROM account_cache WHERE company_name = ?',
            (company_name,),
        )
        conn.execute(
            'DELETE FROM lead_scores WHERE company_name = ?',
            (company_name,),
        )

        # Conservar el historial del audit log pero anonimizando el nombre
        conn.execute(
            "UPDATE audit_log SET company_name = 'REDACTED' WHERE company_name = ?",
            (company_name,),
        )