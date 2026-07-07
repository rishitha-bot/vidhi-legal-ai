import flet as ft

from services.db import init_db
from i18n import t, toggle_language, is_telugu
from views.home import home_view
from views.login import login_view
from views.dashboard import dashboard_view
from views.client_dashboard import client_dashboard_view
from views.new_case import new_case_view
from views.active_cases import active_cases_view          # original (all cases)
from views.active_cases_only import active_cases_only_view  # Box 1 — Active only
from views.service_requests import service_requests_view    # Box 2 — Pending requests
from views.hearings_this_week import hearings_this_week_view  # Box 3
from views.case_detail import case_detail_view
from views.matters import matters_view
from views.documents import documents_view
from views.assistant import assistant_view
from views.calendar import calendar_view
from views.billing import billing_view
from views.client_billing import client_billing_view
from views.client_documents import client_documents_view
from views.settings import settings_view


def main(page: ft.Page):
    page.title = "VIDHI Legal AI"
    page.window.width  = 1600
    page.window.height = 900
    page.theme_mode = ft.ThemeMode.LIGHT

    init_db()

    user_role = {"role": "advocate"}
    user_info = {"username": "", "role": "Advocate", "case": None}

    screen_state = {"name": "home", "page_name": "dashboard", "args": ()}

    content_area = ft.Container(expand=True)

    def go_home():
        screen_state["name"] = "home"
        page.controls.clear()
        page.add(
            home_view(
                open_client_login,
                open_advocate_login,
                translate_callback=toggle_translation
            )
        )
        page.update()

    def load_page(page_name, *args):
        if page_name == "home":
            go_home()
            return

        screen_state["name"]      = "dashboard"
        screen_state["page_name"] = page_name
        screen_state["args"]      = args

        if page_name == "dashboard":
            if user_role["role"] == "client":
                content_area.content = client_dashboard_view(
                    page, load_page, user_info=user_info, on_translate=toggle_translation
                )
            else:
                content_area.content = dashboard_view(
                    page, load_page, user_info=user_info, on_translate=toggle_translation
                )

        # ── Box 1: Active Cases ────────────────────────────────────────────
        elif page_name == "active_cases_only":
            content_area.content = active_cases_only_view(
                page, load_page,
                open_case_detail=lambda cid: open_case_detail(cid, from_page="active_cases_only"),
                user_info=user_info, on_translate=toggle_translation
            )

        # ── Box 2: Service Requests ───────────────────────────────────────
        elif page_name == "service_requests":
            content_area.content = service_requests_view(
                page, load_page, user_info=user_info, on_translate=toggle_translation
            )

        # ── Box 3: Hearings This Week ──────────────────────────────────────
        elif page_name == "hearings_this_week":
            content_area.content = hearings_this_week_view(
                page, load_page,
                open_case_detail=lambda cid: open_case_detail(cid, from_page="hearings_this_week"),
                user_info=user_info, on_translate=toggle_translation
            )

        # ── Legacy active_cases route (sidebar) ───────────────────────────
        elif page_name == "active_cases":
            content_area.content = active_cases_view(
                page, load_page,
                open_case_detail=lambda cid: open_case_detail(cid, from_page="active_cases"),
                user_info=user_info, on_translate=toggle_translation
            )

        elif page_name == "case_detail":
            case_id   = args[0] if args else None
            from_page = args[1] if len(args) > 1 else "active_cases_only"
            content_area.content = case_detail_view(
                page, load_page, case_id, user_info=user_info, from_page=from_page, on_translate=toggle_translation
            )

        elif page_name == "matters":
            content_area.content = matters_view(page=page)

        elif page_name == "documents":
            if user_role["role"] == "client":
                content_area.content = client_documents_view(
                    page, load_page, user_info=user_info
                )
            else:
                content_area.content = documents_view(
                    page, load_page, user_info=user_info
                )

        elif page_name == "assistant":
            content_area.content = assistant_view(page, load_page, user_info=user_info, on_translate=toggle_translation)

        elif page_name == "calendar":
            content_area.content = calendar_view(user_info=user_info, page=page)

        elif page_name == "new_case":
            content_area.content = new_case_view(page, load_page, user_info=user_info, on_translate=toggle_translation)

        elif page_name == "billing":
            if user_role["role"] == "client":
                content_area.content = client_billing_view(
                    page, load_page, user_info=user_info
                )
            else:
                content_area.content = billing_view(page=page, load_page=load_page)

        elif page_name == "settings":
            content_area.content = settings_view(page)

        page.update()

    def open_case_detail(case_id, from_page="active_cases_only"):
        load_page("case_detail", case_id, from_page)

    def rebuild_current_screen():
        if screen_state["name"] == "home":
            go_home()
        elif screen_state["name"] == "login":
            if user_role["role"] == "client":
                open_client_login(None)
            else:
                open_advocate_login(None)
        else:
            load_page(screen_state["page_name"], *screen_state["args"])
            page.controls.clear()
            page.add(
                ft.Row(expand=True, controls=[build_sidebar(), content_area])
            )
            page.update()

    def toggle_translation(e=None):
        toggle_language()
        rebuild_current_screen()

    def build_sidebar():
        items = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DASHBOARD, color="white"),
                title=ft.Text(t("Dashboard"), color="white"),
                on_click=lambda e: load_page("dashboard")
            )
        ]

        if user_role["role"] == "advocate":
            items.extend([
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.GAVEL, color="white"),
                    title=ft.Text(t("Active Matters"), color="white"),
                    on_click=lambda e: load_page("active_cases")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DESCRIPTION, color="white"),
                    title=ft.Text(t("Documents"), color="white"),
                    on_click=lambda e: load_page("documents")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SMART_TOY, color="white"),
                    title=ft.Text(t("AI Assistant"), color="white"),
                    on_click=lambda e: load_page("assistant")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.CALENDAR_MONTH, color="white"),
                    title=ft.Text(t("Calendars & Hearings"), color="white"),
                    on_click=lambda e: load_page("calendar")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PAYMENTS, color="white"),
                    title=ft.Text(t("Billing"), color="white"),
                    on_click=lambda e: load_page("billing")
                ),
            ])
        else:
            items.extend([
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PAYMENTS, color="white"),
                    title=ft.Text(t("Billing & Payments"), color="white"),
                    on_click=lambda e: load_page("billing")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.FOLDER_COPY, color="white"),
                    title=ft.Text(t("Documentation"), color="white"),
                    on_click=lambda e: load_page("documents")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SMART_TOY, color="white"),
                    title=ft.Text(t("AI Assistant"), color="white"),
                    on_click=lambda e: load_page("assistant")
                ),
            ])

        items.extend([
            ft.ListTile(
                leading=ft.Icon(ft.Icons.SETTINGS, color="white"),
                title=ft.Text(t("Settings"), color="white"),
                on_click=lambda e: load_page("settings")
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOGOUT, color="#F87171"),
                title=ft.Text(t("Logout"), color="#F87171"),
                on_click=lambda e: go_home()
            )
        ])

        return ft.Container(
            width=240,
            bgcolor="#1E293B",
            padding=20,
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Image(src="logo.png", width=38, height=38),
                            ft.Column(
                                spacing=0,
                                controls=[
                                    ft.Text(t("VIDHI"), size=22, color="white",
                                            weight=ft.FontWeight.BOLD),
                                    ft.Text(t("Legal AI Platform"), color="white70", size=11),
                                ]
                            ),
                        ],
                    ),
                    ft.Divider(),
                    *items
                ]
            ),
        )

    def open_dashboard():
        load_page("dashboard")
        page.controls.clear()
        page.add(ft.Row(expand=True, controls=[build_sidebar(), content_area]))
        page.update()

    def login_success(username):
        user_info["username"] = username
        open_dashboard()

    def open_client_login(e):
        user_role["role"]  = "client"
        user_info["role"]  = "Client"
        screen_state["name"] = "login"
        page.controls.clear()
        page.add(
            login_view(
                login_success,
                back_to_home=lambda e: go_home(),
                translate_callback=toggle_translation
            )
        )
        page.update()

    def open_advocate_login(e):
        user_role["role"]  = "advocate"
        user_info["role"]  = "Advocate"
        screen_state["name"] = "login"
        page.controls.clear()
        page.add(
            login_view(
                login_success,
                back_to_home=lambda e: go_home(),
                translate_callback=toggle_translation
            )
        )
        page.update()

    page.add(
        home_view(
            open_client_login,
            open_advocate_login,
            translate_callback=toggle_translation
        )
    )


ft.run(main, assets_dir="assets")
