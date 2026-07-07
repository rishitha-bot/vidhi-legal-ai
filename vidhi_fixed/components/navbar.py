import flet as ft
from datetime import datetime

from i18n import t, is_telugu


def navbar(user_info=None, on_logout=None, on_translate=None):
    today    = datetime.now().strftime("%d %b %Y")
    username = (user_info or {}).get("username", "User")
    role     = t((user_info or {}).get("role", "Advocate"))

    # Language toggle button — shows current language, click to switch
    lang_label = ft.Text(
        "EN | తె" if not is_telugu() else "తె | EN",
        size=12,
        weight=ft.FontWeight.BOLD,
        color="#4A7FC1",
    )

    def handle_translate(e):
        if on_translate:
            on_translate(e)

    translate_btn = ft.Container(
        border=ft.Border.all(1.5, "#4A7FC1"),
        border_radius=8,
        padding=ft.Padding(left=10, right=10, top=6, bottom=6),
        tooltip="Translate to Telugu / ఆంగ్లంలోకి మార్చండి",
        on_click=handle_translate,
        content=ft.Row(
            spacing=6,
            controls=[
                ft.Icon(ft.Icons.TRANSLATE, color="#4A7FC1", size=16),
                lang_label,
            ]
        )
    )

    def handle_logout(e):
        if on_logout:
            on_logout(e)

    profile_popup = ft.PopupMenuButton(
        content=ft.Container(
            width=40, height=40,
            bgcolor="#4A7FC1",
            border_radius=20,
            alignment=ft.Alignment(0, 0),
            content=ft.Icon(ft.Icons.PERSON, color="white", size=22),
            tooltip=t("Profile"),
        ),
        items=[
            ft.PopupMenuItem(
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(username, weight=ft.FontWeight.BOLD,
                                color="black", size=14),
                        ft.Text(f"{t('Logged in as ')}{role}", color="grey", size=12),
                    ]
                ),
            ),
            ft.PopupMenuItem(),  # divider
            ft.PopupMenuItem(
                content=ft.Row(spacing=8, controls=[
                    ft.Icon(ft.Icons.LOGOUT, color="#64748B", size=18),
                    ft.Text(t("Logout"), color="#64748B", size=14),
                ]),
                on_click=handle_logout,
            ),
        ]
    )

    return ft.Container(
        bgcolor="white",
        padding=ft.Padding(top=14, bottom=14, left=20, right=20),
        border_radius=15,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(t("VIDHI Legal AI"), size=16,
                        weight=ft.FontWeight.BOLD, color="#1E293B"),
                ft.Row(
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        # ── Translation toggle ──
                        translate_btn,

                        # ── Date ──
                        ft.Column(
                            spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                            controls=[
                                ft.Text(t("Today"), size=11, color="grey"),
                                ft.Text(today, size=14,
                                        weight=ft.FontWeight.BOLD, color="black"),
                            ]
                        ),

                        # ── Username / role ──
                        ft.Column(
                            spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                            controls=[
                                ft.Text(username, size=14,
                                        weight=ft.FontWeight.BOLD, color="black"),
                                ft.Text(role, size=11, color="grey"),
                            ]
                        ),

                        profile_popup,
                    ]
                )
            ]
        )
    )
