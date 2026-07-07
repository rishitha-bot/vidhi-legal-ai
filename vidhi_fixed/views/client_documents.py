"""
client_documents.py  –  VIDHI Legal AI
Client document manager with per-case folder tree and Merkle-tree integrity.

Folder structure per case:
    Client Documents
    ├── Identity Documents
    ├── Case Documents
    ├── Evidence Files
    ├── Supporting Documents
    └── Complaints & Notices

Flet 0.24 / 0.85.3 compatible.
"""

import os
import flet as ft
from datetime import datetime
from i18n import t

from components.navbar import navbar
from services.db import (
    get_all_cases_for_user,
    get_files_in_category,
    save_uploaded_file,
    delete_doc_file,
    get_merkle_root,
    ALLOWED_EXTENSIONS,
    get_category_path,
)

# Client-side folder categories (separate from advocate categories)
CLIENT_FOLDER_CATEGORIES = [
    "Identity Documents",
    "Case Documents",
    "Evidence Files",
    "Supporting Documents",
    "Complaints & Notices",
]

# ── Theme ──────────────────────────────────────────────────────────────────
_BLUE      = "#4A7FC1"
_DARK      = "#1E293B"
_SLATE     = "#64748B"
_GREEN     = "#4A8C6A"
_RED       = "#EF4444"
_BG        = "#F8FAFC"
_WHITE     = "white"
_BORDER    = "#E2E8F0"
_HOVER_BG  = "#EFF6FF"

_CATEGORY_ICONS = {
    "Identity Documents":    ft.Icons.BADGE,
    "Case Documents":        ft.Icons.GAVEL,
    "Evidence Files":        ft.Icons.FIND_IN_PAGE,
    "Supporting Documents":  ft.Icons.ATTACH_FILE,
    "Complaints & Notices":  ft.Icons.REPORT,
}

_CATEGORY_COLORS = {
    "Identity Documents":    "#7C3AED",
    "Case Documents":        "#1D4ED8",
    "Evidence Files":        "#B45309",
    "Supporting Documents":  "#047857",
    "Complaints & Notices":  "#DC2626",
}


def _fmt_size(b):
    if b < 1024:
        return f"{b} B"
    elif b < 1024 * 1024:
        return f"{b/1024:.1f} KB"
    return f"{b/1024/1024:.1f} MB"


def _ext_icon(filename):
    ext = os.path.splitext(filename)[1].lower()
    mapping = {
        ".pdf":  (ft.Icons.PICTURE_AS_PDF, "#DC2626"),
        ".doc":  (ft.Icons.DESCRIPTION,    "#1D4ED8"),
        ".docx": (ft.Icons.DESCRIPTION,    "#1D4ED8"),
        ".xls":  (ft.Icons.TABLE_CHART,    "#047857"),
        ".xlsx": (ft.Icons.TABLE_CHART,    "#047857"),
        ".ppt":  (ft.Icons.SLIDESHOW,      "#D97706"),
        ".pptx": (ft.Icons.SLIDESHOW,      "#D97706"),
        ".jpg":  (ft.Icons.IMAGE,          "#7C3AED"),
        ".jpeg": (ft.Icons.IMAGE,          "#7C3AED"),
        ".png":  (ft.Icons.IMAGE,          "#7C3AED"),
        ".gif":  (ft.Icons.IMAGE,          "#7C3AED"),
        ".txt":  (ft.Icons.TEXT_SNIPPET,   "#64748B"),
        ".csv":  (ft.Icons.GRID_ON,        "#0EA5E9"),
        ".zip":  (ft.Icons.FOLDER_ZIP,     "#92400E"),
        ".rar":  (ft.Icons.FOLDER_ZIP,     "#92400E"),
    }
    return mapping.get(ext, (ft.Icons.INSERT_DRIVE_FILE, "#64748B"))


# ── Main view ─────────────────────────────────────────────────────────────

