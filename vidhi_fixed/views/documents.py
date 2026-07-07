"""documents.py - VIDHI Legal AI (Advocate side) — dark-mode aware."""

import os
from datetime import datetime

import flet as ft
from i18n import t

from components.cards import stat_card
from services.db import (
    get_all_cases,
    get_all_doc_files,
    get_files_in_category,
    save_uploaded_file,
    delete_doc_file,
    get_merkle_root,
    get_category_path,
    FOLDER_CATEGORIES,
)

_BLUE  = "#4A7FC1"
_GREEN = "#4A8C6A"
_AMBER = "#B07D3A"
_SLATE = "#64748B"
_RED   = "#EF4444"
_WHITE = "white"
_BORDER = "#E2E8F0"


def _fmt_size(b):
    if b < 1024:        return f"{b} B"
    elif b < 1048576:   return f"{b/1024:.1f} KB"
    return f"{b/1048576:.1f} MB"


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
        ".txt":  (ft.Icons.TEXT_SNIPPET,   "#64748B"),
        ".csv":  (ft.Icons.GRID_ON,        "#0EA5E9"),
        ".zip":  (ft.Icons.FOLDER_ZIP,     "#92400E"),
        ".rar":  (ft.Icons.FOLDER_ZIP,     "#92400E"),
    }
    return mapping.get(ext, (ft.Icons.INSERT_DRIVE_FILE, "#64748B"))


