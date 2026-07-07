import flet as ft
from i18n import t, is_telugu


def home_view(client_callback, advocate_callback, translate_callback=None):

    return ft.Container(
        expand=True,
        bgcolor="#051225",
        content=ft.Stack(
            controls=[

                # BACKGROUND
                ft.Container(
                    right=-300,
                    top=70,
                    opacity=0.40,
                    content=ft.Image(
                        src="background.png",
                        width=1800,
                        height=900,
                    ),
                ),

                # MAIN CONTENT
                ft.Column(
                    spacing=0,
                    controls=[

                        # NAVBAR
                        ft.Container(
                            height=90,
                            padding=20,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=12,
                                        controls=[
                                            ft.Image(src="logo.png", width=85, height=85),
                                            ft.Text(t("VIDHI LEGAL AI"), size=36, weight=ft.FontWeight.BOLD, color="white"),
                                        ],
                                    ),
                                    ft.Row(
                                        spacing=40,
                                        controls=[
                                            ft.Text(t("Case Management"), color="#CBD5E1", size=15),
                                            ft.Text(t("Document Intelligence"), color="#CBD5E1", size=15),
                                            ft.Text(t("Legal Research"), color="#CBD5E1", size=15),
                                            ft.ElevatedButton(
                                                ("English" if is_telugu() else "తెలుగు (Telugu)"),
                                                icon=ft.Icons.TRANSLATE,
                                                bgcolor="#1E293B",
                                                color="white",
                                                on_click=translate_callback,
                                            ) if translate_callback else ft.Container(),
                                        ],
                                    ),
                                ],
                            ),
                        ),

                        ft.Divider(height=1, color="#1E293B"),

                        # HERO
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[

                                    ft.Container(height=0),

                                    ft.Text(t("Smarter Legal Work,"), size=42, weight=ft.FontWeight.BOLD, color="white"),
                                    ft.Text(t("Powered by AI"), size=52, weight=ft.FontWeight.BOLD, color="#3B82F6"),

                                    ft.Container(height=8),

                                    ft.Text(t("Manage cases, analyze documents and conduct legal research"), size=17, color="#CBD5E1"),
                                    ft.Text(t("with intelligent tools built for legal professionals."), size=17, color="#CBD5E1"),

                                    ft.Container(height=5),

                                    # ROLE CARDS
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=100,
                                        controls=[

                                            # CLIENT CARD
                                            ft.Column(
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    ft.Container(
                                                        width=90, height=90,
                                                        bgcolor="#0F1F3D",
                                                        border_radius=45,
                                                        content=ft.Icon(ft.Icons.PERSON, size=50, color="#3B82F6"),
                                                    ),
                                                    ft.Container(height=4),
                                                    ft.Container(
                                                        width=270, height=160,
                                                        bgcolor="#11284D",
                                                        border_radius=20,
                                                        padding=20,
                                                        content=ft.Column(
                                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                            spacing=6,
                                                            controls=[
                                                                ft.Text(t("Client"), size=22, weight=ft.FontWeight.BOLD, color="white"),
                                                                ft.Text(t("Track your cases\nand updates"), text_align=ft.TextAlign.CENTER, size=13, color="#CBD5E1"),
                                                                ft.Container(expand=True),
                                                                ft.ElevatedButton(
                                                                    t("Continue  →"),
                                                                    width=180,
                                                                    bgcolor="#2563EB",
                                                                    color="white",
                                                                    on_click=client_callback,
                                                                ),
                                                            ],
                                                        ),
                                                    ),
                                                ],
                                            ),

                                            # ADVOCATE CARD
                                            ft.Column(
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    ft.Container(
                                                        width=90, height=90,
                                                        bgcolor="#241A45",
                                                        border_radius=45,
                                                        content=ft.Icon(ft.Icons.WORK, size=50, color="#8B5CF6"),
                                                    ),
                                                    ft.Container(height=5),
                                                    ft.Container(
                                                        width=270, height=160,
                                                        bgcolor="#1A1D4D",
                                                        border_radius=20,
                                                        padding=20,
                                                        content=ft.Column(
                                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                            spacing=6,
                                                            controls=[
                                                                ft.Text(t("Advocate"), size=22, weight=ft.FontWeight.BOLD, color="white"),
                                                                ft.Text(t("Manage clients\nand matters"), text_align=ft.TextAlign.CENTER, size=13, color="#CBD5E1"),
                                                                ft.Container(expand=True),
                                                                ft.ElevatedButton(
                                                                    t("Continue  →"),
                                                                    width=180,
                                                                    bgcolor="#7C3AED",
                                                                    color="white",
                                                                    on_click=advocate_callback,
                                                                ),
                                                            ],
                                                        ),
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )
