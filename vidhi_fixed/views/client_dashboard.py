import flet as ft
from i18n import t, is_telugu
from components.navbar import navbar
from services.db import (
    get_cases_by_user,
    get_hearings_by_user,
    get_case_by_id,
    delete_case_by_id,
    get_documents,
)


def client_dashboard_view(page, load_page=None, user_info=None, on_translate=None):

    is_dark = page.theme_mode == ft.ThemeMode.DARK

    page_bg = "#0F172A" if is_dark else "#F8FAFC"
    card_bg = "#1E293B" if is_dark else "white"
    primary_text = "white" if is_dark else "#111827"
    secondary_text = "#CBD5E1" if is_dark else "#6B7280"
    divider_color = "#334155" if is_dark else "#D1D5DB"
    desc_bg = "#334155" if is_dark else "#F3F4F6"

    active_count_text = ft.Text(
        "0",
        size=48,
        color="#3B82F6",
        weight=ft.FontWeight.BOLD
    )

    status_text = ft.Text(
        t("No Cases"),
        size=16,
        color=secondary_text
    )

    active_cases_list = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        height=350
    )

    def close_active_cases(e=None):
        active_cases_dialog.open = False
        page.update()

    active_cases_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(t("Active Cases")),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    on_click=close_active_cases,
                    tooltip=t("Close"),
                )
            ]
        ),
        content=ft.Container(
            width=600,
            content=active_cases_list
        ),
        actions=[
            ft.TextButton(t("Close"), on_click=close_active_cases)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_active_cases(e=None):
        active_cases_list.controls.clear()
        cases = get_cases_by_user(user_info["username"])

        for c in cases:
            cid = c[0]
            docs = get_documents(cid)

            active_cases_list.controls.append(
                ft.Card(
                    content=ft.ListTile(
                        title=ft.Text(cid, color=primary_text),
                        subtitle=ft.Text(
                            f"{t('Documents')}: {len(docs)}",
                            color=secondary_text
                        ),
                        on_click=lambda e, cc=cid: open_case_dialog(cc)
                    )
                )
            )

        if active_cases_dialog not in page.overlay:
            page.overlay.append(active_cases_dialog)
        active_cases_dialog.open = True
        page.update()

    dlg_case_id = ft.Text("", size=18, weight=ft.FontWeight.BOLD)
    dlg_status = ft.Text("")
    dlg_advocate = ft.Text("")
    dlg_court = ft.Text("")
    dlg_case_type = ft.Text("")
    dlg_urgency = ft.Text("")
    dlg_desc = ft.Text("")

    def close_case_dialog(e=None):
        case_detail_dialog.open = False
        page.update()

    case_detail_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    t("Case Details"),
                    weight=ft.FontWeight.BOLD
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    on_click=close_case_dialog,
                    tooltip=t("Close"),
                )
            ]
        ),
        content=ft.Container(
            width=420,
            content=ft.Column(
                controls=[
                    dlg_case_id,
                    ft.Divider(color=divider_color),
                    ft.Row([ft.Text(t("Status:"), width=120), dlg_status]),
                    ft.Row([ft.Text(t("Advocate:"), width=120), dlg_advocate]),
                    ft.Row([ft.Text(t("Court:"), width=120), dlg_court]),
                    ft.Row([ft.Text(t("Case Type:"), width=120), dlg_case_type]),
                    ft.Row([ft.Text(t("Urgency:"), width=120), dlg_urgency]),
                    ft.Text(
                        t("Description:"),
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(
                        bgcolor=desc_bg,
                        padding=10,
                        border_radius=8,
                        content=dlg_desc
                    )
                ]
            )
        ),
        actions=[
            ft.TextButton(t("Close"), on_click=close_case_dialog)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_case_dialog(case_id):
        case = get_case_by_id(case_id)

        if not case:
            return

        dlg_case_id.value = f"{t('Case ID')}: {case[2]}"
        dlg_status.value = case[6]
        dlg_advocate.value = case[4] or "-"
        dlg_court.value = case[5] or "-"
        dlg_case_type.value = case[7] or "-"
        dlg_urgency.value = case[9] or "-"
        dlg_desc.value = case[8] or "No description"

        if case_detail_dialog not in page.overlay:
            page.overlay.append(case_detail_dialog)
        case_detail_dialog.open = True
        page.update()

    current_status_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text(t("Case ID"), color=primary_text)),
            ft.DataColumn(ft.Text(t("Client Name"), color=primary_text)),
            ft.DataColumn(ft.Text(t("Advocate"), color=primary_text)),
            ft.DataColumn(ft.Text(t("Status"), color=primary_text)),
            ft.DataColumn(ft.Text(t("Action"), color=primary_text)),
        ],
        rows=[]
    )

    hearing_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text(t("Case ID"), color=primary_text)),
            ft.DataColumn(ft.Text(t("Hearing Date"), color=primary_text)),
            ft.DataColumn(ft.Text(t("Court"), color=primary_text)),
            ft.DataColumn(ft.Text(t("Judge Name"), color=primary_text)),
            ft.DataColumn(ft.Text(t("Advocate Name"), color=primary_text)),
        ],
        rows=[]
    )

    def refresh_dashboard():
        cases = get_cases_by_user(user_info["username"])

        active_count_text.value = str(len(cases))

        if cases:
            status_text.value = f"{len(cases)} Service Request(s)"
        else:
            status_text.value = t("No Cases")

        current_status_table.rows.clear()

        for case in cases:
            case_id = case[0]
            client_name = case[1]
            advocate_name = case[2]
            status = case[3]

            current_status_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.TextButton(
                                case_id,
                                on_click=lambda e, cid=case_id: open_case_dialog(cid)
                            )
                        ),
                        ft.DataCell(ft.Text(client_name, color=primary_text)),
                        ft.DataCell(ft.Text(advocate_name, color=primary_text)),
                        ft.DataCell(ft.Text(status, color=primary_text)),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                on_click=lambda e: delete_case_by_id(case_id, user_info["username"])
                            )
                        )
                    ]
                )
            )

        hearing_table.rows.clear()

        hearings = get_hearings_by_user(user_info["username"])

        for hearing in hearings:
            hearing_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(hearing[0], color=primary_text)),
                        ft.DataCell(ft.Text(hearing[1], color=primary_text)),
                        ft.DataCell(ft.Text(hearing[2], color=primary_text)),
                        ft.DataCell(ft.Text(hearing[3] or "-", color=primary_text)),
                        ft.DataCell(ft.Text(hearing[4] or "-", color=primary_text)),
                    ]
                )
            )

        page.update()

    refresh_dashboard()

    return ft.Container(
        expand=True,
        padding=20,
        bgcolor=page_bg,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                navbar(
                    user_info=user_info,
                    on_logout=(lambda e: load_page("home")) if load_page else None,
                    on_translate=on_translate,
                ),

                ft.Row(
                    spacing=20,
                    controls=[
                        ft.GestureDetector(
                            on_tap=open_active_cases,
                            content=ft.Container(
                                expand=1,
                                bgcolor=card_bg,
                                border_radius=15,
                                padding=25,
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(
                                            t("Active Service Requests"),
                                            size=22,
                                            weight=ft.FontWeight.BOLD,
                                            color=primary_text
                                        ),
                                        active_count_text,
                                        status_text
                                    ]
                                )
                            )
                        ),

                        ft.Container(
                            expand=1,
                            bgcolor=card_bg,
                            border_radius=15,
                            padding=25,
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        t("Quick Actions"),
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=primary_text
                                    ),
                                    ft.ElevatedButton(
                                        t("Add Service Request"),
                                        on_click=lambda e: load_page("new_case")
                                    )
                                ]
                            )
                        )
                    ]
                ),

                ft.Container(
                    bgcolor=card_bg,
                    border_radius=15,
                    padding=20,
                    margin=10,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                t("My Current Status"),
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=primary_text
                            ),
                            ft.Divider(color=divider_color),
                            current_status_table
                        ]
                    )
                ),

                ft.Container(
                    bgcolor=card_bg,
                    border_radius=15,
                    padding=20,
                    margin=10,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                t("Upcoming Hearings"),
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=primary_text
                            ),
                            ft.Divider(color=divider_color),
                            hearing_table
                        ]
                    )
                ),

                ft.Container(
                    padding=20,
                    content=ft.Text(
                        t("VIDHI Legal AI © 2026"),
                        size=14,
                        color=secondary_text
                    )
                )
            ]
        )
    )