def documents_view(page=None, load_page=None, user_info=None):

    is_dark        = page.theme_mode == ft.ThemeMode.DARK if page else False
    page_bg        = "#0F172A" if is_dark else "#F8FAFC"
    card_bg        = "#1E293B" if is_dark else "white"
    primary_text   = "white"   if is_dark else "#111827"
    secondary_text = "#CBD5E1" if is_dark else "#6B7280"
    divider_color  = "#334155" if is_dark else "#D1D5DB"
    file_card_bg   = "#253347" if is_dark else _WHITE
    file_card_bdr  = "#334155" if is_dark else _BORDER
    merkle_bg      = "#334155" if is_dark else "#F1F5F9"

    all_cases = get_all_cases()
    case_owner = {}
    case_label = {}
    for row in all_cases:
        _id, username, case_id, client_name = row[0], row[1], row[2], row[3]
        status = row[6] if len(row) > 6 else ""
        case_owner[case_id] = username
        case_label[case_id] = f"{case_id} - {client_name or 'Unknown'} ({status})"

    selected    = {"case_id": None, "username": None, "category": FOLDER_CATEGORIES[0]}
    upload_pick = ft.FilePicker()

    status_text   = ft.Text("", size=13)
    merkle_text   = ft.Text("", size=10, color=_SLATE, selectable=True, font_family="monospace")
    file_list_col = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)

    all_docs = get_all_doc_files()

    stats_row = ft.Row(controls=[
        stat_card("Total Documents",   len(all_docs)),
        stat_card("Cases",             len(all_cases)),
        stat_card("Folder Categories", len(FOLDER_CATEGORIES)),
        stat_card("AI Analyzed",       0),
    ])

    def refresh_stats():
        docs_now = get_all_doc_files()
        stats_row.controls[0] = stat_card("Total Documents", len(docs_now))
        if page: page.update()

    case_dd = ft.Dropdown(
        label=t("Select case"),
        hint_text=t("Choose a case to manage documents"),
        options=[ft.dropdown.Option(key=cid, text=label) for cid, label in case_label.items()],
        expand=2,
    )
    category_dd = ft.Dropdown(
        label=t("Folder / category"),
        value=FOLDER_CATEGORIES[0],
        options=[ft.dropdown.Option(key=c, text=t(c)) for c in FOLDER_CATEGORIES],
        expand=1,
    )
    upload_btn = ft.ElevatedButton(t("Upload File"), icon=ft.Icons.UPLOAD_FILE, bgcolor=_BLUE, color=_WHITE, disabled=True)

    def show_status(msg, ok=True):
        status_text.value = msg
        status_text.color = _GREEN if ok else _RED
        if page: page.update()

    def load_file_list():
        file_list_col.controls.clear()
        case_id  = selected["case_id"]
        username = selected["username"]
        category = selected["category"]

        if not case_id:
            file_list_col.controls.append(
                ft.Container(padding=30, content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.FOLDER_OPEN, size=44, color="#CBD5E1"),
                        ft.Text(t("Select a case above to view or upload its documents"), color=_SLATE, size=13),
                    ]
                ))
            )
            if page: page.update()
            return

        rows = get_files_in_category(username, case_id, category)
        if not rows:
            file_list_col.controls.append(
                ft.Container(padding=30, content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.CLOUD_UPLOAD_OUTLINED, size=44, color="#CBD5E1"),
                        ft.Text(t("No files yet in this folder. Upload the first one!"), color=_SLATE, size=13),
                    ]
                ))
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
                                if sys.platform.startswith("win"):   os.startfile(fp)
                                elif sys.platform == "darwin":       subprocess.call(["open", fp])
                                else:                                subprocess.call(["xdg-open", fp])
                        except Exception as ex:
                            show_status(f"{t('Cannot open')}: {ex}", ok=False)
                    return _open

                def make_delete(doc_id=fid, uname=username, cid=case_id, cat=category):
                    def _del(e):
                        ok = delete_doc_file(doc_id, uname, cid, cat)
                        if ok:
                            show_status("File deleted.", ok=True)
                            refresh_stats()
                        load_file_list()
                    return _del

                file_list_col.controls.append(
                    ft.Container(
                        bgcolor=file_card_bg, border_radius=10,
                        border=ft.Border.all(1, file_card_bdr),
                        padding=ft.Padding(left=14, right=10, top=10, bottom=10),
                        content=ft.Row(
                            spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(width=36, height=36, bgcolor=f"{icol}18", border_radius=8,
                                             alignment=ft.Alignment.CENTER,
                                             content=ft.Icon(icon, color=icol, size=20)),
                                ft.Column(spacing=2, expand=True, controls=[
                                    ft.Text(orig, size=13, weight=ft.FontWeight.W_500,
                                            color=primary_text, overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text(f"{_fmt_size(sz)}  ·  {uon}  ·  SHA {fhash[:12]}…",
                                            size=11, color=_SLATE),
                                ]),
                                ft.IconButton(icon=ft.Icons.OPEN_IN_NEW, icon_color=_BLUE, icon_size=18,
                                              tooltip=t("Open file"), on_click=make_open()),
                                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=_RED, icon_size=18,
                                              tooltip=t("Delete"), on_click=make_delete()),
                            ]
                        )
                    )
                )
        if page: page.update()

    def on_case_change(e):
        case_id = case_dd.value
        selected["case_id"]  = case_id
        selected["username"] = case_owner.get(case_id)
        upload_btn.disabled  = case_id is None
        if case_id:
            root, _ = get_merkle_root(selected["username"], case_id, selected["category"])
            merkle_text.value = f"{t('Merkle root')}: {root[:20]}...{root[-8:]}"
        else:
            merkle_text.value = ""
        load_file_list()

    def on_category_change(e):
        selected["category"] = category_dd.value
        if selected["case_id"]:
            root, _ = get_merkle_root(selected["username"], selected["case_id"], selected["category"])
            merkle_text.value = f"{t('Merkle root')}: {root[:20]}...{root[-8:]}"
        load_file_list()

    case_dd.on_select     = on_case_change
    category_dd.on_select = on_category_change

    def process_picked_files(files):
        if not files: return
        case_id  = selected["case_id"]
        username = selected["username"]
        category = selected["category"]
        if not case_id:
            show_status("Select a case first.", ok=False)
            return
        today   = datetime.now().strftime("%d-%m-%Y")
        results = []
        for f in files:
            try:
                if f.bytes is not None:           data = f.bytes
                elif f.path:
                    with open(f.path, "rb") as fh: data = fh.read()
                else:                              raise ValueError("No file data")
                ok, msg = save_uploaded_file(username, case_id, category, data, f.name, today)
                results.append(f"OK {f.name}" if ok else f"FAILED {f.name}: {msg}")
            except Exception as ex:
                results.append(f"FAILED {f.name}: {ex}")
        root, _ = get_merkle_root(username, case_id, category)
        merkle_text.value = f"{t('Merkle root')}: {root[:20]}...{root[-8:]}"
        show_status("  |  ".join(results), ok=all(r.startswith("OK") for r in results))
        load_file_list()
        refresh_stats()
        if page: page.update()

    async def handle_upload_click(e):
        files = await upload_pick.pick_files(dialog_title="Select files to upload", allow_multiple=True, with_data=True)
        process_picked_files(files)

    upload_btn.on_click = handle_upload_click

    if page is not None and upload_pick not in page.services:
        page.services.append(upload_pick)

    load_file_list()

    upload_panel = ft.Container(
        bgcolor=card_bg, padding=20, border_radius=12,
        content=ft.Column(spacing=12, controls=[
            ft.Row(spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Icon(ft.Icons.FOLDER_COPY, color=_BLUE, size=20),
                ft.Text(t("Upload Document for a Case"), size=18, weight=ft.FontWeight.BOLD, color=primary_text),
            ]),
            ft.Text(t("Pick a case and a folder, then upload any file type."), size=12, color=_SLATE),
            ft.Divider(color=divider_color),
            ft.ResponsiveRow(controls=[
                ft.Container(content=case_dd, col=6),
                ft.Container(content=category_dd, col=3),
                ft.Container(content=upload_btn, col=3, alignment=ft.Alignment.CENTER_RIGHT),
            ]),
            ft.Row(controls=[
                ft.Container(padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                             border_radius=8, bgcolor=merkle_bg, content=merkle_text),
            ]),
            status_text,
            ft.Divider(color=divider_color),
            ft.Container(content=file_list_col, height=320),
        ])
    )

    return ft.Container(
        expand=True, padding=20, bgcolor=page_bg,
        content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(t("Document Intelligence"), size=28, weight=ft.FontWeight.BOLD, color=primary_text),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip=t("Refresh"),
                        icon_color="#64748B",
                        on_click=lambda e: load_page("documents") if load_page else page.update(),
                    ),
                ]
            ),
            stats_row,
            ft.Container(height=10),
            upload_panel,
            ft.Container(height=10),
            ft.Container(
                bgcolor=card_bg, padding=20, border_radius=12,
                content=ft.Column(controls=[
                    ft.Text(t("AI Document Analysis"), size=18, weight=ft.FontWeight.BOLD, color=primary_text),
                    ft.Divider(color=divider_color),
                    ft.Text(t("Risk Score: Low"),         color=primary_text),
                    ft.Text(t("Missing Clauses: None"),   color=primary_text),
                    ft.Text(t("Document Review Ready"),   color=primary_text),
                ])
            ),
        ])
    )
