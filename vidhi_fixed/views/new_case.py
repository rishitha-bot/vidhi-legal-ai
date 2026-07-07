import flet as ft
import random
from i18n import t

from components.navbar import navbar
from services.db import create_case

_BLUE  = "#4A7FC1"
_SLATE = "#64748B"
_GREEN = "#4A8C6A"

ADVOCATES = [
    {"name": "Adv. Ramesh Iyer",   "specialisation": "Criminal Law",           "phone": "+91 98765 43210", "experience": "12 years", "rating": "4.8", "destination": "Chennai"},
    {"name": "Adv. Priya Nair",    "specialisation": "Property & Civil Law",   "phone": "+91 87654 32109", "experience": "9 years",  "rating": "4.6", "destination": "Noida"},
    {"name": "Adv. Suresh Menon",  "specialisation": "Family & Divorce Law",   "phone": "+91 76543 21098", "experience": "7 years",  "rating": "4.5", "destination": "Kochi"},
    {"name": "Adv. Kavitha Reddy", "specialisation": "Corporate & Contract Law","phone": "+91 65432 10987", "experience": "15 years", "rating": "4.9", "destination": "Hyderabad"},
    {"name": "Adv. Anil Sharma",   "specialisation": "Labour & Employment Law", "phone": "+91 54321 09876", "experience": "6 years",  "rating": "4.3", "destination": "Mumbai"},
]


