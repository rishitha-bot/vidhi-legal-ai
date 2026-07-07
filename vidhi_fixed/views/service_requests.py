"""Box 2 — Service Requests: shows only cases that are NOT Active."""
import flet as ft
from i18n import t

from components.navbar import navbar
from services.db import get_all_cases, approve_case, reject_case

_BLUE   = "#4A7FC1"
_TEAL   = "#4A8FA8"
_GREEN  = "#4A8C6A"
_RED    = "#DC2626"
_AMBER  = "#B07D3A"
_SLATE  = "#64748B"


def _status_colour(status):
    return {
        "Active":          _GREEN,
        "Pending Review":  _AMBER,
        "Rejected":        _RED,
    }.get(status, _SLATE)


def service_requests_view(page, load_page, user_info=None, on_translate=None):

    is_dark        = page.theme_mode == ft.ThemeMode.DARK
    page_bg        = "#0F172A" if is_dark else "#F8FAFC"
    card_bg        = "#1E293B" if is_dark else "white"
    primary_text   = "white"   if is_dark else "#111827"
    secondary_text = "#CBD5E1" if is_dark else "#6B7280"
    divider_color  = "#334155" if is_dark else "#D1D5DB"
    card_border    = "#334155" if is_dark else "#E2E8F0"

    list_col = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=12)

    def refresh():
        list_col.controls.clear()
        all_cases = get_all_cases()
        pending = [c for c in all_cases if c[6] != "Active"]

        if not pending:
            list_col.controls.append(
                ft.Text(t("No pending service requests."), color=secondary_text, size=14)
            )
            page.update()
            return

        for c in pending:
            case_id       = c[2]
            client_name   = c[3]
            advocate_name = c[4]
            court         = c[5]
            status        = c[6]

            status_ref      = ft.Ref[ft.Text]()
            approve_btn_ref = ft.Ref[ft.ElevatedButton]()
            reject_btn_ref  = ft.Ref[ft.ElevatedButton]()

            def make_approve(cid, sref, aref, rref):
                def _approve(e):
                    approve_case(cid)
                    sref.current.value = t("Active")
                    sref.current.color = _GREEN
                    aref.current.disabled = True
                    rref.current.visible  = False
                    page.snack_bar = ft.SnackBar(ft.Text(t("Request Approved")))
                    page.snack_bar.open = True
                    page.update()
                return _approve

            def make_reject(cid, sref, aref, rref):
                def _reject(e):
                    reject_case(cid)
                    sref.current.value = t("Rejected")
                    sref.current.color = _RED
                    aref.current.disabled = False
                    page.snack_bar = ft.SnackBar(ft.Text(t("Request Rejected")))
                    page.snack_bar.open = True
                    page.update()
                return _reject

            already_rejected = (status == "Rejected")

            card = ft.Container(
                bgcolor=card_bg,
                border_radius=12,
                border=ft.Border.all(1, card_border),
                padding=16,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(
                                    f"{t('Request ID')}: {case_id}",
                                    size=15, weight=ft.FontWeight.BOLD, color=primary_text
                                ),
                                ft.Text(
                                    t(status), size=13,
                                    color=_status_colour(status),
                                    weight=ft.FontWeight.BOLD,
                                    ref=status_ref,
                                ),
                            ]
                        ),
                        ft.Row(spacing=20, controls=[
                            ft.Text(f"👤 {client_name}",   size=13, color=secondary_text),
                            ft.Text(f"⚖️ {advocate_name}", size=13, color=secondary_text),
                            ft.Text(f"🏛 {court}",         size=13, color=secondary_text),
                        ]),
                        ft.Row(spacing=10, controls=[
                            ft.ElevatedButton(
                                t("Accept"), bgcolor=_GREEN, color="white",
                                ref=approve_btn_ref,
                                on_click=make_approve(case_id, status_ref, approve_btn_ref, reject_btn_ref),
                                disabled=already_rejected,
                            ),
                            ft.ElevatedButton(
                                t("Reject"), bgcolor=_RED, color="white",
                                ref=reject_btn_ref,
                                on_click=make_reject(case_id, status_ref, approve_btn_ref, reject_btn_ref),
                                visible=not already_rejected,
                            ),
                        ]),
                    ]
                )
            )
            list_col.controls.append(card)

        page.update()

    refresh()

    return ft.Container(
        expand=True, padding=20, bgcolor=page_bg,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                navbar(
                    user_info=user_info,
                    on_logout=(lambda e: load_page("home")) if load_page else None,
                    on_translate=on_translate
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    controls=[
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: load_page("dashboard")),
                        ft.Icon(ft.Icons.INBOX, color=_TEAL, size=26),
                        ft.Text(t("Service Requests"), size=26, weight=ft.FontWeight.BOLD, color=primary_text),
                    ]
                ),

                ft.Text(
                    t("Active cases are excluded — only pending / rejected requests are shown here."),
                    size=12, color=secondary_text, italic=True
                ),

                ft.Container(height=8),

                ft.Container(
                    bgcolor=card_bg, padding=20, border_radius=12,
                    content=ft.Column(controls=[
                        ft.Text(t("Pending Service Requests"), size=18, weight=ft.FontWeight.BOLD, color=primary_text),
                        ft.Divider(color=divider_color),
                        list_col,
                    ])
                ),

                ft.Container(
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Divider(color=divider_color),
                            ft.Text(t("VIDHI Legal AI © 2026"), size=14, color=secondary_text),
                            ft.Text(t("AI-Powered Legal Intelligence Platform"), size=12, color=secondary_text),
                        ]
                    )
                )
            ]
        )
    )
