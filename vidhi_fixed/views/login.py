import flet as ft
import re
from i18n import t, is_telugu

from services.db import create_user, validate_user


def login_view(login_callback, back_to_home=None, translate_callback=None):

    contact_field = ft.TextField(
        label=t("Email ID / Phone Number"),
        width=400,
        color="white",
        label_style=ft.TextStyle(color="white70"),
        border_color="#38BDF8"
    )
    username_field = ft.TextField(
        label=t("Username"),
        width=400,
        color="white",
        label_style=ft.TextStyle(color="white70"),
        border_color="#38BDF8"
    )
    password_field = ft.TextField(
        label=t("Password"),
        password=True,
        can_reveal_password=True,
        width=400,
        color="white",
        label_style=ft.TextStyle(color="white70"),
        border_color="#38BDF8"
    )
    message = ft.Text(t(""), color="#F87171", size=14)

    def validate_inputs():
        contact  = contact_field.value.strip()
        username = username_field.value.strip()
        password = password_field.value.strip()
        phone_pat = r"^[6-9]\d{9}$"
        email_pat = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not contact or not username or not password:
            return False, t("Fill all fields")
        if not re.match(phone_pat, contact) and not re.match(email_pat, contact):
            return False, t("Enter valid Phone Number or Email")
        if len(username) < 4:
            return False, t("Username must be at least 4 characters")
        if len(password) < 6:
            return False, t("Password must be at least 6 characters")
        return True, ""

    def login_click(e):
        valid, msg = validate_inputs()
        if not valid:
            message.value = msg
            message.update()
            return
        user = validate_user(
            contact_field.value.strip(),
            username_field.value.strip(),
            password_field.value.strip()
        )
        if user:
            # Pass the typed username so navbar shows it
            login_callback(username_field.value.strip())
        else:
            message.value = t("Invalid Username or Password")
            message.update()

    def register_click(e):
        valid, msg = validate_inputs()
        if not valid:
            message.value = msg
            message.update()
            return
        success, msg = create_user(
            contact_field.value.strip(),
            username_field.value.strip(),
            password_field.value.strip()
        )
        if success:
            login_callback(username_field.value.strip())
        else:
            message.value = t(msg)
            message.update()

    return ft.Container(
        expand=True,
        bgcolor="#0F172A",
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=550,
                    bgcolor="#1E293B",
                    border_radius=20,
                    padding=40,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.TextButton(
                                        t("← Back to Home"),
                                        style=ft.ButtonStyle(color="#38BDF8"),
                                        on_click=back_to_home if back_to_home else None,
                                    ),
                                    ft.ElevatedButton(
                                        ("English" if is_telugu() else "తెలుగు (Telugu)"),
                                        icon=ft.Icons.TRANSLATE,
                                        bgcolor="#0F172A",
                                        color="white",
                                        on_click=translate_callback,
                                    ) if translate_callback else ft.Container(),
                                ]
                            ),
                            ft.Icon(ft.Icons.GAVEL, size=80, color="#38BDF8"),
                            ft.Text(t("VIDHI Legal AI"), size=34, weight=ft.FontWeight.BOLD, color="white"),
                            ft.Text(t("Login / Register"), size=20, color="white"),
                            ft.Container(height=10),
                            contact_field,
                            ft.Container(height=10),
                            username_field,
                            ft.Container(height=10),
                            password_field,
                            ft.Container(height=10),
                            message,
                            ft.Container(height=15),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.ElevatedButton(
                                        t("Login"),
                                        on_click=login_click,
                                        color="white",
                                        bgcolor="#38BDF8"
                                    ),
                                    ft.ElevatedButton(
                                        t("Create Account"),
                                        on_click=register_click,
                                        color="white",
                                        bgcolor="#2563EB"
                                    )
                                ]
                            ),
                            ft.Container(height=20),
                            ft.Text(t("AI-Powered Legal Intelligence Platform"), size=12, color="#94A3B8")
                        ]
                    )
                )
            ]
        )
    )
