import flet as ft
import random
from i18n import t
from services.db import (
    get_hearings_by_user,
    get_all_hearings,
    get_all_cases,
    create_hearing,
)

_BLUE  = "#4A7FC1"
_GREEN = "#4A8C6A"
_SLATE = "#64748B"

JUDGE_POOL = [
    "Hon. Justice A. Krishnamurthy",
    "Hon. Justice S. Raghavan",
    "Hon. Justice P. Mehta",
    "Hon. Justice R. Iyer",
    "Hon. Justice N. Chatterjee",
    "Hon. Justice V. Subramaniam",
    "Hon. Justice D. Kapoor",
    "Hon. Justice L. Sharma",
]


def calendar_view(user_info=None, page=None):

    is_dark        = page.theme_mode == ft.ThemeMode.DARK if page else False
    page_bg        = "#0F172A" if is_dark else "#F8FAFC"
    card_bg        = "#1E293B" if is_dark else "white"
    primary_text   = "white"   if is_dark else "#111827"
    secondary_text = "#CBD5E1" if is_dark else "#6B7280"
    divider_color  = "#334155" if is_dark else "#D1D5DB"
    field_bg       = "#334155" if is_dark else "#F1F5F9"

    role = (user_info or {}).get("role", "Advocate").lower()
    username = (user_info or {}).get("username", "")

    # ── Hearing table (dynamic, refreshable) ──────────────────────────────────
    hearing_table_col = ft.Column()

    def load_hearings():
        hearing_table_col.controls.clear()

        if role == "client":
            hearings = get_hearings_by_user(username)
        else:
            hearings = get_all_hearings()

        if not hearings:
            hearing_table_col.controls.append(
                ft.Text(t("No hearings scheduled"), color=secondary_text)
            )
            return

        hearing_table_col.controls.append(
            ft.DataTable(
                column_spacing=20,
                columns=[
                    ft.DataColumn(ft.Text(t("Case ID"),       color=primary_text, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("Date"),          color=primary_text, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("Court"),         color=primary_text, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("Judge Name"),    color=primary_text, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(t("Advocate Name"), color=primary_text, weight=ft.FontWeight.BOLD)),
                ],
                rows=[
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(h[0] or "—", color=primary_text, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(h[1] or "—", color=primary_text)),
                        ft.DataCell(ft.Text(h[2] or "—", color=secondary_text)),
                        ft.DataCell(ft.Text(h[3] or "—", color=_BLUE)),
                        ft.DataCell(ft.Text(h[4] or "—", color=_GREEN)),
                    ])
                    for h in hearings
                ],
            )
        )

    load_hearings()

    # ── Schedule Hearing form (advocate only) ─────────────────────────────────
    schedule_section = ft.Container()

    if role != "client":
        all_cases = get_all_cases()
        case_options = [
            ft.dropdown.Option(key=c[2], text=f"{c[2]} — {c[3]}")
            for c in all_cases
        ]

        case_dd = ft.Dropdown(
            label=t("Select Case"),
            options=case_options,
            width=340,
            border_color=_BLUE,
        )
        hearing_date_field = ft.TextField(
            label=t("Hearing Date (DD-MM-YYYY)"),
            width=340,
        )
        assigned_judge = random.choice(JUDGE_POOL)
        judge_field = ft.TextField(
            label=t("Judge Name (Auto-assigned)"),
            value=assigned_judge,
            width=340,
            read_only=True,
            bgcolor=field_bg,
        )

        def reroll_judge(e):
            judge_field.value = random.choice(JUDGE_POOL)
            if page:
                page.update()

        schedule_result = ft.Text("", color=_GREEN)

        def do_schedule(e):
            if not case_dd.value or not hearing_date_field.value:
                schedule_result.value = t("⚠ Please select a case and enter a date.")
                schedule_result.color = "#6B7A5E"
                if page:
                    page.update()
                return

            # get court from case
            court_val = "—"
            for c in all_cases:
                if c[2] == case_dd.value:
                    court_val = c[5] if len(c) > 5 else "—"
                    break

            create_hearing(
                case_dd.value,
                hearing_date_field.value,
                court_val,
                judge_field.value,
                username,
            )

            schedule_result.value = t("✔ Hearing scheduled successfully!")
            schedule_result.color = _GREEN
            hearing_date_field.value = ""
            judge_field.value = random.choice(JUDGE_POOL)
            load_hearings()
            if page:
                page.update()

        schedule_section = ft.Container(
            bgcolor=card_bg,
            padding=20,
            border_radius=12,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Text(t("Schedule Hearing"), size=18,
                            weight=ft.FontWeight.BOLD, color=primary_text),
                    ft.Divider(color=divider_color),
                    case_dd,
                    hearing_date_field,
                    ft.Row(spacing=10, controls=[
                        judge_field,
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip=t("Re-assign random judge"),
                            on_click=reroll_judge,
                        ),
                    ]),
                    ft.ElevatedButton(
                        t("Schedule Hearing"),
                        bgcolor=_BLUE,
                        color="white",
                        on_click=do_schedule,
                    ),
                    schedule_result,
                ]
            )
        )

    # ── Layout ─────────────────────────────────────────────────────────────────
    controls = [
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(t("Calendars & Hearings"), size=30,
                        weight=ft.FontWeight.BOLD, color=primary_text),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip=t("Refresh"),
                    icon_color=_SLATE,
                    on_click=lambda e: (load_hearings(), page.update()) if page else None,
                ),
            ]
        ),
        ft.Container(height=10),
    ]

    if role != "client":
        controls.append(schedule_section)
        controls.append(ft.Container(height=14))

    controls.append(
        ft.Container(
            bgcolor=card_bg,
            padding=20,
            border_radius=10,
            content=ft.Column(controls=[
                ft.Text(t("Upcoming Hearings"), size=20,
                        color=primary_text, weight=ft.FontWeight.BOLD),
                ft.Divider(color=divider_color),
                hearing_table_col,
            ]),
        )
    )

    return ft.Container(
        expand=True,
        padding=20,
        bgcolor=page_bg,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=controls,
        ),
    )
