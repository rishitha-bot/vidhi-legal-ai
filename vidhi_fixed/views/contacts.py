import flet as ft
from i18n import t

from components.cards import stat_card


def contacts_view(page=None):

    is_dark        = page.theme_mode == ft.ThemeMode.DARK if page else False
    page_bg        = "#0F172A" if is_dark else "#F8FAFC"
    card_bg        = "#1E293B" if is_dark else "white"
    primary_text   = "white"   if is_dark else "#111827"
    secondary_text = "#CBD5E1" if is_dark else "#6B7280"
    divider_color  = "#334155" if is_dark else "#D1D5DB"

    return ft.Container(
        expand=True,
        padding=20,
        bgcolor=page_bg,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text(t("Contacts"), size=30, weight=ft.FontWeight.BOLD, color=primary_text),

                ft.Row(controls=[
                    stat_card("Clients",   87),
                    stat_card("Advocates", 24),
                    stat_card("Courts",    12),
                    stat_card("Partners",  8),
                ]),

                ft.Container(
                    bgcolor=card_bg,
                    padding=20,
                    border_radius=10,
                    content=ft.Column(controls=[
                        ft.Text(t("Contact Directory"), size=20, color=primary_text, weight=ft.FontWeight.BOLD),

                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON),
                            title=ft.Text(t("Ramesh Kumar"), color=primary_text),
                            subtitle=ft.Text(t("Client"), color=secondary_text),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON),
                            title=ft.Text(t("Adv. Sharma"), color=primary_text),
                            subtitle=ft.Text(t("Senior Advocate"), color=secondary_text),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.PERSON),
                            title=ft.Text(t("Anjali Rao"), color=primary_text),
                            subtitle=ft.Text(t("Legal Consultant"), color=secondary_text),
                        ),
                    ])
                )
            ]
        )
    )
