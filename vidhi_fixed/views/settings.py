import flet as ft
from i18n import t


def settings_view(page: ft.Page):

    def change_theme(e):
        if e.control.value:
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
        page.update()

    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[

                ft.Text(t("Settings"), size=30, weight=ft.FontWeight.BOLD),
                ft.Divider(),

                ft.Switch(label=t("Dark Mode"),          on_change=change_theme),
                ft.Switch(label=t("Notifications")),
                ft.Switch(label=t("Email Alerts")),
                ft.Switch(label=t("Automatic Backup")),
                ft.Switch(label=t("AI Recommendations")),

                ft.Container(height=20),

                

                ft.Container(height=20),

                ft.ElevatedButton(t("Save Settings")),
            ]
        )
    )
