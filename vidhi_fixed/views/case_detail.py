import flet as ft
import os
from i18n import t

from components.navbar import navbar
from services.db import (
    get_case_by_id,
    approve_case,
    reject_case,
    get_hearings,
    get_payments_by_case,
    get_all_doc_files,
    get_case_note,
    save_case_note,
)

_BLUE  = "#4A7FC1"
_GREEN = "#4A8C6A"
_RED   = "#DC2626"
_SLATE = "#64748B"
_AMBER = "#7A6A3A"


def case_detail_view(page, load_page, case_id, user_info=None, from_page="active_cases_only", on_translate=None):

    is_dark        = page.theme_mode == ft.ThemeMode.DARK
    page_bg        = "#0F172A" if is_dark else "#F8FAFC"
    card_bg        = "#1E293B" if is_dark else "white"
    primary_text   = "white"   if is_dark else "#111827"
    secondary_text = "#CBD5E1" if is_dark else "#6B7280"
    divider_color  = "#334155" if is_dark else "#D1D5DB"
    field_bg       = "#334155" if is_dark else "#F1F5F9"
    tag_bg         = "#253347" if is_dark else "#EFF6FF"

    case = get_case_by_id(case_id)
    if not case:
        return ft.Container(
            expand=True, padding=20,
            content=ft.Column(controls=[ft.Text(t("Case not found"), size=22, color="red")])
        )

    # case columns: id(0) username(1) case_id(2) client_name(3) advocate_name(4)
    #               court(5) status(6) case_type(7) description(8) urgency(9)
    request_id    = case[2]
    client_name   = case[3]
    advocate_name = case[4]
    court         = case[5]
    status        = case[6]
    case_type     = case[7] or "—"
    description   = case[8] or "—"
    urgency       = case[9] or "—"
    username      = case[1]

    # ── Status chip ────────────────────────────────────────────────────────────
    status_text = ft.Text(
        status, size=14, weight=ft.FontWeight.BOLD,
        color=_GREEN if status == "Active" else "orange"
    )

    # ── Hearing table ──────────────────────────────────────────────────────────
    hearing_col = ft.Column()

    def load_hearings():
        hearing_col.controls.clear()
        hearings = get_hearings(request_id)
        if not hearings:
            hearing_col.controls.append(
                ft.Text(t("No hearings scheduled yet"), color=secondary_text, italic=True)
            )
            return
        hearing_col.controls.append(
            ft.DataTable(
                column_spacing=20,
                columns=[
                    ft.DataColumn(ft.Text(t("Date"),          color=primary_text, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("Court"),         color=primary_text, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("Judge"),         color=primary_text, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("Advocate"),      color=primary_text, weight=ft.FontWeight.BOLD)),
                ],
                rows=[
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(h[2] or "—", color=primary_text)),
                        ft.DataCell(ft.Text(h[3] or "—", color=secondary_text)),
                        ft.DataCell(ft.Text(h[4] or "—", color=_BLUE)),
                        ft.DataCell(ft.Text(h[5] or "—", color=_GREEN)),
                    ])
                    for h in hearings
                ],
            )
        )

    load_hearings()

    # ── Approve / Reject ───────────────────────────────────────────────────────
    def approve_request(e):
        approve_case(request_id)
        status_text.value = t("Active")
        status_text.color = _GREEN
        approve_btn.disabled = True
        reject_btn.visible   = False
        page.snack_bar = ft.SnackBar(ft.Text(t("Request Approved")))
        page.snack_bar.open = True
        page.update()

    def reject_request(e):
        reject_case(request_id)
        status_text.value = t("Rejected")
        status_text.color = _RED
        page.snack_bar = ft.SnackBar(ft.Text(t("Request Rejected")))
        page.snack_bar.open = True
        page.update()

    approve_btn = ft.ElevatedButton(
        t("Approve Request"), bgcolor=_GREEN, color="white",
        on_click=approve_request, disabled=(status == "Active"),
    )
    reject_btn = ft.ElevatedButton(
        t("Reject Request"), bgcolor=_RED, color="white",
        on_click=reject_request, visible=(status != "Active"),
    )

    # ── Real documents from DB ─────────────────────────────────────────────────
    all_docs = get_all_doc_files()
    # all_docs: (id, username, case_id, category, orig_name, stored_name, file_hash, uploaded_on, size_bytes)
    case_docs = [d for d in all_docs if d[2] == request_id]

    def _ext_icon_color(filename):
        ext = os.path.splitext(filename)[1].lower()
        m = {
            ".pdf":  ("#DC2626", ft.Icons.PICTURE_AS_PDF),
            ".doc":  ("#1D4ED8", ft.Icons.DESCRIPTION),
            ".docx": ("#1D4ED8", ft.Icons.DESCRIPTION),
            ".xls":  ("#047857", ft.Icons.TABLE_CHART),
            ".xlsx": ("#047857", ft.Icons.TABLE_CHART),
            ".jpg":  ("#7C3AED", ft.Icons.IMAGE),
            ".jpeg": ("#7C3AED", ft.Icons.IMAGE),
            ".png":  ("#7C3AED", ft.Icons.IMAGE),
        }
        c, i = m.get(ext, ("#64748B", ft.Icons.INSERT_DRIVE_FILE))
        return c, i

    doc_controls = []
    for d in case_docs[:8]:   # show up to 8
        color, icon = _ext_icon_color(d[4])
        doc_controls.append(
            ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, size=16, color=color),
                    ft.Text(d[4], size=12, color=primary_text,
                            overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                    ft.Text(d[7] or "—", size=10, color=secondary_text),
                ]
            )
        )

    if not doc_controls:
        doc_controls.append(
            ft.Text(t("No documents uploaded yet"), color=secondary_text,
                    italic=True, size=12)
        )

    # ── Real payments summary ──────────────────────────────────────────────────
    payments = get_payments_by_case(request_id)
    # (id, case_id, fee_type, amount, payment_status, payment_method, payment_date, deadline, ...)
    total_fees   = sum(float(p[3]) for p in payments)
    paid_fees    = sum(float(p[3]) for p in payments if p[4] == "Paid")
    pending_fees = total_fees - paid_fees

    # ── Case Notes (replaces AI Legal Insights) ───────────────────────────────
    existing_note = get_case_note(request_id)
    note_value    = existing_note[0] if existing_note else ""
    note_updated  = existing_note[1] if existing_note else ""

    notes_field = ft.TextField(
        value=note_value,
        multiline=True,
        min_lines=4,
        max_lines=8,
        hint_text=t("Add case notes, observations, strategy, key facts..."),
        border_color=_BLUE,
        bgcolor=field_bg,
    )
    notes_saved_text = ft.Text(
        f"{t('Last saved')}: {note_updated}" if note_updated else "",
        size=10, color=secondary_text, italic=True
    )

    def save_note(e):
        ts = save_case_note(request_id, notes_field.value or "")
        notes_saved_text.value = f"{t('Last saved')}: {ts}"
        page.snack_bar = ft.SnackBar(ft.Text(t("✔ Notes saved")))
        page.snack_bar.open = True
        page.update()

    # ── Urgency & type tags ────────────────────────────────────────────────────
    def _tag(label, color):
        return ft.Container(
            bgcolor=color + "22", border_radius=8,
            padding=ft.Padding(top=4, bottom=4, left=12, right=12),
            content=ft.Text(label, size=12, color=color, weight=ft.FontWeight.BOLD),
        )

    urgency_color = {"High": _RED, "Normal": _GREEN, "Low": _SLATE}.get(urgency, _SLATE)

    # ── Layout ─────────────────────────────────────────────────────────────────
    left_col = ft.Column(
        expand=3, spacing=14,
        controls=[
            # Matter Info card
            ft.Container(
                bgcolor=card_bg, padding=20, border_radius=12,
                content=ft.Column(spacing=12, controls=[
                    ft.Text(t("Matter Information"), size=17,
                            weight=ft.FontWeight.BOLD, color=primary_text),
                    ft.Divider(color=divider_color),
                    # Row of key fields
                    ft.Row(spacing=24, wrap=True, controls=[
                        ft.Column(spacing=2, controls=[
                            ft.Text(t("Client"), size=11, color=secondary_text),
                            ft.Text(client_name or "—", size=13,
                                    weight=ft.FontWeight.BOLD, color=primary_text),
                        ]),
                        ft.Column(spacing=2, controls=[
                            ft.Text(t("Case Type"), size=11, color=secondary_text),
                            ft.Text(case_type, size=13, color=primary_text),
                        ]),
                        ft.Column(spacing=2, controls=[
                            ft.Text(t("Court"), size=11, color=secondary_text),
                            ft.Text(court or "—", size=13,
                                    weight=ft.FontWeight.BOLD, color=primary_text),
                        ]),
                        ft.Column(spacing=2, controls=[
                            ft.Text(t("Advocate"), size=11, color=secondary_text),
                            ft.Text(advocate_name or "—", size=13, color=_BLUE),
                        ]),
                        ft.Column(spacing=2, controls=[
                            ft.Text(t("Status"), size=11, color=secondary_text),
                            status_text,
                        ]),
                        ft.Column(spacing=2, controls=[
                            ft.Text(t("Urgency"), size=11, color=secondary_text),
                            _tag(urgency, urgency_color),
                        ]),
                    ]),
                    ft.Divider(color=divider_color),
                    ft.Text(t("Description"), size=12, color=secondary_text),
                    ft.Container(
                        bgcolor=field_bg, border_radius=8, padding=10,
                        content=ft.Text(description, size=13, color=primary_text),
                    ),
                    # Approve / Reject
                    ft.Row(spacing=10, controls=[approve_btn, reject_btn]),
                ])
            ),

            # Case Notes (replaces AI Legal Insights)
            ft.Container(
                bgcolor=card_bg, padding=20, border_radius=12,
                content=ft.Column(spacing=10, controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(spacing=8, controls=[
                                ft.Icon(ft.Icons.NOTES, color=_BLUE, size=18),
                                ft.Text(t("Case Notes"), size=17,
                                        weight=ft.FontWeight.BOLD, color=primary_text),
                            ]),
                            ft.ElevatedButton(
                                t("Save Notes"), bgcolor=_BLUE, color="white",
                                height=32, on_click=save_note,
                            ),
                        ]
                    ),
                    ft.Text(
                        t("Record observations, legal strategy, key facts or reminders for this case."),
                        size=12, color=secondary_text,
                    ),
                    ft.Divider(color=divider_color),
                    notes_field,
                    notes_saved_text,
                ])
            ),

            # Hearing History
            ft.Container(
                bgcolor=card_bg, padding=20, border_radius=12,
                content=ft.Column(spacing=10, controls=[
                    ft.Row(spacing=8, controls=[
                        ft.Icon(ft.Icons.HISTORY, color=_BLUE, size=18),
                        ft.Text(t("Hearing History"), size=17,
                                weight=ft.FontWeight.BOLD, color=primary_text),
                    ]),
                    ft.Divider(color=divider_color),
                    hearing_col,
                ])
            ),
        ]
    )

    right_col = ft.Column(
        expand=1, spacing=14,
        controls=[
            # Documents panel
            ft.Container(
                bgcolor=card_bg, padding=18, border_radius=12,
                content=ft.Column(spacing=10, controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(spacing=6, controls=[
                                ft.Icon(ft.Icons.FOLDER_OPEN, color=_BLUE, size=16),
                                ft.Text(t("Documents"), size=15,
                                        weight=ft.FontWeight.BOLD, color=primary_text),
                            ]),
                            ft.Container(
                                bgcolor=_BLUE + "22", border_radius=6,
                                padding=ft.Padding(top=2, bottom=2, left=8, right=8),
                                content=ft.Text(str(len(case_docs)), size=11,
                                                color=_BLUE, weight=ft.FontWeight.BOLD),
                            ),
                        ]
                    ),
                    ft.Divider(color=divider_color),
                    *doc_controls,
                    ft.Container(height=4),
                    ft.ElevatedButton(
                        t("Manage in Documents"),
                        bgcolor=_BLUE, color="white",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=lambda e: load_page("documents"),
                    ),
                ])
            ),

            # Payments summary
            ft.Container(
                bgcolor=card_bg, padding=18, border_radius=12,
                content=ft.Column(spacing=10, controls=[
                    ft.Row(spacing=6, controls=[
                        ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color=_GREEN, size=16),
                        ft.Text(t("Payments"), size=15,
                                weight=ft.FontWeight.BOLD, color=primary_text),
                    ]),
                    ft.Divider(color=divider_color),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(t("Total Fees"), size=12, color=secondary_text),
                            ft.Text(f"₹ {total_fees:,.0f}", size=13,
                                    weight=ft.FontWeight.BOLD, color=primary_text),
                        ]
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(t("Paid"), size=12, color=secondary_text),
                            ft.Text(f"₹ {paid_fees:,.0f}", size=13,
                                    weight=ft.FontWeight.BOLD, color=_GREEN),
                        ]
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(t("Pending"), size=12, color=secondary_text),
                            ft.Text(f"₹ {pending_fees:,.0f}", size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=_RED if pending_fees > 0 else _GREEN),
                        ]
                    ),
                    ft.Divider(color=divider_color),
                    ft.ElevatedButton(
                        t("Go to Billing"),
                        bgcolor=_GREEN, color="white",
                        icon=ft.Icons.RECEIPT_LONG,
                        on_click=lambda e: load_page("billing"),
                    ),
                ])
            ),

            # Case IDs / quick info
            ft.Container(
                bgcolor=card_bg, padding=18, border_radius=12,
                content=ft.Column(spacing=8, controls=[
                    ft.Row(spacing=6, controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=_SLATE, size=16),
                        ft.Text(t("Quick Info"), size=15,
                                weight=ft.FontWeight.BOLD, color=primary_text),
                    ]),
                    ft.Divider(color=divider_color),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(t("Request ID"), size=12, color=secondary_text),
                            ft.Text(request_id, size=12,
                                    color=_BLUE, weight=ft.FontWeight.BOLD),
                        ]
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(t("Hearings"), size=12, color=secondary_text),
                            ft.Text(str(len(get_hearings(request_id))), size=12,
                                    color=primary_text, weight=ft.FontWeight.BOLD),
                        ]
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(t("Payments"), size=12, color=secondary_text),
                            ft.Text(str(len(payments)), size=12,
                                    color=primary_text, weight=ft.FontWeight.BOLD),
                        ]
                    ),
                ])
            ),
        ]
    )

    return ft.Container(
        expand=True,
        padding=20,
        bgcolor=page_bg,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                navbar(
                    user_info=user_info,
                    on_logout=(lambda e: load_page("home")) if load_page else None,
                    on_translate=on_translate
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=lambda e: load_page(from_page)
                            ),
                            ft.Icon(ft.Icons.GAVEL, color=_BLUE, size=22),
                            ft.Text(t("Case Details"), size=24,
                                    weight=ft.FontWeight.BOLD, color=primary_text),
                        ]),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip=t("Refresh"),
                            icon_color=_SLATE,
                            on_click=lambda e: load_page("case_detail", case_id, from_page),
                        ),
                    ]
                ),
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[left_col, right_col],
                ),
            ]
        )
    )
