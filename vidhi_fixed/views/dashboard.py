import flet as ft
from i18n import t
from datetime import datetime, timedelta

from components.navbar import navbar
from services.db import get_all_cases, get_hearings_this_week


_BLUE  = "#4A7FC1"
_TEAL  = "#4A8FA8"
_AMBER = "#B07D3A"
_GREEN = "#4A8C6A"
_SLATE = "#64748B"


def _case_stage_funnel(is_dark, primary_text, card_bg, divider_color):
    bar_bg = "#334155" if is_dark else "#E5E7EB"
    stages = [
        ("Filed",            96, _BLUE),
        ("Hearing Scheduled", 74, _TEAL),
        ("Under Judgment",   42, _AMBER),
        ("Closed",           54, _GREEN),
    ]
    max_val = max(v for _, v, _ in stages)
    rows = []
    for label, count, colour in stages:
        bar_w = int((count / max_val) * 320)
        rows.append(
            ft.Column(
                spacing=4,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(label, size=13, color=primary_text),
                            ft.Text(str(count), size=13, weight=ft.FontWeight.BOLD, color=primary_text),
                        ]
                    ),
                    ft.Container(
                        height=18, bgcolor=bar_bg, border_radius=6,
                        content=ft.Row(spacing=0, controls=[
                            ft.Container(width=bar_w, height=18, bgcolor=colour, border_radius=6)
                        ])
                    )
                ]
            )
        )
    return ft.Container(
        bgcolor=card_bg, padding=20, border_radius=14,
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Text(t("Case Stage Funnel"), size=16, color=primary_text, weight=ft.FontWeight.BOLD),
                ft.Divider(color=divider_color),
                *rows,
            ]
        )
    )


def _stat_card(label, value, sub, card_bg, primary_text):
    return ft.Container(
        expand=True, bgcolor=card_bg, border_radius=14, padding=20,
        content=ft.Column(
            spacing=4,
            controls=[
                ft.Text(label, size=13, color=_SLATE),
                ft.Text(str(value), size=34, weight=ft.FontWeight.BOLD, color=primary_text),
                ft.Text(sub, size=11, color=_SLATE) if sub else ft.Container()
            ]
        )
    )


def dashboard_view(page, load_page=None, user_info=None, on_translate=None):

    is_dark = page.theme_mode == ft.ThemeMode.DARK
    page_bg       = "#0F172A" if is_dark else "#F8FAFC"
    card_bg       = "#1E293B" if is_dark else "white"
    primary_text  = "white"   if is_dark else "#111827"
    secondary_text = "#CBD5E1" if is_dark else "#6B7280"
    divider_color = "#334155" if is_dark else "#D1D5DB"

    all_cases = get_all_cases()
    active_count = sum(1 for c in all_cases if c[6] == "Active")
    service_request_count = sum(1 for c in all_cases if c[6] != "Active")
    hearings_week = get_hearings_this_week()
    hearings_count = len(hearings_week)

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

                ft.Container(height=10),

                ft.Row(
                    spacing=16,
                    controls=[
                        ft.GestureDetector(
                            on_tap=lambda e: load_page("active_cases_only") if load_page else None,
                            content=ft.Container(
                                width=220, bgcolor=card_bg, border_radius=14, padding=20,
                                border=ft.Border.all(2, _BLUE),
                                content=ft.Column(spacing=4, controls=[
                                    ft.Row(spacing=8, controls=[
                                        ft.Icon(ft.Icons.GAVEL, color=_BLUE, size=22),
                                        ft.Text(t("Active Cases"), color=secondary_text, size=13),
                                    ]),
                                    ft.Text(str(active_count), size=34, weight=ft.FontWeight.BOLD, color=_BLUE),
                                    ft.Text(t("Click to view all"), size=11, color=_BLUE),
                                ])
                            )
                        ),
                        ft.GestureDetector(
                            on_tap=lambda e: load_page("service_requests") if load_page else None,
                            content=ft.Container(
                                width=220, bgcolor=card_bg, border_radius=14, padding=20,
                                border=ft.Border.all(2, _TEAL),
                                content=ft.Column(spacing=4, controls=[
                                    ft.Row(spacing=8, controls=[
                                        ft.Icon(ft.Icons.INBOX, color=_TEAL, size=22),
                                        ft.Text(t("Service Requests"), color=secondary_text, size=13),
                                    ]),
                                    ft.Text(str(service_request_count), size=34, weight=ft.FontWeight.BOLD, color=_TEAL),
                                    ft.Text(t("Click to view pending"), size=11, color=_TEAL),
                                ])
                            )
                        ),
                        ft.GestureDetector(
                            on_tap=lambda e: load_page("hearings_this_week") if load_page else None,
                            content=ft.Container(
                                width=220, bgcolor=card_bg, border_radius=14, padding=20,
                                border=ft.Border.all(2, _AMBER),
                                content=ft.Column(spacing=4, controls=[
                                    ft.Row(spacing=8, controls=[
                                        ft.Icon(ft.Icons.CALENDAR_TODAY, color=_AMBER, size=22),
                                        ft.Text(t("Hearings This Week"), color=secondary_text, size=13),
                                    ]),
                                    ft.Text(str(hearings_count), size=34, weight=ft.FontWeight.BOLD, color=_AMBER),
                                    ft.Text(t("Click to view schedule"), size=11, color=_AMBER),
                                ])
                            )
                        ),
                        ft.Container(
                            width=220, bgcolor=card_bg, border_radius=14, padding=20,
                            content=ft.Column(spacing=4, controls=[
                                ft.Row(spacing=8, controls=[
                                    ft.Icon(ft.Icons.CURRENCY_RUPEE, color=_GREEN, size=22),
                                    ft.Text(t("Annual Revenue"), color=secondary_text, size=13),
                                ]),
                                ft.Text(t("45.2L"), size=34, weight=ft.FontWeight.BOLD, color=_GREEN),
                                ft.Text(t("FY 2025-26"), size=11, color=secondary_text),
                            ])
                        ),
                    ]
                ),

                ft.Container(height=10),

                ft.Row(
                    spacing=16,
                    controls=[
                        _stat_card("Cases Won",       "94", "FY 2025-26", card_bg, primary_text),
                        _stat_card("Cases Lost",      "32", "FY 2025-26", card_bg, primary_text),
                        _stat_card("Win Probability", "74%", "Average",   card_bg, primary_text),
                    ]
                ),

                ft.Container(height=10),

                _case_stage_funnel(is_dark, primary_text, card_bg, divider_color),

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