def client_documents_view(page=None, load_page=None, user_info=None):

    username = (user_info or {}).get("username", "user")

    # ── state ──
    selected_case    = {"id": None, "label": None}
    selected_cat     = {"name": None}
    upload_pick      = ft.FilePicker()
    pending_category = {"name": None}

    # ── reusable text refs ──
    merkle_text   = ft.Text(t(""), size=10, color=_SLATE,
                            selectable=True, font_family="monospace")
    status_text   = ft.Text(t(""), size=13)
    file_list_col = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    cat_title_ref = ft.Text(t(""), size=17, weight=ft.FontWeight.BOLD, color=_DARK)
    cat_sub_ref   = ft.Text(t(""), size=12, color=_SLATE)
    upload_btn    = ft.ElevatedButton(
        t("Upload File"),
        icon=ft.Icons.UPLOAD_FILE,
        bgcolor=_BLUE, color=_WHITE,
        disabled=True,
    )
    right_panel   = ft.Column(expand=True, spacing=0, visible=False)

    # ── case/folder tree ──
    tree_col      = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO)

    # ─────────────────────────────────────────────
    # helpers
    # ─────────────────────────────────────────────

    def show_status(msg, ok=True):
        status_text.value = msg
        status_text.color = _GREEN if ok else _RED
        page.update()

    def _category_row(case_id, category, selected=False):
        icon, col = _CATEGORY_ICONS[category], _CATEGORY_COLORS[category]
        count = len(get_files_in_category(username, case_id, category))
        badge = ft.Container(
            width=22, height=22,
            bgcolor=col, border_radius=11,
            alignment=ft.Alignment.CENTER,
            content=ft.Text(str(count), size=10, color=_WHITE,
                            weight=ft.FontWeight.BOLD),
        )
        return ft.Container(
            bgcolor=_HOVER_BG if selected else "transparent",
            border_radius=8,
            padding=ft.Padding(left=28, right=10, top=6, bottom=6),
            on_click=lambda e, c=case_id, cat=category: open_category(c, cat),
            content=ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(icon, color=col, size=16),
                    ft.Text(t(category), size=13, color=_DARK, expand=True),
                    badge,
                ]
            )
        )

    def _case_tile(case_id, label, status):
        status_chip = ft.Container(
            padding=ft.Padding(left=6, right=6, top=2, bottom=2),
            border_radius=6,
            bgcolor="#DCFCE7" if status == "Active" else "#FEF9C3",
            content=ft.Text(
                status, size=10,
                color=_GREEN if status == "Active" else "#92400E",
                weight=ft.FontWeight.BOLD
            )
        )
        is_open = selected_case["id"] == case_id

        cats = ft.Column(
            visible=is_open,
            spacing=0,
            controls=[_category_row(case_id, cat,
                                    selected=(is_open and selected_cat["name"] == cat))
                      for cat in CLIENT_FOLDER_CATEGORIES]
        )

        def toggle_case(e, cid=case_id, lbl=label):
            if selected_case["id"] == cid:
                selected_case["id"] = None
                selected_case["label"] = None
                right_panel.visible = False
            else:
                selected_case["id"] = cid
                selected_case["label"] = lbl
                selected_cat["name"] = None
                right_panel.visible = False
            rebuild_tree()

        return ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    bgcolor=_DARK if is_open else "transparent",
                    border_radius=8,
                    padding=ft.Padding(left=10, right=10, top=8, bottom=8),
                    on_click=toggle_case,
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.FOLDER_OPEN if is_open else ft.Icons.FOLDER,
                                color=_BLUE if not is_open else _WHITE,
                                size=18
                            ),
                            ft.Text(
                                f"Case {case_id}",
                                size=13, expand=True,
                                weight=ft.FontWeight.W_600,
                                color=_WHITE if is_open else _DARK
                            ),
                            status_chip if not is_open else
                            ft.Icon(ft.Icons.EXPAND_LESS, color=_WHITE, size=16),
                        ]
                    )
                ),
                cats,
            ]
        )

    def rebuild_tree():
        tree_col.controls.clear()
        cases = get_all_cases_for_user(username)
        if not cases:
            tree_col.controls.append(
                ft.Text(t("No cases found."), color=_SLATE, size=13)
            )
        for (cid, cname, cstatus) in cases:
            label = f"{cname} ({cid})"
            tree_col.controls.append(_case_tile(cid, label, cstatus))
        page.update()

    def open_category(case_id, category):
        selected_case["id"] = case_id
        selected_cat["name"] = category
        upload_btn.disabled = False
        pending_category["name"] = category

        color = _CATEGORY_COLORS[category]
        icon  = _CATEGORY_ICONS[category]

        cat_title_ref.value = t(category)
        cat_sub_ref.value   = f"{t('Case')}: {case_id}"

        root, _ = get_merkle_root(username, case_id, category)
        merkle_text.value = f"{t('Merkle root')}: {root[:20]}…{root[-8:]}"

        load_file_list()
        right_panel.visible = True
        rebuild_tree()

    def load_file_list():
        file_list_col.controls.clear()
        case_id  = selected_case["id"]
        category = selected_cat["name"]
        if not case_id or not category:
            page.update()
            return

        rows = get_files_in_category(username, case_id, category)
        if not rows:
            file_list_col.controls.append(
                ft.Container(
                    padding=30,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.CLOUD_UPLOAD_OUTLINED,
                                    size=48, color="#CBD5E1"),
                            ft.Text(t("No files yet. Upload the first one!"),
                                    color=_SLATE, size=13),
                        ]
                    )
                )
            )
        else:
            for (fid, orig, stored, fhash, uon, sz) in rows:
                icon, icol = _ext_icon(orig)
                cat_path   = get_category_path(username, case_id, category)
                full_path  = os.path.join(cat_path, stored)

                def make_open(fp=full_path):
                    def _open(e):
                        try:
                            if os.path.exists(fp):
                                import subprocess, sys
                                if sys.platform.startswith("win"):
                                    os.startfile(fp)
                                elif sys.platform == "darwin":
                                    subprocess.call(["open", fp])
                                else:
                                    subprocess.call(["xdg-open", fp])
                        except Exception as ex:
                            show_status(f"{t('Cannot open')}: {ex}", ok=False)
                    return _open

                def make_delete(doc_id=fid, cid=case_id, cat=category):
                    def _del(e):
                        ok = delete_doc_file(doc_id, username, cid, cat)
                        if ok:
                            root, _ = get_merkle_root(username, cid, cat)
                            merkle_text.value = \
                                f"{t('Merkle root')}: {root[:20]}…{root[-8:]}"
                            show_status("File deleted.", ok=True)
                        load_file_list()
                    return _del

                row = ft.Container(
                    bgcolor=_WHITE,
                    border_radius=10,
                    border=ft.Border.all(1, _BORDER),
                    padding=ft.Padding(left=14, right=10, top=10, bottom=10),
                    content=ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=36, height=36,
                                bgcolor=f"{icol}18",
                                border_radius=8,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(icon, color=icol, size=20)
                            ),
                            ft.Column(
                                spacing=2, expand=True,
                                controls=[
                                    ft.Text(orig, size=13,
                                            weight=ft.FontWeight.W_500,
                                            color=_DARK,
                                            overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text(
                                        f"{_fmt_size(sz)}  ·  {uon}  ·  "
                                        f"SHA {fhash[:12]}…",
                                        size=11, color=_SLATE
                                    ),
                                ]
                            ),
                            ft.IconButton(
                                icon=ft.Icons.OPEN_IN_NEW,
                                icon_color=_BLUE, icon_size=18,
                                tooltip=t("Open file"),
                                on_click=make_open(),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=_RED, icon_size=18,
                                tooltip=t("Delete"),
                                on_click=make_delete(),
                            ),
                        ]
                    )
                )
                file_list_col.controls.append(row)

        page.update()

    # ── file picker result ──
    def process_picked_files(files):
        if not files:
            return
        case_id  = selected_case["id"]
        category = pending_category["name"]
        if not case_id or not category:
            show_status("Select a case folder first.", ok=False)
            return

        today = datetime.now().strftime("%d-%m-%Y")
        results = []
        for f in files:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                results.append(f"⚠ {f.name}: type not allowed")
                continue
            try:
                if f.bytes is not None:
                    data = f.bytes
                elif f.path:
                    with open(f.path, "rb") as fh:
                        data = fh.read()
                else:
                    raise ValueError("No file data returned by the file picker")
                ok, msg = save_uploaded_file(
                    username, case_id, category, data, f.name, today
                )
                results.append(
                    f"✓ {f.name}" if ok else f"✗ {f.name}: {msg}"
                )
            except Exception as ex:
                results.append(f"✗ {f.name}: {ex}")

        root, _ = get_merkle_root(username, case_id, category)
        merkle_text.value = f"{t('Merkle root')}: {root[:20]}…{root[-8:]}"
        show_status("  |  ".join(results), ok=all(r.startswith("✓") for r in results))
        load_file_list()
        rebuild_tree()

    async def handle_upload_click(e):
        files = await upload_pick.pick_files(
            dialog_title="Select files to upload",
            allow_multiple=True,
            allowed_extensions=[ext.lstrip(".") for ext in ALLOWED_EXTENSIONS],
            with_data=True,
        )
        process_picked_files(files)

    upload_btn.on_click = handle_upload_click

    # ── right panel content ──
    right_panel.controls = [
        # header
        ft.Container(
            bgcolor=_WHITE,
            border_radius=12,
            border=ft.Border.all(1, _BORDER),
            padding=ft.Padding(left=18, right=18, top=14, bottom=14),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[cat_title_ref, cat_sub_ref]
                    ),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Container(
                                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                border_radius=8,
                                bgcolor="#F1F5F9",
                                content=merkle_text,
                            ),
                            upload_btn,
                        ]
                    )
                ]
            )
        ),
        ft.Container(height=8),
        status_text,
        ft.Container(height=4),
        # files
        ft.Container(
            expand=True,
            content=file_list_col,
        ),
    ]

    # ── register the file picker as a page service (required in Flet 0.85.x —
    #    Service controls like FilePicker must be added via page.services,
    #    NOT page.overlay, or pick_files() will silently do nothing) ──
    if page is not None and upload_pick not in page.services:
        page.services.append(upload_pick)

    # ── left tree panel ──
    rebuild_tree()

    left_panel = ft.Container(
        width=280,
        bgcolor=_WHITE,
        border_radius=14,
        border=ft.Border.all(1, _BORDER),
        padding=ft.Padding(left=12, right=12, top=16, bottom=16),
        content=ft.Column(
            spacing=6,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.ACCOUNT_TREE, color=_BLUE, size=18),
                        ft.Text(t("Client Documents"),
                                size=15, weight=ft.FontWeight.BOLD, color=_DARK),
                    ]
                ),
                ft.Container(
                    height=1, bgcolor=_BORDER,
                    margin=ft.Margin(top=4, bottom=8, left=0, right=0)
                ),
                tree_col,
            ]
        )
    )

    right_wrapper = ft.Container(
        expand=True,
        padding=ft.Padding(left=14, right=0, top=0, bottom=0),
        content=right_panel,
    )

    placeholder = ft.Container(
        expand=True,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.FOLDER_OPEN, size=64, color="#CBD5E1"),
                ft.Text(t("Select a case folder to view documents"),
                        size=15, color=_SLATE),
            ]
        )
    )

    body_row = ft.Row(
        expand=True,
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            left_panel,
            ft.Stack(
                expand=True,
                controls=[
                    placeholder,
                    right_wrapper,
                ]
            )
        ]
    )

    return ft.Container(
        expand=True,
        bgcolor=_BG,
        padding=24,
        content=ft.Column(
            expand=True,
            spacing=12,
            controls=[
                navbar(
                    user_info=user_info,
                    on_logout=(
                        lambda e: load_page("home")
                    ) if load_page else None
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.Icons.FOLDER_COPY, color=_BLUE, size=22),
                                ft.Column(
                                    spacing=0,
                                    controls=[
                                        ft.Text(t("Client Documents"),
                                                size=22, weight=ft.FontWeight.BOLD,
                                                color=_DARK),
                                        ft.Text(
                                            t("Merkle-verified document store — "
                                            "PDF, Word, Excel, Images and more"),
                                            color=_SLATE, size=12
                                        ),
                                    ]
                                )
                            ]
                        ),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip=t("Refresh"),
                            icon_color=_SLATE,
                            on_click=lambda e: load_page("documents") if load_page else page.update(),
                        ),
                    ]
                ),

                body_row,
            ]
        )
    )
