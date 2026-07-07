"""Box 1 — Active Cases: shows only cases with status='Active'."""
import flet as ft
from i18n import t

from components.navbar import navbar
from services.db import get_all_cases

_BLUE  = "#4A7FC1"
_GREEN = "#4A8C6A"
_SLATE = "#64748B"


def active_cases_only_view(page, load_page, open_case_detail, user_info=None, on_translate=None):

    is_dark        = page.theme_mode == ft.ThemeMode.DARK
    page_bg        = "#0F172A" if is_dark else "#F8FAFC"
    card_bg        = "#1E293B" if is_dark else "white"
    primary_text   = "white"   if is_dark else "#111827"
    secondary_text = "#CBD5E1" if is_dark else "#6B7280"
    divider_color  = "#334155" if is_dark else "#D1D5DB"

    all_cases = get_all_cases()
    active = [c for c in all_cases if c[6] == "Active"]

    rows = []
    for c in active:
        case_id       = c[2]
        client_name   = c[3]
        advocate_name = c[4]
        court         = c[5]
        status        = c[6]

        rows.append(
            ft.DataRow(
                on_select_change=lambda e, cid=case_id: open_case_detail(cid),
                cells=[
                    ft.DataCell(ft.Text(case_id,       color=primary_text)),
                    ft.DataCell(ft.Text(client_name,   color=primary_text)),
                    ft.DataCell(ft.Text(advocate_name, color=primary_text)),
                    ft.DataCell(ft.Text(court,         color=primary_text)),
                    ft.DataCell(ft.Text(t(status),     color=_GREEN)),
                ]
            )
        )

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
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.START,
                            controls=[
                                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: load_page("dashboard")),
                                ft.Icon(ft.Icons.GAVEL, color=_BLUE, size=26),
                                ft.Text(t("Active Cases"), size=26, weight=ft.FontWeight.BOLD, color=primary_text),
                            ]
                        ),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip=t("Refresh"),
                            icon_color=_SLATE,
                            on_click=lambda e: load_page("active_cases_only"),
                        ),
                    ]
                ),

                ft.Container(
                    bgcolor=card_bg, padding=20, border_radius=12,
                    content=ft.Column(controls=[
                        ft.Text(f"{t('Active Cases')} ({len(active)})", size=20, color=primary_text, weight=ft.FontWeight.BOLD),
                        ft.Text(t("Click on a case to view full details"), size=12, color=secondary_text),
                        ft.Divider(color=divider_color),
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text(t("Case ID"),   color=primary_text)),
                                ft.DataColumn(ft.Text(t("Client"),    color=primary_text)),
                                ft.DataColumn(ft.Text(t("Advocate"),  color=primary_text)),
                                ft.DataColumn(ft.Text(t("Court"),     color=primary_text)),
                                ft.DataColumn(ft.Text(t("Status"),    color=primary_text)),
                            ],
                            rows=rows,
                        ) if rows else ft.Text(t("No active cases found."), color=secondary_text, size=14),
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
