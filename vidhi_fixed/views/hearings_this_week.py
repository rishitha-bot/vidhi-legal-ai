"""Box 3 — Hearings This Week."""
import flet as ft
from datetime import datetime, timedelta
from i18n import t

from components.navbar import navbar
from services.db import get_hearings_this_week

_BLUE  = "#4A7FC1"
_AMBER = "#7A6A3A"
_GREEN = "#4A8C6A"
_SLATE = "#64748B"


def hearings_this_week_view(page, load_page, open_case_detail, user_info=None, on_translate=None):

    is_dark        = page.theme_mode == ft.ThemeMode.DARK
    page_bg        = "#0F172A" if is_dark else "#F8FAFC"
    card_bg        = "#1E293B" if is_dark else "white"
    primary_text   = "white"   if is_dark else "#111827"
    secondary_text = "#CBD5E1" if is_dark else "#6B7280"
    divider_color  = "#334155" if is_dark else "#D1D5DB"

    # Live week range based on today
    today      = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end   = week_start + timedelta(days=6)
    week_label = f"{week_start.strftime('%d %b')} – {week_end.strftime('%d %b %Y')}"

    hearings_col = ft.Column()

    def load_hearings():
        hearings_col.controls.clear()
        hearings = get_hearings_this_week()

        if not hearings:
            hearings_col.controls.append(
                ft.Text(t("No hearings scheduled this week."), color=secondary_text, size=14, italic=True)
            )
            return

        rows = []
        for h in hearings:
            case_id, hearing_date, court, judge_name, advocate_name = h
            rows.append(
                ft.DataRow(
                    on_select_change=lambda e, cid=case_id: open_case_detail(cid),
                    cells=[
                        ft.DataCell(ft.Text(case_id,       color=_BLUE,         weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(hearing_date,  color=primary_text)),
                        ft.DataCell(ft.Text(court or "—",  color=primary_text)),
                        ft.DataCell(ft.Text(judge_name,    color=secondary_text)),
                        ft.DataCell(ft.Text(advocate_name, color=_GREEN)),
                    ]
                )
            )

        hearings_col.controls.append(
            ft.DataTable(
                column_spacing=20,
                columns=[
                    ft.DataColumn(ft.Text(t("Case ID"),      color=primary_text, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("Hearing Date"), color=primary_text, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("Court"),        color=primary_text, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("Judge"),        color=primary_text, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("Advocate"),     color=primary_text, weight=ft.FontWeight.BOLD)),
                ],
                rows=rows,
            )
        )

    load_hearings()

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
                        ft.Row(controls=[
                            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: load_page("dashboard")),
                            ft.Icon(ft.Icons.CALENDAR_TODAY, color=_BLUE, size=26),
                            ft.Text(t("Hearings This Week"), size=26, weight=ft.FontWeight.BOLD, color=primary_text),
                        ]),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip=t("Refresh"),
                            icon_color=_SLATE,
                            on_click=lambda e: (load_hearings(), page.update()),
                        ),
                    ]
                ),

                ft.Container(
                    bgcolor=card_bg, padding=20, border_radius=12,
                    content=ft.Column(controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(
                                    t("Scheduled Hearings This Week"),
                                    size=18, color=primary_text, weight=ft.FontWeight.BOLD
                                ),
                                ft.Container(
                                    bgcolor=_BLUE + "22", border_radius=8,
                                    padding=ft.Padding(top=4, bottom=4, left=12, right=12),
                                    content=ft.Text(week_label, size=12, color=_BLUE, weight=ft.FontWeight.BOLD),
                                ),
                            ]
                        ),
                        ft.Text(t("Click on a row to view full case details"), size=12, color=secondary_text),
                        ft.Divider(color=divider_color),
                        hearings_col,
                    ])
                ),

                ft.Container(
                    padding=20,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Divider(color=divider_color),
                            ft.Text(t("VIDHI Legal AI © 2026"), size=14, color=secondary_text),
                        ]
                    )
                )
            ]
        )
    )
