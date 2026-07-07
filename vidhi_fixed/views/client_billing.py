import flet as ft
from datetime import datetime
from i18n import t

from components.navbar import navbar
from services.db import (
    get_payments_by_user,
    update_payment_status,
    get_cases_by_user,
)

_BLUE  = "#4A7FC1"
_SLATE = "#64748B"
_GREEN = "#4A8C6A"
_RED   = "#DC2626"
_AMBER = "#B07D3A"

PAYMENT_METHODS = [
    {"key": "Cash",        "label": "Cash",        "icon": ft.Icons.PAYMENTS,      "color": _AMBER},
    {"key": "UPI",         "label": "UPI",         "icon": ft.Icons.PHONE_ANDROID, "color": _BLUE},
    {"key": "Credit Card", "label": "Credit Card", "icon": ft.Icons.CREDIT_CARD,   "color": _GREEN},
    {"key": "Debit Card",  "label": "Debit Card",  "icon": ft.Icons.CREDIT_CARD,   "color": _SLATE},
]


def client_billing_view(page=None, load_page=None, user_info=None):
    username = user_info["username"] if user_info else ""

    is_dark        = page.theme_mode == ft.ThemeMode.DARK if page else False
    page_bg        = "#0F172A" if is_dark else "#F8FAFC"
    card_bg        = "#1E293B" if is_dark else "white"
    primary_text   = "white"   if is_dark else "#111827"
    secondary_text = "#CBD5E1" if is_dark else "#6B7280"
    divider_color  = "#334155" if is_dark else "#D1D5DB"
    input_bg       = "#0F172A" if is_dark else "#F1F5F9"
    receipt_bg     = "#0D1F0D" if is_dark else "#F0FDF4"

    # ── State ──────────────────────────────────────────────────────────────────
    selected_method   = {"value": None}
    selected_payments = {"ids": [], "case_id": "", "total": 0.0, "rows": []}

    # ── Dialog widgets ─────────────────────────────────────────────────────────
    dlg_case_label   = ft.Text("", size=13, color=secondary_text)
    dlg_fee_rows     = ft.Column(spacing=6, tight=True)
    dlg_total_text   = ft.Text("", size=20, weight=ft.FontWeight.BOLD, color=_BLUE)
    dlg_result       = ft.Text("", color=_GREEN, size=13)
    method_btn_refs  = {}   # key → ElevatedButton

    # ── Receipt section (shown after successful payment) ───────────────────────
    receipt_section = ft.Container(visible=False)

    def _build_receipt(method, case_id, fee_rows, total):
        now = datetime.now().strftime("%d %b %Y, %I:%M %p")
        txn_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"

        fee_icons = {
            "Court Fee":    (ft.Icons.GAVEL,        _BLUE),
            "Advocate Fee": (ft.Icons.PERSON,        _GREEN),
            "General Fee":  (ft.Icons.RECEIPT_LONG,  _AMBER),
        }

        fee_lines = []
        for pid, fee_type, amount in fee_rows:
            icon, color = fee_icons.get(fee_type, (ft.Icons.MONEY, _SLATE))
            fee_lines.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(spacing=6, controls=[
                            ft.Icon(icon, size=13, color=color),
                            ft.Text(t(fee_type), size=12, color=primary_text),
                        ]),
                        ft.Text(f"₹ {amount:,.0f}", size=12,
                                color=primary_text, weight=ft.FontWeight.BOLD),
                    ],
                )
            )

        return ft.Container(
            visible=True,
            bgcolor=receipt_bg,
            border_radius=10,
            padding=ft.Padding(top=14, bottom=14, left=16, right=16),
            border=ft.Border(
                left=ft.BorderSide(3, _GREEN),
                right=ft.BorderSide(1, _GREEN + "44"),
                top=ft.BorderSide(1, _GREEN + "44"),
                bottom=ft.BorderSide(1, _GREEN + "44"),
            ),
            content=ft.Column(
                spacing=8,
                controls=[
                    # Receipt header
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(spacing=6, controls=[
                                ft.Icon(ft.Icons.RECEIPT_LONG, size=16, color=_GREEN),
                                ft.Text(t("Payment Receipt"), size=13,
                                        weight=ft.FontWeight.BOLD, color=_GREEN),
                            ]),
                            ft.Container(
                                bgcolor=_GREEN + "22",
                                border_radius=6,
                                padding=ft.Padding(top=2, bottom=2, left=8, right=8),
                                content=ft.Text(t("PAID"), size=11, color=_GREEN,
                                                weight=ft.FontWeight.BOLD),
                            ),
                        ],
                    ),
                    ft.Divider(color=_GREEN + "33", height=1),
                    # Meta info
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=2, controls=[
                                ft.Text(t("Transaction ID"), size=10, color=secondary_text),
                                ft.Text(txn_id, size=11, color=primary_text,
                                        weight=ft.FontWeight.BOLD),
                            ]),
                            ft.Column(spacing=2,
                                      horizontal_alignment=ft.CrossAxisAlignment.END,
                                      controls=[
                                ft.Text(t("Date & Time"), size=10, color=secondary_text),
                                ft.Text(now, size=11, color=primary_text),
                            ]),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=2, controls=[
                                ft.Text(t("Case ID"), size=10, color=secondary_text),
                                ft.Text(case_id, size=11, color=primary_text),
                            ]),
                            ft.Column(spacing=2,
                                      horizontal_alignment=ft.CrossAxisAlignment.END,
                                      controls=[
                                ft.Text(t("Payment Method"), size=10, color=secondary_text),
                                ft.Text(method, size=11, color=primary_text),
                            ]),
                        ],
                    ),
                    ft.Divider(color=_GREEN + "33", height=1),
                    # Fee breakdown
                    *fee_lines,
                    ft.Divider(color=_GREEN + "33", height=1),
                    # Total
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(t("Total Paid"), size=13,
                                    weight=ft.FontWeight.BOLD, color=primary_text),
                            ft.Text(f"₹ {total:,.0f}", size=15,
                                    weight=ft.FontWeight.BOLD, color=_GREEN),
                        ],
                    ),
                ],
            ),
        )

    def _build_failed_section(method, case_id):
        return ft.Container(
            visible=True,
            bgcolor="#2D0A0A" if is_dark else "#FEF2F2",
            border_radius=10,
            padding=ft.Padding(top=14, bottom=14, left=16, right=16),
            border=ft.Border(
                left=ft.BorderSide(3, _RED),
                right=ft.BorderSide(1, _RED + "44"),
                top=ft.BorderSide(1, _RED + "44"),
                bottom=ft.BorderSide(1, _RED + "44"),
            ),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(spacing=8, controls=[
                        ft.Icon(ft.Icons.CANCEL, size=20, color=_RED),
                        ft.Text(t("Payment Failed"), size=14,
                                weight=ft.FontWeight.BOLD, color=_RED),
                    ]),
                    ft.Text(
                        t("Your payment could not be processed. Please try again or choose a different payment method."),
                        size=12, color=_RED, italic=True,
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=2, controls=[
                                ft.Text(t("Case ID"), size=10, color=secondary_text),
                                ft.Text(case_id, size=11, color=primary_text),
                            ]),
                            ft.Column(spacing=2,
                                      horizontal_alignment=ft.CrossAxisAlignment.END,
                                      controls=[
                                ft.Text(t("Attempted Method"), size=10, color=secondary_text),
                                ft.Text(method, size=11, color=primary_text),
                            ]),
                        ],
                    ),
                ],
            ),
        )

    def _make_method_btn(m):
        key   = m["key"]
        icon  = m["icon"]
        label = m["label"]
        color = m["color"]

        def on_click(e, k=key):
            selected_method["value"] = k
            for mk, mb in method_btn_refs.items():
                mb.bgcolor = _BLUE if mk == k else (("#334155" if is_dark else "#E2E8F0"))
                mb.color   = "white" if mk == k else secondary_text
                mb.style   = ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    side=ft.BorderSide(2, _BLUE if mk == k else "transparent"),
                )
            dlg_result.value = ""
            receipt_section.visible = False
            receipt_section.content = None
            page.update()

        btn = ft.ElevatedButton(
            content=ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(icon, size=16, color="white" if selected_method["value"] == key else secondary_text),
                    ft.Text(label, size=13),
                ],
            ),
            bgcolor="#334155" if is_dark else "#E2E8F0",
            color=secondary_text,
            on_click=on_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(2, "transparent"),
            ),
        )
        method_btn_refs[key] = btn
        return btn

    method_buttons_row = ft.Row(
        spacing=8,
        wrap=True,
        controls=[_make_method_btn(m) for m in PAYMENT_METHODS],
    )

    # ── Payment status banner (shown above receipt) ────────────────────────────
    payment_status_banner = ft.Container(visible=False)

    def confirm_payment(e):
        meth = selected_method["value"]
        if not meth:
            dlg_result.value = t("⚠ Please select a payment method.")
            dlg_result.color = _AMBER
            receipt_section.visible = False
            page.update()
            return

        pids = selected_payments["ids"]
        if not pids:
            return

        case_id   = selected_payments["case_id"]
        total     = selected_payments["total"]
        fee_rows  = selected_payments["rows"]

        # Simulate payment processing
        payment_success = True   # Always succeeds for online; Cash is "pending"

        if meth == "Cash":
            # Cash → pending confirmation
            new_status = "Pending Confirmation"
            for pid in pids:
                update_payment_status(pid, new_status, method=meth)

            # Show amber status banner
            payment_status_banner.visible = True
            payment_status_banner.bgcolor = "#1C1200" if is_dark else "#FFFBEB"
            payment_status_banner.border_radius = 8
            payment_status_banner.padding = ft.Padding(top=10, bottom=10, left=14, right=14)
            payment_status_banner.border = ft.Border(
                left=ft.BorderSide(3, _AMBER),
                right=ft.BorderSide(1, _AMBER + "44"),
                top=ft.BorderSide(1, _AMBER + "44"),
                bottom=ft.BorderSide(1, _AMBER + "44"),
            )
            payment_status_banner.content = ft.Row(spacing=10, controls=[
                ft.Icon(ft.Icons.HOURGLASS_EMPTY, size=18, color=_AMBER),
                ft.Text(
                    t("Cash payment recorded. Awaiting advocate confirmation."),
                    size=12, color=_AMBER, weight=ft.FontWeight.BOLD,
                ),
            ])

            # No full receipt for cash — just pending note
            receipt_section.visible = False
            receipt_section.content = None

        elif payment_success:
            # Online payment succeeded
            new_status = "Paid"
            for pid in pids:
                update_payment_status(pid, new_status, method=meth)

            # ── Payment Done banner ────────────────────────────────────────────
            payment_status_banner.visible = True
            payment_status_banner.bgcolor = "#0D1F0D" if is_dark else "#F0FDF4"
            payment_status_banner.border_radius = 8
            payment_status_banner.padding = ft.Padding(top=10, bottom=10, left=14, right=14)
            payment_status_banner.border = ft.Border(
                left=ft.BorderSide(3, _GREEN),
                right=ft.BorderSide(1, _GREEN + "44"),
                top=ft.BorderSide(1, _GREEN + "44"),
                bottom=ft.BorderSide(1, _GREEN + "44"),
            )
            payment_status_banner.content = ft.Row(spacing=10, controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE, size=20, color=_GREEN),
                ft.Text(
                    t("Payment Done!"),
                    size=14, color=_GREEN, weight=ft.FontWeight.BOLD,
                ),
            ])

            # ── Show Receipt ───────────────────────────────────────────────────
            receipt_section.visible = True
            receipt_section.content = _build_receipt(meth, case_id, fee_rows, total).content
            receipt_section.bgcolor = _build_receipt(meth, case_id, fee_rows, total).bgcolor
            receipt_section.border_radius = _build_receipt(meth, case_id, fee_rows, total).border_radius
            receipt_section.padding = _build_receipt(meth, case_id, fee_rows, total).padding
            receipt_section.border = _build_receipt(meth, case_id, fee_rows, total).border

        else:
            # Payment failed
            payment_status_banner.visible = True
            payment_status_banner.bgcolor = "#2D0A0A" if is_dark else "#FEF2F2"
            payment_status_banner.border_radius = 8
            payment_status_banner.padding = ft.Padding(top=10, bottom=10, left=14, right=14)
            payment_status_banner.border = ft.Border(
                left=ft.BorderSide(3, _RED),
                right=ft.BorderSide(1, _RED + "44"),
                top=ft.BorderSide(1, _RED + "44"),
                bottom=ft.BorderSide(1, _RED + "44"),
            )
            payment_status_banner.content = ft.Row(spacing=10, controls=[
                ft.Icon(ft.Icons.CANCEL, size=20, color=_RED),
                ft.Text(
                    t("Payment Failed. Please try again."),
                    size=13, color=_RED, weight=ft.FontWeight.BOLD,
                ),
            ])

            # Show failed section
            failed = _build_failed_section(meth, case_id)
            receipt_section.visible = True
            receipt_section.content = failed.content
            receipt_section.bgcolor = failed.bgcolor
            receipt_section.border_radius = failed.border_radius
            receipt_section.padding = failed.padding
            receipt_section.border = failed.border

        dlg_result.value = ""
        page.update()

    pay_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(t("Pay Case Fees"), size=16, weight=ft.FontWeight.BOLD, color=primary_text),
        content=ft.Container(
            width=460,
            content=ft.Column(
                tight=True,
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    dlg_case_label,
                    ft.Divider(color=divider_color),
                    dlg_fee_rows,
                    ft.Divider(color=divider_color),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(t("Total Amount"), size=14, weight=ft.FontWeight.BOLD, color=primary_text),
                            dlg_total_text,
                        ],
                    ),
                    ft.Container(height=4),
                    ft.Text(t("Select Payment Method"), size=13, weight=ft.FontWeight.BOLD, color=primary_text),
                    method_buttons_row,
                    ft.Container(height=4),
                    dlg_result,
                    # ── Payment status banner (injected after confirm) ──────────
                    payment_status_banner,
                    # ── Receipt / failed section (injected after confirm) ───────
                    receipt_section,
                ],
            ),
        ),
        actions=[
            ft.TextButton(t("Close"), on_click=lambda e: close_dialog()),
            ft.ElevatedButton(
                t("Confirm Payment"),
                bgcolor=_BLUE,
                color="white",
                on_click=confirm_payment,
            ),
        ],
        bgcolor=card_bg,
    )

    def close_dialog():
        pay_dialog.open = False
        dlg_result.value = ""
        selected_method["value"] = None
        payment_status_banner.visible = False
        payment_status_banner.content = None
        receipt_section.visible = False
        receipt_section.content = None
        for mb in method_btn_refs.values():
            mb.bgcolor = "#334155" if is_dark else "#E2E8F0"
            mb.color   = secondary_text
            mb.style   = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(2, "transparent"),
            )
        refresh_view()

    def open_pay_dialog(case_id, pending_rows):
        """pending_rows: list of (id, fee_type, amount) for unpaid fees of this case"""
        selected_payments["ids"]     = [r[0] for r in pending_rows]
        selected_payments["case_id"] = case_id
        total = sum(r[2] for r in pending_rows)
        selected_payments["total"]   = total
        selected_payments["rows"]    = list(pending_rows)

        dlg_case_label.value = f"📁 {t('Case ID')}: {case_id}"
        dlg_fee_rows.controls = []

        fee_icons = {
            "Court Fee":    (ft.Icons.GAVEL,        _BLUE),
            "Advocate Fee": (ft.Icons.PERSON,        _GREEN),
            "General Fee":  (ft.Icons.RECEIPT_LONG,  _AMBER),
        }
        for pid, fee_type, amount in pending_rows:
            icon, color = fee_icons.get(fee_type, (ft.Icons.MONEY, _SLATE))
            dlg_fee_rows.controls.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(spacing=6, controls=[
                            ft.Icon(icon, size=15, color=color),
                            ft.Text(t(fee_type), size=13, color=primary_text),
                        ]),
                        ft.Text(f"₹ {amount:,.0f}", size=13, color=primary_text, weight=ft.FontWeight.BOLD),
                    ],
                )
            )

        dlg_total_text.value = f"₹ {total:,.0f}"
        dlg_result.value     = ""

        # Reset status/receipt on re-open
        payment_status_banner.visible = False
        payment_status_banner.content = None
        receipt_section.visible = False
        receipt_section.content = None

        selected_method["value"] = None
        for mb in method_btn_refs.values():
            mb.bgcolor = "#334155" if is_dark else "#E2E8F0"
            mb.color   = secondary_text

        pay_dialog.open = True
        page.overlay.clear()
        page.overlay.append(pay_dialog)
        page.update()

    # ── Main view container ────────────────────────────────────────────────────
    view_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=16)

    def _fee_detail_row(label, amount, icon, color):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=6, controls=[
                    ft.Icon(icon, size=14, color=color),
                    ft.Text(label, size=13, color=secondary_text),
                ]),
                ft.Text(f"₹ {amount:,.0f}", size=13, color=primary_text, weight=ft.FontWeight.BOLD),
            ],
        )

    def _status_chip(status):
        color = {
            "Paid":                 _GREEN,
            "Pending":              _RED,
            "Overdue":              _RED,
            "Pending Confirmation": _AMBER,
        }.get(status, _SLATE)
        return ft.Container(
            bgcolor=color + "22",
            border_radius=6,
            padding=ft.Padding(top=3, bottom=3, left=10, right=10),
            content=ft.Text(status, size=11, color=color, weight=ft.FontWeight.BOLD),
        )

    def build_case_card(case_id, case_status, payments_for_case):
        court_amt = adv_amt = gen_amt = 0.0
        overall_status = "Paid"
        pending_rows = []   # (id, fee_type, amount) still to pay

        fee_details = {}   # fee_type -> (pid, amount, status, method, pay_date, deadline)
        for p in payments_for_case:
            pid, _, fee_type, amount, status, method, pay_date, deadline, _ = p
            amount = float(amount)
            if fee_type == "Court Fee":      court_amt = amount
            elif fee_type == "Advocate Fee": adv_amt   = amount
            else:                            gen_amt   = amount
            fee_details[fee_type] = (pid, amount, status, method, pay_date, deadline)
            if status != "Paid":
                overall_status = status
                pending_rows.append((pid, fee_type, amount))

        total      = court_amt + adv_amt + gen_amt
        paid_total = total - sum(r[2] for r in pending_rows)

        all_paid = not pending_rows

        fee_icons = {
            "Court Fee":    (ft.Icons.GAVEL,        _BLUE),
            "Advocate Fee": (ft.Icons.PERSON,        _GREEN),
            "General Fee":  (ft.Icons.RECEIPT_LONG,  "#7A6A3A"),
        }

        fee_rows_ui = []
        for fee_type in ["Court Fee", "Advocate Fee", "General Fee"]:
            if fee_type not in fee_details:
                continue
            pid, amount, status, method, pay_date, deadline = fee_details[fee_type]
            icon, color = fee_icons.get(fee_type, (ft.Icons.MONEY, _SLATE))
            is_paid = status == "Paid"

            # Deadline overdue check (stored as DD-MM-YYYY)
            deadline_display = ""
            deadline_color   = secondary_text
            if deadline and not is_paid:
                try:
                    from datetime import datetime as _dt
                    dl_date = _dt.strptime(deadline.strip(), "%d-%m-%Y").date()
                    days    = (dl_date - _dt.now().date()).days
                    # Show as DD Mon YYYY for readability
                    deadline_display = f"Due: {dl_date.strftime('%d %b %Y')}"
                    if days < 0:
                        deadline_display = f"⚠ Overdue since {dl_date.strftime('%d %b %Y')}"
                        deadline_color   = _RED
                    elif days == 0:
                        deadline_display = f"⚠ Due Today!"
                        deadline_color   = _RED
                    elif days <= 3:
                        deadline_display = f"⚠ Due in {days} day{'s' if days != 1 else ''}"
                        deadline_color   = "#B45309"
                except Exception:
                    deadline_display = deadline

            status_chip = ft.Container(
                bgcolor=(_GREEN if is_paid else _RED) + "22",
                border_radius=6,
                padding=ft.Padding(top=2, bottom=2, left=8, right=8),
                content=ft.Text(
                    t("Paid") if is_paid else t("Pending"),
                    size=11,
                    color=_GREEN if is_paid else _RED,
                    weight=ft.FontWeight.BOLD,
                ),
            )

            pay_single_btn = ft.ElevatedButton(
                t("Pay"),
                bgcolor=_BLUE,
                color="white",
                height=30,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
                on_click=lambda e, _pid=pid, _ft=fee_type, _amt=amount:
                    open_pay_dialog(case_id, [(_pid, _ft, _amt)]),
                visible=not is_paid,
            )

            fee_rows_ui.append(
                ft.Container(
                    bgcolor="#F8FAFC" if not is_dark else "#253347",
                    border_radius=8,
                    padding=ft.Padding(top=10, bottom=10, left=14, right=14),
                    border=ft.Border.all(1, divider_color),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(spacing=10, controls=[
                                ft.Container(
                                    width=32, height=32, bgcolor=color + "18",
                                    border_radius=8, alignment=ft.Alignment.CENTER,
                                    content=ft.Icon(icon, size=16, color=color),
                                ),
                            ft.Column(spacing=2, controls=[
                                    ft.Text(t(fee_type), size=13,
                                            weight=ft.FontWeight.BOLD, color=primary_text),
                                    ft.Text(
                                        f"{method or '—'}  ·  {pay_date or '—'}" if is_paid else t("Not paid yet"),
                                        size=11, color=secondary_text,
                                    ),
                                    ft.Text(deadline_display, size=11, color=deadline_color,
                                            weight=ft.FontWeight.BOLD) if deadline_display else ft.Container(),
                                ]),
                            ]),
                            ft.Row(spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                                ft.Text(f"₹ {amount:,.0f}", size=14,
                                        weight=ft.FontWeight.BOLD, color=primary_text),
                                status_chip,
                                pay_single_btn,
                            ]),
                        ],
                    ),
                )
            )

        # ── Pay All button (only if multiple pending) ──────────────────────────
        pay_all_btn = ft.Container()
        if len(pending_rows) > 1:
            pay_all_btn = ft.ElevatedButton(
                t("Pay All Pending"),
                bgcolor=_BLUE,
                color="white",
                icon=ft.Icons.PAYMENT,
                on_click=lambda e, pr=list(pending_rows): open_pay_dialog(case_id, pr),
            )

        paid_badge = ft.Container(
            bgcolor=_GREEN + "22",
            border_radius=8,
            padding=ft.Padding(top=4, bottom=4, left=12, right=12),
            content=ft.Row(spacing=6, controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE, size=14, color=_GREEN),
                ft.Text(t("All Fees Paid"), size=12, color=_GREEN, weight=ft.FontWeight.BOLD),
            ]),
            visible=all_paid,
        )

        return ft.Container(
            bgcolor=card_bg,
            border_radius=14,
            padding=20,
            content=ft.Column(
                spacing=12,
                controls=[
                    # Header row
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(spacing=10, controls=[
                                ft.Icon(ft.Icons.FOLDER_OPEN, color=_BLUE, size=20),
                                ft.Text(case_id, size=15,
                                        weight=ft.FontWeight.BOLD, color=primary_text),
                            ]),
                            ft.Row(spacing=8, controls=[
                                paid_badge,
                                pay_all_btn,
                            ]),
                        ],
                    ),
                    ft.Divider(color=divider_color, height=1),
                    # Per-fee rows
                    *fee_rows_ui,
                    ft.Divider(color=divider_color, height=1),
                    # Summary totals
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=2, controls=[
                                ft.Text(t("Total Amount"), size=12, color=secondary_text),
                                ft.Text(f"₹ {total:,.0f}", size=20,
                                        weight=ft.FontWeight.BOLD, color=_BLUE),
                            ]),
                            ft.Column(spacing=2,
                                      horizontal_alignment=ft.CrossAxisAlignment.END, controls=[
                                ft.Text(t("Paid"), size=12, color=secondary_text),
                                ft.Text(f"₹ {paid_total:,.0f}", size=16,
                                        weight=ft.FontWeight.BOLD, color=_GREEN),
                            ]),
                            ft.Column(spacing=2,
                                      horizontal_alignment=ft.CrossAxisAlignment.END, controls=[
                                ft.Text(t("Pending"), size=12, color=secondary_text),
                                ft.Text(
                                    f"₹ {sum(r[2] for r in pending_rows):,.0f}",
                                    size=16, weight=ft.FontWeight.BOLD,
                                    color=_RED if pending_rows else _GREEN,
                                ),
                            ]),
                        ],
                    ),
                ],
            ),
        )

    def refresh_view():
        payments = get_payments_by_user(username)
        cases    = get_cases_by_user(username)

        from collections import defaultdict
        by_case = defaultdict(list)
        for p in payments:
            by_case[p[1]].append(p)

        total_paid = total_pending = 0.0
        for p in payments:
            amt = float(p[3])
            if p[4] == "Paid":
                total_paid += amt
            else:
                total_pending += amt

        def _summary_card(label, value, colour, icon):
            return ft.Container(
                expand=True,
                bgcolor=card_bg,
                border_radius=12,
                padding=18,
                content=ft.Column(spacing=6, controls=[
                    ft.Row(spacing=6, controls=[
                        ft.Icon(icon, color=colour, size=16),
                        ft.Text(label, size=12, color=secondary_text),
                    ]),
                    ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=colour),
                ]),
            )

        case_cards = []
        for c in cases:
            case_id, client_name, advocate_name, status = c
            if case_id in by_case:
                card = build_case_card(case_id, status, by_case[case_id])
                case_cards.append(card)

        empty_state = ft.Container(
            bgcolor=card_bg,
            border_radius=14,
            padding=40,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.RECEIPT_LONG, size=48, color=_SLATE),
                    ft.Text(t("No billing records found"), size=15, color=_SLATE),
                    ft.Text(t("Fee details will appear here once your advocate declares fees."),
                            size=12, color=_SLATE, italic=True),
                ],
            ),
        ) if not case_cards else ft.Container()

        view_container.controls = [
            navbar(user_info=user_info, on_logout=(lambda e: load_page("home")) if load_page else None),
            ft.Container(height=4),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(spacing=2, controls=[
                        ft.Text(t("Billing & Payments"), size=24, weight=ft.FontWeight.BOLD, color=primary_text),
                        ft.Text(t("View fee details and pay securely"), size=13, color=secondary_text),
                    ]),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip=t("Refresh"),
                        icon_color=_SLATE,
                        on_click=lambda e: refresh_view(),
                    ),
                ]
            ),
            ft.Container(height=4),
            ft.Row(spacing=14, controls=[
                _summary_card(t("Total Paid"),    f"₹ {total_paid:,.0f}",              _GREEN, ft.Icons.CHECK_CIRCLE),
                _summary_card(t("Total Pending"), f"₹ {total_pending:,.0f}",           _RED,   ft.Icons.PENDING),
                _summary_card(t("Total Amount"),  f"₹ {total_paid + total_pending:,.0f}", _BLUE, ft.Icons.ACCOUNT_BALANCE_WALLET),
            ]),
            ft.Container(height=8),
            ft.Text(t("Cases & Fee Details"), size=16, weight=ft.FontWeight.BOLD, color=primary_text),
            *case_cards,
            empty_state,
            ft.Container(height=20),
            ft.Text(t("VIDHI Legal AI © 2026"), size=12, color=_SLATE),
        ]
        page.update()

    refresh_view()

    return ft.Container(
        expand=True,
        bgcolor=page_bg,
        padding=24,
        content=view_container,
    )
