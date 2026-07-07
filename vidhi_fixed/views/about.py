import flet as ft
from i18n import t


def about_view(page=None):

    is_dark       = page.theme_mode == ft.ThemeMode.DARK if page else False
    page_bg       = "#0F172A" if is_dark else "#F8FAFC"
    primary_text  = "white"   if is_dark else "#111827"
    divider_color = "#334155" if is_dark else "#D1D5DB"

    return ft.Container(
        expand=True,
        padding=20,
        bgcolor=page_bg,
        content=ft.Column(controls=[
            ft.Text(t("About VIDHI Legal AI"), size=30, weight=ft.FontWeight.BOLD, color=primary_text),
            ft.Divider(color=divider_color),
            ft.Text(t("VIDHI Legal AI is an AI-powered legal management platform."), color=primary_text),
            ft.Container(height=20),
            ft.Text(t("Technology Stack"), size=20, weight=ft.FontWeight.BOLD, color=primary_text),
            ft.Text(t("• Python"),  color=primary_text),
            ft.Text(t("• Flet"),    color=primary_text),
            ft.Text(t("• VS Code"), color=primary_text),
            ft.Container(height=20),
            ft.Text(t("Modules"), size=20, weight=ft.FontWeight.BOLD, color=primary_text),
            ft.Text(t("• Dashboard"),    color=primary_text),
            ft.Text(t("• Matters"),      color=primary_text),
            ft.Text(t("• Documents"),    color=primary_text),
            ft.Text(t("• AI Assistant"), color=primary_text),
            ft.Text(t("• Calendar"),     color=primary_text),
            ft.Text(t("• Billing"),      color=primary_text),
            ft.Text(t("• Contacts"),     color=primary_text),
            ft.Text(t("• Settings"),     color=primary_text),
            ft.Container(height=20),
            ft.Text(t("Version 1.0"), size=18, weight=ft.FontWeight.BOLD, color=primary_text),
            ft.Text(t("Developer: Rishi"), color=primary_text),
        ])
    )
