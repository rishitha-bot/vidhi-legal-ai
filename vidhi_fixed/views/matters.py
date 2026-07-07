import flet as ft
from i18n import t

from components.cards import stat_card


def matters_view(page=None):

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
                ft.Text(t("Case Management"), size=30, weight=ft.FontWeight.BOLD, color=primary_text),

                ft.Row(controls=[
                    stat_card("Total Matters", 256),
                    stat_card("Active Cases",  148),
                    stat_card("Pending Cases",  52),
                    stat_card("Closed Cases",   56),
                ]),

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.TextField(width=500, hint_text=t("Search Cases...")),
                        ft.ElevatedButton(t("+ New Matter")),
                    ]
                ),

                ft.Container(
                    bgcolor=card_bg, padding=20, border_radius=10,
                    content=ft.Column(controls=[
                        ft.Text(t("All Matters"), size=20, color=primary_text, weight=ft.FontWeight.BOLD),

                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text(t("Case No"),  color=primary_text)),
                                ft.DataColumn(ft.Text(t("Client"),   color=primary_text)),
                                ft.DataColumn(ft.Text(t("Court"),    color=primary_text)),
                                ft.DataColumn(ft.Text(t("Status"),   color=primary_text)),
                                ft.DataColumn(ft.Text(t("Priority"), color=primary_text)),
                            ],
                            rows=[
                                ft.DataRow(cells=[
                                    ft.DataCell(ft.Text(t("VD001"),          color=primary_text)),
                                    ft.DataCell(ft.Text(t("State vs Kumar"), color=primary_text)),
                                    ft.DataCell(ft.Text(t("High Court"),     color=primary_text)),
                                    ft.DataCell(ft.Text(t("Active"),         color="green")),
                                    ft.DataCell(ft.Text(t("High"),           color="red")),
                                ]),
                                ft.DataRow(cells=[
                                    ft.DataCell(ft.Text(t("VD002"),             color=primary_text)),
                                    ft.DataCell(ft.Text(t("Property Dispute"),  color=primary_text)),
                                    ft.DataCell(ft.Text(t("District Court"),    color=primary_text)),
                                    ft.DataCell(ft.Text(t("Pending"),           color="orange")),
                                    ft.DataCell(ft.Text(t("Medium"),            color="blue")),
                                ]),
                                ft.DataRow(cells=[
                                    ft.DataCell(ft.Text(t("VD003"),            color=primary_text)),
                                    ft.DataCell(ft.Text(t("Contract Breach"),  color=primary_text)),
                                    ft.DataCell(ft.Text(t("Civil Court"),      color=primary_text)),
                                    ft.DataCell(ft.Text(t("Closed"),           color="red")),
                                    ft.DataCell(ft.Text(t("Low"),              color="green")),
                                ]),
                                ft.DataRow(cells=[
                                    ft.DataCell(ft.Text(t("VD004"),            color=primary_text)),
                                    ft.DataCell(ft.Text(t("Criminal Appeal"),  color=primary_text)),
                                    ft.DataCell(ft.Text(t("High Court"),       color=primary_text)),
                                    ft.DataCell(ft.Text(t("Active"),           color="green")),
                                    ft.DataCell(ft.Text(t("High"),             color="red")),
                                ]),
                            ]
                        )
                    ])
                ),

                ft.Container(
                    bgcolor=card_bg, padding=20, border_radius=10,
                    content=ft.Column(controls=[
                        ft.Text(t("Selected Matter"), size=20, color=primary_text, weight=ft.FontWeight.BOLD),
                        ft.Divider(color=divider_color),
                        ft.Text(t("Case Number: VD001"),        color=primary_text),
                        ft.Text(t("Client: State vs Kumar"),    color=primary_text),
                        ft.Text(t("Court: High Court"),         color=primary_text),
                        ft.Text(t("Next Hearing: 12 Jun 2026"), color=primary_text),
                        ft.Text(t("Priority: High"),            color="red"),
                    ])
                )
            ]
        )
    )