def new_case_view(page, load_page=None, user_info=None, on_translate=None):

    is_dark        = page.theme_mode == ft.ThemeMode.DARK
    page_bg        = "#0F172A" if is_dark else "#F8FAFC"
    card_bg        = "#1E293B" if is_dark else "white"
    primary_text   = "white"   if is_dark else "#111827"
    secondary_text = "#CBD5E1" if is_dark else "#6B7280"
    divider_color  = "#334155" if is_dark else "#D1D5DB"
    card_unsel_bg  = "#334155" if is_dark else "#F1F5F9"
    card_border_un = "#475569" if is_dark else "#E2E8F0"

    selected_advocate = {"index": None}

    case_type = ft.TextField(label=t("Type of Case / Legal Issue"), width=500,
                             hint_text=t("e.g. Property dispute, Criminal case, Divorce..."))
    case_desc = ft.TextField(label=t("Brief Description"), width=500, multiline=True,
                             min_lines=3, max_lines=5,
                             hint_text=t("Describe your case in brief..."))
    urgency   = ft.Dropdown(
        label=t("Urgency"), width=500,
        options=[
            ft.dropdown.Option(key="Normal",     text=t("Normal")),
            ft.dropdown.Option(key="Urgent",     text=t("Urgent")),
            ft.dropdown.Option(key="Very Urgent",text=t("Very Urgent")),
        ],
        value="Normal"
    )

    advocate_cards = ft.Row(wrap=True, spacing=14, run_spacing=14)
    selected_label = ft.Text("", size=13, color=_SLATE)

    def build_advocate_cards():
        advocate_cards.controls.clear()
        for i, adv in enumerate(ADVOCATES):
            is_selected = selected_advocate["index"] == i

            def make_tap(idx):
                def on_tap(e):
                    selected_advocate["index"] = idx
                    selected_label.value = (
                        f"{t('Selected')}: {ADVOCATES[idx]['name']}  |  {ADVOCATES[idx]['phone']}"
                    )
                    build_advocate_cards()
                    page.update()
                return on_tap

            card = ft.GestureDetector(
                on_tap=make_tap(i),
                content=ft.Container(
                    width=220, padding=16, border_radius=12,
                    bgcolor=card_bg if is_selected else card_bg,
                    border=ft.Border.all(2, _BLUE if is_selected else card_border_un),
                    content=ft.Column(spacing=6, controls=[
                        ft.Text(adv["name"], size=14, weight=ft.FontWeight.BOLD, color=primary_text),
                        ft.Text(adv["specialisation"], size=12, color=_BLUE),
                        ft.Divider(height=6, color=divider_color),
                        ft.Row(spacing=6, controls=[
                            ft.Icon(ft.Icons.LOCATION_ON, size=13, color=_SLATE),
                            ft.Text(adv["destination"], size=12, color=secondary_text),
                        ]),
                        ft.Row(spacing=6, controls=[
                            ft.Icon(ft.Icons.PHONE, size=13, color=_SLATE),
                            ft.Text(adv["phone"], size=12, color=secondary_text),
                        ]),
                        ft.Row(spacing=6, controls=[
                            ft.Icon(ft.Icons.STAR, size=13, color="#B0B0B0"),
                            ft.Text(f"{adv['rating']}  ·  {adv['experience']}", size=12, color=secondary_text),
                        ]),
                        ft.Container(
                            margin=ft.Margin(top=6, bottom=0, left=0, right=0),
                            bgcolor=_BLUE if is_selected else card_unsel_bg,
                            border_radius=8,
                            padding=ft.Padding(top=6, bottom=6, left=0, right=0),
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(
                                t("Selected ✓") if is_selected else "Select",
                                size=12,
                                color="white" if is_selected else secondary_text,
                                weight=ft.FontWeight.BOLD,
                            )
                        )
                    ])
                )
            )
            advocate_cards.controls.append(card)

    build_advocate_cards()

    error_text = ft.Text("", color="red", size=12)

    def submit_case(e):
        if not case_type.value or not case_type.value.strip():
            error_text.value = t("Please enter the type of case.")
            page.update()
            return
        if selected_advocate["index"] is None:
            error_text.value = t("Please select an advocate.")
            page.update()
            return
        adv = ADVOCATES[selected_advocate["index"]]
        case_id = f"REQ-{random.randint(10000,99999)}"
        create_case(
            user_info["username"], case_id,
            user_info.get("username", "Client"),
            adv["name"], adv["destination"],
            "Pending Review",
            case_type=case_type.value.strip(),
            description=case_desc.value.strip() if case_desc.value else "",
            urgency=urgency.value or "",
        )
        user_info["case"] = {
            "case_type": case_type.value, "advocate": adv["name"],
            "phone": adv["phone"], "status": "Pending Review"
        }
        load_page("dashboard")

    return ft.Container(
        expand=True, bgcolor=page_bg, padding=24,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                navbar(user_info=user_info,
                       on_logout=(lambda e: load_page("home")) if load_page else None),
                ft.Container(height=10),
                ft.Text(t("Add Service Request"), size=24, weight=ft.FontWeight.BOLD, color=primary_text),
                ft.Text(t("Fill in your case details and choose an advocate."), size=13, color=secondary_text),
                ft.Container(height=10),
                ft.Container(
                    bgcolor=card_bg, border_radius=14, padding=24,
                    content=ft.Column(spacing=14, controls=[
                        ft.Text(t("Case Details"), size=16, weight=ft.FontWeight.BOLD, color=primary_text),
                        ft.Divider(color=divider_color),
                        case_type, case_desc, urgency,
                    ])
                ),
                ft.Container(height=14),
                ft.Container(
                    bgcolor=card_bg, border_radius=14, padding=24,
                    content=ft.Column(spacing=14, controls=[
                        ft.Text(t("Select an Advocate"), size=16, weight=ft.FontWeight.BOLD, color=primary_text),
                        ft.Text(t("Tap a card to select. You can see their location and contact number."),
                                size=12, color=secondary_text),
                        ft.Divider(color=divider_color),
                        advocate_cards,
                        selected_label,
                    ])
                ),
                ft.Container(height=14),
                error_text,
                ft.ElevatedButton(t("Submit Request"), bgcolor=_BLUE, color="white", on_click=submit_case, width=200),
                ft.Container(height=20),
            ]
        )
    )
