import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "vidhi_users.db"


def _hash_password(password: str) -> str:
    """Hash a password with SHA-256 before storing/comparing.
    Note: for production use, prefer bcrypt/argon2 (with per-user salt)
    over a plain SHA-256 hash. This is a minimal upgrade from storing
    plaintext passwords."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

GENERAL_FEES = {"Family": 500, "Property": 1000, "Criminal": 1500}


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # PAYMENTS — extended with deadline and cash_confirmed_by
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            fee_type TEXT,
            amount REAL,
            payment_status TEXT DEFAULT 'Pending',
            payment_method TEXT,
            payment_date TEXT,
            deadline TEXT,
            cash_confirmed_by TEXT DEFAULT NULL
        )
    """)

    # Migrate existing payments table to add new columns if missing
    try:
        cursor.execute("ALTER TABLE payments ADD COLUMN deadline TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE payments ADD COLUMN cash_confirmed_by TEXT DEFAULT NULL")
    except Exception:
        pass

    # CASE NOTES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            note TEXT,
            updated_on TEXT
        )
    """)

    # USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # CASES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            case_id TEXT,
            client_name TEXT,
            advocate_name TEXT,
            court TEXT,
            status TEXT,
            case_type TEXT,
            description TEXT,
            urgency TEXT
        )
    """)
    # Migrate existing cases table
    for col in ["case_type TEXT", "description TEXT", "urgency TEXT"]:
        try:
            cursor.execute(f"ALTER TABLE cases ADD COLUMN {col}")
        except Exception:
            pass

    # HEARINGS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hearings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            hearing_date TEXT,
            court TEXT,
            judge_name TEXT,
            advocate_name TEXT
        )
    """)
    # Migrate old schema
    try:
        cursor.execute("ALTER TABLE hearings ADD COLUMN judge_name TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE hearings ADD COLUMN advocate_name TEXT")
    except Exception:
        pass

    # DOCUMENTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT,
            subject TEXT,
            filename TEXT,
            uploaded_by TEXT,
            uploaded_on TEXT
        )
    """)

    conn.commit()
    conn.close()

    # initialise document folder table
    init_doc_folders_table()


# --------------------------------------------------
# USERS
# --------------------------------------------------

def create_user(contact, username, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users(contact, username, password) VALUES(?,?,?)",
            (contact, username, _hash_password(password))
        )
        conn.commit()
        conn.close()
        return True, "Account created successfully"
    except Exception as e:
        return False, str(e)


def validate_user(contact, username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE contact=? AND username=? AND password=?",
        (contact, username, _hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    return user


def get_usernames(contact):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE contact=?", (contact,))
    users = cursor.fetchall()
    conn.close()
    return [u[0] for u in users]


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, contact, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


# --------------------------------------------------
# CASES
# --------------------------------------------------

def create_case(username, case_id, client_name, advocate_name, court, status,
               case_type="", description="", urgency=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO cases(username,case_id,client_name,advocate_name,court,status,
                             case_type,description,urgency)
           VALUES(?,?,?,?,?,?,?,?,?)""",
        (username, case_id, client_name, advocate_name, court, status,
         case_type, description, urgency)
    )
    conn.commit()
    conn.close()


def get_cases_by_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT case_id,client_name,advocate_name,status FROM cases WHERE username=? ORDER BY id DESC",
        (username,)
    )
    cases = cursor.fetchall()
    conn.close()
    return cases


def get_active_cases_by_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT case_id,advocate_name FROM cases WHERE username=? AND status='Active' ORDER BY id DESC",
        (username,)
    )
    cases = cursor.fetchall()
    conn.close()
    return cases


def get_all_cases():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases ORDER BY id DESC")
    cases = cursor.fetchall()
    conn.close()
    return cases


def get_case_by_id(case_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id,username,case_id,client_name,advocate_name,court,status,
                  case_type,description,urgency
           FROM cases WHERE case_id=?""",
        (case_id,)
    )
    case = cursor.fetchone()
    conn.close()
    return case


def approve_case(case_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE cases SET status='Active' WHERE case_id=?", (case_id,))
    conn.commit()
    conn.close()


def reject_case(case_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE cases SET status='Rejected' WHERE case_id=?", (case_id,))
    conn.commit()
    conn.close()


def delete_case_by_id(case_id, username):
    conn = get_connection()
    cursor = conn.cursor()
    # Only allow deletion if case belongs to user and is still Pending
    cursor.execute("DELETE FROM payments  WHERE case_id=?", (case_id,))
    cursor.execute("DELETE FROM hearings  WHERE case_id=?", (case_id,))
    cursor.execute("DELETE FROM cases     WHERE case_id=? AND username=?", (case_id, username))
    conn.commit()
    conn.close()


# --------------------------------------------------
# HEARINGS
# --------------------------------------------------

def _normalise_date(raw: str) -> str:
    """Try to parse any common date format and return DD-MM-YYYY.
    Falls back to the original string if nothing matches."""
    from datetime import datetime
    FORMATS = [
        "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d",
        "%d %b %Y", "%d %B %Y",
        "%d-%m-%y", "%d/%m/%y",
    ]
    raw = raw.strip()
    for fmt in FORMATS:
        try:
            return datetime.strptime(raw, fmt).strftime("%d-%m-%Y")
        except ValueError:
            continue
    return raw   # return as-is if we can't parse


def create_hearing(case_id, hearing_date, court, judge_name, advocate_name):
    normalised = _normalise_date(hearing_date)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO hearings(case_id,hearing_date,court,judge_name,advocate_name) VALUES(?,?,?,?,?)",
        (case_id, normalised, court, judge_name, advocate_name)
    )
    conn.commit()
    conn.close()


def get_hearings(case_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, case_id, hearing_date, court, judge_name, advocate_name
           FROM hearings WHERE case_id=? ORDER BY id DESC""",
        (case_id,)
    )
    hearings = cursor.fetchall()
    conn.close()
    return hearings


def get_hearings_by_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT h.case_id,h.hearing_date,h.court,h.judge_name,h.advocate_name
           FROM hearings h JOIN cases c ON h.case_id=c.case_id
           WHERE c.username=? ORDER BY h.id DESC""",
        (username,)
    )
    hearings = cursor.fetchall()
    conn.close()
    return hearings


# --------------------------------------------------
# DOCUMENTS
# --------------------------------------------------

def add_document(case_id, subject, filename, uploaded_by, uploaded_on):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents(case_id,subject,filename,uploaded_by,uploaded_on) VALUES(?,?,?,?,?)",
        (case_id, subject, filename, uploaded_by, uploaded_on)
    )
    conn.commit()
    conn.close()


def get_documents(case_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE case_id=? ORDER BY id DESC", (case_id,))
    docs = cursor.fetchall()
    conn.close()
    return docs


def get_all_documents():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents ORDER BY id DESC")
    docs = cursor.fetchall()
    conn.close()
    return docs


# --------------------------------------------------
# PAYMENTS
# --------------------------------------------------

def add_payment(case_id, fee_type, amount, payment_status, payment_method, payment_date, deadline=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO payments(case_id,fee_type,amount,payment_status,payment_method,payment_date,deadline)
           VALUES(?,?,?,?,?,?,?)""",
        (case_id, fee_type, amount, payment_status, payment_method, payment_date, deadline)
    )
    conn.commit()
    conn.close()


def get_payments_by_case(case_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments WHERE case_id=? ORDER BY id DESC", (case_id,))
    payments = cursor.fetchall()
    conn.close()
    return payments


def get_all_payments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments ORDER BY id DESC")
    payments = cursor.fetchall()
    conn.close()
    return payments


def get_payments_by_user(username):
    """Returns: (id, case_id, fee_type, amount, status, method, date, deadline, cash_confirmed_by)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT p.id, p.case_id, p.fee_type, p.amount, p.payment_status,
                  p.payment_method, p.payment_date, p.deadline, p.cash_confirmed_by
           FROM payments p
           JOIN cases c ON p.case_id = c.case_id
           WHERE c.username=?
           ORDER BY p.id DESC""",
        (username,)
    )
    payments = cursor.fetchall()
    conn.close()
    return payments


def update_payment_deadline(payment_id, deadline):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE payments SET deadline=? WHERE id=?", (deadline, payment_id))
    conn.commit()
    conn.close()


def update_payment_status(payment_id, new_status, method=None, confirmed_by=None):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%d %b %Y")
    if method:
        cursor.execute(
            """UPDATE payments SET payment_status=?, payment_method=?,
               payment_date=?, cash_confirmed_by=? WHERE id=?""",
            (new_status, method, today, confirmed_by, payment_id)
        )
    else:
        cursor.execute(
            "UPDATE payments SET payment_status=?, cash_confirmed_by=? WHERE id=?",
            (new_status, confirmed_by, payment_id)
        )
    conn.commit()
    conn.close()


def get_pending_cash_payments():
    """Returns payments where method=Cash and status=Pending Confirmation"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT p.id, p.case_id, p.fee_type, p.amount, p.payment_method,
                  p.payment_date, p.deadline, c.username
           FROM payments p
           JOIN cases c ON p.case_id = c.case_id
           WHERE p.payment_method='Cash' AND p.payment_status='Pending Confirmation'
           ORDER BY p.id DESC"""
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# --------------------------------------------------
# DOCUMENT FOLDERS  (Merkle-tree backed)
# --------------------------------------------------

import hashlib
import json
import os
import shutil


ALLOWED_EXTENSIONS = {
    ".pdf", ".txt", ".doc", ".docx", ".xls", ".xlsx",
    ".ppt", ".pptx", ".jpg", ".jpeg", ".png", ".gif",
    ".bmp", ".tiff", ".mp4", ".avi", ".mov", ".mp3",
    ".wav", ".zip", ".rar", ".csv", ".odt", ".rtf"
}

FOLDER_CATEGORIES = [
    "Pleadings",
    "Evidence & Exhibits",
    "Legal Notices",
    "Court Orders",
    "Judgments & Reports",
]

DOCS_ROOT = "client_docs"


def _ensure_folder(path):
    os.makedirs(path, exist_ok=True)


def get_case_folder_root(username, case_id):
    """Returns: client_docs/<username>/<case_id>/"""
    path = os.path.join(DOCS_ROOT, username, case_id)
    _ensure_folder(path)
    return path


def get_category_path(username, case_id, category):
    root = get_case_folder_root(username, case_id)
    path = os.path.join(root, category)
    _ensure_folder(path)
    return path


# ---------- Merkle Tree ----------

def _file_hash(filepath):
    """SHA-256 of a file's content."""
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except FileNotFoundError:
        return hashlib.sha256(b"").hexdigest()
    return h.hexdigest()


def _build_merkle_tree(hashes):
    """Build a Merkle tree from a list of hex-digest strings.
    Returns (root_hash, tree_levels).
    tree_levels[0] = leaf hashes, tree_levels[-1] = [root]."""
    if not hashes:
        return hashlib.sha256(b"").hexdigest(), [[]]
    nodes = list(hashes)
    levels = [nodes[:]]
    while len(nodes) > 1:
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1])  # duplicate last for odd count
        next_level = []
        for i in range(0, len(nodes), 2):
            combined = nodes[i] + nodes[i + 1]
            next_level.append(hashlib.sha256(combined.encode()).hexdigest())
        nodes = next_level
        levels.append(nodes[:])
    return nodes[0], levels


def compute_merkle_root(username, case_id, category):
    """Compute Merkle root for all files in a category folder."""
    path = get_category_path(username, case_id, category)
    files = sorted(
        f for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and not f.endswith(".merkle.json")
    )
    hashes = [_file_hash(os.path.join(path, f)) for f in files]
    root, levels = _build_merkle_tree(hashes)
    tree_data = {
        "files": files,
        "hashes": hashes,
        "levels": levels,
        "root": root,
    }
    meta_path = os.path.join(path, ".merkle.json")
    with open(meta_path, "w") as fp:
        json.dump(tree_data, fp, indent=2)
    return root, tree_data


def get_merkle_root(username, case_id, category):
    """Read cached Merkle root or recompute."""
    path = get_category_path(username, case_id, category)
    meta_path = os.path.join(path, ".merkle.json")
    if os.path.exists(meta_path):
        with open(meta_path) as fp:
            data = json.load(fp)
        return data.get("root", ""), data
    return compute_merkle_root(username, case_id, category)


# ---------- Document DB helpers ----------

def init_doc_folders_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doc_files (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT,
            case_id     TEXT,
            category    TEXT,
            orig_name   TEXT,
            stored_name TEXT,
            file_hash   TEXT,
            uploaded_on TEXT,
            size_bytes  INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def save_uploaded_file(username, case_id, category, file_bytes, orig_name, uploaded_on):
    """Save bytes to disk, update DB, recompute Merkle tree."""
    ext = os.path.splitext(orig_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type '{ext}' not allowed."

    dest_dir = get_category_path(username, case_id, category)
    # De-duplicate stored name
    stored_name = orig_name
    counter = 1
    while os.path.exists(os.path.join(dest_dir, stored_name)):
        name_no_ext = os.path.splitext(orig_name)[0]
        stored_name = f"{name_no_ext}_{counter}{ext}"
        counter += 1

    full_path = os.path.join(dest_dir, stored_name)
    with open(full_path, "wb") as f:
        f.write(file_bytes)

    file_hash = _file_hash(full_path)
    size = len(file_bytes)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO doc_files(username,case_id,category,orig_name,stored_name,
                                  file_hash,uploaded_on,size_bytes)
           VALUES(?,?,?,?,?,?,?,?)""",
        (username, case_id, category, orig_name, stored_name,
         file_hash, uploaded_on, size)
    )
    conn.commit()
    conn.close()

    compute_merkle_root(username, case_id, category)
    return True, stored_name


def get_files_in_category(username, case_id, category):
    """Returns list of (id, orig_name, stored_name, file_hash, uploaded_on, size_bytes)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, orig_name, stored_name, file_hash, uploaded_on, size_bytes
           FROM doc_files
           WHERE username=? AND case_id=? AND category=?
           ORDER BY id DESC""",
        (username, case_id, category)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_doc_file(doc_id, username, case_id, category):
    """Delete file from disk and DB, recompute Merkle."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT stored_name FROM doc_files WHERE id=? AND username=?",
        (doc_id, username)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    stored_name = row[0]
    dest_dir = get_category_path(username, case_id, category)
    full_path = os.path.join(dest_dir, stored_name)
    if os.path.exists(full_path):
        os.remove(full_path)
    cursor.execute("DELETE FROM doc_files WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()
    compute_merkle_root(username, case_id, category)
    return True


def get_all_doc_files():
    """Returns every uploaded doc_files row across all clients/cases.
    (id, username, case_id, category, orig_name, stored_name,
     file_hash, uploaded_on, size_bytes)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, username, case_id, category, orig_name, stored_name,
                  file_hash, uploaded_on, size_bytes
           FROM doc_files
           ORDER BY id DESC"""
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_cases_for_user(username):
    """Returns list of (case_id, client_name, status) for all cases of a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT case_id, client_name, status FROM cases WHERE username=? ORDER BY id DESC",
        (username,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_case_note(case_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT note, updated_on FROM case_notes WHERE case_id=? ORDER BY id DESC LIMIT 1", (case_id,))
    row = cursor.fetchone()
    conn.close()
    return row  # (note, updated_on) or None


def save_case_note(case_id, note):
    from datetime import datetime
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM case_notes WHERE case_id=?", (case_id,))
    cursor.execute("INSERT INTO case_notes(case_id, note, updated_on) VALUES(?,?,?)", (case_id, note, now))
    conn.commit()
    conn.close()
    return now


def get_all_hearings():
    """Return all hearings from DB for the advocate calendar view."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT h.case_id, h.hearing_date, h.court, h.judge_name, h.advocate_name
           FROM hearings h ORDER BY h.id DESC"""
    )
    hearings = cursor.fetchall()
    conn.close()
    return hearings


def get_hearings_this_week():
    """Return hearings whose hearing_date falls in the current Mon–Sun week.
    Normalises all stored formats. Returns list of
    (case_id, display_date, court, judge_name, advocate_name)."""
    from datetime import datetime, timedelta

    today      = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())   # Monday
    week_end   = week_start + timedelta(days=6)            # Sunday

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT case_id, hearing_date, court, judge_name, advocate_name FROM hearings ORDER BY id DESC"
    )
    all_h = cursor.fetchall()
    conn.close()

    FORMATS = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d %b %Y", "%d %B %Y",
               "%d-%m-%y", "%d/%m/%y"]

    result = []
    for h in all_h:
        raw_date = (h[1] or "").strip()
        parsed   = None
        for fmt in FORMATS:
            try:
                parsed = datetime.strptime(raw_date, fmt).date()
                break
            except ValueError:
                continue
        if parsed and week_start <= parsed <= week_end:
            display = parsed.strftime("%d %b %Y")   # e.g. 27 Jun 2026
            result.append((h[0], display, h[2], h[3], h[4]))

    return result
