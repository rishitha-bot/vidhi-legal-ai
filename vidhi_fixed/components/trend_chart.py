import flet as ft
from i18n import t


def trend_bar_chart(
    data,
    value_key,
    label_key,
    max_value=100,
    min_value=0,
    bar_color="#4F83C2",
    suffix="%",
    height=260,
):
    chart_height = 140

    values = [item[value_key] for item in data]

    if not values:
        return ft.Container(
            height=height,
            content=ft.Text(t("No data available"))
        )

    actual_min = min(values)
    actual_max = max(values)

    span = max(actual_max - actual_min, 1)

    bars = []

    for item in data:
        value = item[value_key]

        normalized = (value - actual_min) / span

        # minimum visible height
        bar_height = 50 + (normalized * 70)

        bars.append(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                controls=[
                    ft.Text(
                        f"{value}{suffix}",
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color="#1E3A8A",
                    ),

                    ft.Container(
                        width=46,
                        height=bar_height,
                        bgcolor=bar_color,
                    ),

                    ft.Text(
                        str(item[label_key]),
                        size=12,
                        color="#6B7280",
                    ),
                ],
            )
        )

    return ft.Container(
        height=height,
        padding=10,
        content=ft.Column(
            controls=[
                ft.Divider(),

                ft.Row(
                    controls=bars,
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ),
            ]
        ),
    )