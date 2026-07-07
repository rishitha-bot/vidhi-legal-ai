import flet as ft


def stat_card(title, value, on_click=None):

    return ft.Container(
        width=220,
        height=130,
        bgcolor="white",
        border_radius=15,
        padding=20,
        ink=True,
        on_click=on_click,

        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=12,
            color="black12"
        ),

        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,

            controls=[

                ft.Text(
                    title,
                    size=16,
                    color="grey"
                ),

                ft.Text(
                    str(value),
                    size=34,
                    weight=ft.FontWeight.BOLD,
                    color="#2563EB"
                )
            ]
        )
    )