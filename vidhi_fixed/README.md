# Vidhi Legal AI

A desktop legal case management application built with [Flet](https://flet.dev), designed to serve both **advocates** (lawyers) and **clients** through separate, role-specific views.

## Features

- **Dual dashboards** — separate advocate and client-facing views tailored to each role's needs
- **Case management** — track active cases, pending service requests, and upcoming hearings
- **Document management** — upload, organize, and retrieve case documents by folder/category, with collision-safe file naming
- **Billing & payments** — track fees, payments, and deadlines per case
- **Multi-language support** — full Telugu translation alongside English (180+ translated strings across the app)
- **Light/dark theme support** with theme-aware styling throughout
- **Local calendar view** for hearings and deadlines

## Tech Stack

- **Python 3** with **[Flet](https://flet.dev)** (0.85.3) for the desktop UI
- **SQLite** for local data storage
- Standard library only otherwise (`hashlib`, `sqlite3`, `shutil`, etc.) — no other external dependencies

## Project Structure

```
vidhi_fixed/
├── main.py              # App entry point, view routing
├── i18n.py               # Internationalization (English/Telugu strings)
├── components/           # Reusable UI components (cards, navbar, sidebar, tables, charts)
├── services/
│   ├── db.py             # Database schema, queries, user auth
│   └── case_data.py       # Case-related data helpers
├── views/                # One file per screen (dashboard, cases, billing, documents, etc.)
└── assets/                # Logo and background images
```

## Getting Started

### Prerequisites
- Python 3.10+

### Setup

```bash
# Clone the repo
git clone <your-repo-url>
cd vidhi_fixed

# (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

The SQLite database (`vidhi_users.db`) is created automatically on first run via `init_db()` — no manual setup required. It is intentionally **not** committed to the repository (see `.gitignore`).

## Security Notes

- User passwords are hashed (SHA-256) before being stored or compared — see `services/db.py`. For a production deployment, a stronger algorithm with per-user salting (e.g., `bcrypt` or `argon2`) is recommended; this was a deliberate minimal upgrade from an earlier plaintext-password implementation.
- No API keys or secrets are required to run this project locally.

## Notes on Recent Work

- Implemented real file upload for case documents, including database schema updates and collision-safe file naming
- Added full Telugu-language translation via `i18n.py`
- Fixed dark mode rendering across all views by replacing hardcoded colors with theme-aware variables
- Resolved Flet version incompatibilities; stabilized on Flet `0.85.3`

## License

Add a license of your choice (e.g., MIT) if you intend to make this repository public.
