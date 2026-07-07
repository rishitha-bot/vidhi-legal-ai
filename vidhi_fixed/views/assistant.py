import flet as ft
from components.navbar import navbar
from services.db import get_hearings_by_user, get_cases_by_user


def assistant_view(page=None, load_page=None, user_info=None, on_translate=None):

    is_dark = page.theme_mode == ft.ThemeMode.DARK

    page_bg = "#0F172A" if is_dark else "#F8FAFC"
    card_bg = "#1E293B" if is_dark else "white"
    primary_text = "white" if is_dark else "#111827"
    secondary_text = "#CBD5E1" if is_dark else "#6B7280"

    prompt = ft.TextField(
        label="Ask legal AI",
        multiline=True,
        min_lines=4,
        color=primary_text,
        border_color="#3B82F6"
    )

    output = ft.Text(
        "No query yet",
        selectable=True,
        color=primary_text
    )

    def run_ai(e):
        query = prompt.value.lower().strip() if prompt.value else ""

        if "hearing" in query:
            hearings = get_hearings_by_user(user_info["username"])

            if hearings:
                result = "Upcoming Hearings:\n\n"
                for h in hearings:
                    result += f"• Case ID: {h[0]}\n"
                    result += f"  Date: {h[1]}\n"
                    result += f"  Court: {h[2]}\n\n"
                output.value = result
            else:
                output.value = "No upcoming hearings found."

        elif "case" in query:
            cases = get_cases_by_user(user_info["username"])

            if cases:
                result = "Your Active Cases:\n\n"
                for c in cases:
                    result += f"• {c[0]} - {c[3]}\n"
                output.value = result
            else:
                output.value = "No active cases found."

        elif "document" in query:
            output.value = (
                "Document Intelligence:\n\n"
                "• Missing documents detection coming soon\n"
                "• Document summary coming soon\n"
                "• Auto categorization coming soon"
            )

        elif "payment" in query:
            output.value = (
                "Payment Intelligence:\n\n"
                "• Court Fee status\n"
                "• Advocate Fee status\n"
                "• General Fee status"
            )

        else:
            output.value = (
                "I can help with:\n\n"
                "• Show upcoming hearings\n"
                "• Show active cases\n"
                "• Document analysis\n"
                "• Payment details\n"
                "• Legal deadlines"
            )

        if page:
            page.update()

    return ft.Container(
        expand=True,
        padding=20,
        bgcolor=page_bg,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                navbar(
                    user_info=user_info,
                    on_logout=(
                        lambda e: load_page("home")
                    ) if load_page else None,
                    on_translate=on_translate
                ),

                ft.Text(
                    "AI Legal Workspace",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=primary_text
                ),

                ft.Text(
                    "Ask anything about your cases, hearings, documents or payments",
                    size=14,
                    color=secondary_text
                ),

                prompt,

                ft.ElevatedButton(
                    "Analyze",
                    on_click=run_ai
                ),

                ft.Container(
                    bgcolor=card_bg,
                    padding=15,
                    border_radius=10,
                    content=output
                )
            ]
        )
    )