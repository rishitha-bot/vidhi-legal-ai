import flet as ft
from datetime import datetime
from i18n import t

from services.db import (
    get_all_payments,
    get_pending_cash_payments,
    update_payment_status,
    update_payment_deadline,
    add_payment,
    get_all_cases,
)

_BLUE  = "#4A7FC1"
_SLATE = "#64748B"
_GREEN = "#4A8C6A"
_AMBER = "#7A6A3A"   # muted olive instead of brown
_RED   = "#DC2626"


def _kpi_card(title, value, sub, card_bg, primary_text):
    return ft.Container(
        expand=True,
        bgcolor=card_bg,
        border_radius=12,
        padding=ft.Padding(top=18, bottom=18, left=18, right=18),
        content=ft.Column(
            spacing=4,
            controls=[
                ft.Text(title, size=12, color=_SLATE),
                ft.Text(str(value), size=26, weight=ft.FontWeight.BOLD, color=_BLUE),
                ft.Text(sub, size=11, color=_SLATE) if sub else ft.Container(),
            ],
        ),
    )


def _status_badge(status):
    colour = {
        "Paid":                 _GREEN,
        "Pending":              "#6B7A5E",   # muted sage
        "Overdue":              _RED,
        "Pending Confirmation": "#5A6B7A",   # muted slate-blue
    }.get(status, _SLATE)
    return ft.Container(
        bgcolor=colour + "33",
        border_radius=6,
        padding=ft.Padding(top=3, bottom=3, left=10, right=10),
        content=ft.Text(status, size=12, color=colour, weight=ft.FontWeight.BOLD),
    )


def billing_view(page=None, load_page=None):

    is_dark        = page.theme_mode == ft.ThemeMode.DARK if page else False
    page_bg        = "#0F172A" if is_dark else "#F8FAFC"
    card_bg        = "#1E293B" if is_dark else "white"
    primary_text   = "white"   if is_dark else "#111827"
    secondary_text = "#CBD5E1" if is_dark else "#6B7280"
    divider_color  = "#334155" if is_dark else "#D1D5DB"
    dl_default_col = primary_text

    # ── cash-confirmation dialog ───────────────────────────────────────────────
    dlg_info    = ft.Text("", size=13, color=primary_text)
    dlg_result  = ft.Text("", color=_GREEN)
    confirm_pid = {"id": None}

    def do_confirm(e):
        if confirm_pid["id"] is not None:
            update_payment_status(confirm_pid["id"], "Paid", method="Cash", confirmed_by="Advocate")
            dlg_result.value  = "✔ Cash payment confirmed and marked as Paid."
            dlg_result.color  = _GREEN
            if page:
                page.update()

    cash_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(t("Confirm Cash Payment"), weight=ft.FontWeight.BOLD),
        content=ft.Column(tight=True, width=360, controls=[dlg_info, dlg_result]),
        actions=[
            ft.TextButton(t("Cancel"),  on_click=lambda e: close_cash_dlg()),
            ft.ElevatedButton(t("Confirm Received"), bgcolor=_GREEN, color="white", on_click=do_confirm),
        ],
    )

    def close_cash_dlg():
        cash_dlg.open = False
        dlg_result.value = ""
        if page:
            refresh(page)

    def open_cash_dlg(pid, case_id, amount, fee_type):
        confirm_pid["id"] = pid
        dlg_info.value    = (f"{t('Case')}: {case_id}   |   {fee_type}   |   ₹ {float(amount):,.0f}\n\n"
                             + t("Confirm that you have physically received the cash?"))
        dlg_result.value  = ""
        cash_dlg.open     = True
        if page:
            page.overlay.clear()
            page.overlay.append(cash_dlg)
            page.update()

    # ── deadline dialog ────────────────────────────────────────────────────────
    dl_pid_ref = {"id": None}
    dl_field   = ft.TextField(
        label=t("Deadline (DD-MM-YYYY)"),
        width=300,
        hint_text="e.g. 30-07-2026",
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    dl_result  = ft.Text("", color=_GREEN)

    def _parse_deadline(raw: str):
        """Accept DD-MM-YYYY or DD/MM/YYYY or DD Mon YYYY, return DD-MM-YYYY string or None."""
        from datetime import datetime
        FMTS = ["%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"]
        raw = raw.strip()
        for fmt in FMTS:
            try:
                return datetime.strptime(raw, fmt).strftime("%d-%m-%Y")
            except ValueError:
                continue
        return None

    def save_deadline(e):
        if not dl_pid_ref["id"] or not dl_field.value.strip():
            return
        normalised = _parse_deadline(dl_field.value.strip())
        if not normalised:
            dl_result.value = t("⚠ Use format DD-MM-YYYY  e.g. 30-07-2026")
            dl_result.color = _RED
            if page:
                page.update()
            return
        update_payment_deadline(dl_pid_ref["id"], normalised)
        dl_result.value = t("✔ Deadline saved.")
        dl_result.color = _GREEN
        if page:
            page.update()

    deadline_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(t("Set Payment Deadline"), weight=ft.FontWeight.BOLD),
        content=ft.Column(tight=True, width=340, controls=[dl_field, dl_result]),
        actions=[
            ft.TextButton(t("Close"), on_click=lambda e: close_deadline_dlg()),
            ft.ElevatedButton(t("Save"), bgcolor=_BLUE, color="white", on_click=save_deadline),
        ],
    )

    def close_deadline_dlg():
        deadline_dlg.open = False
        dl_result.value = ""
        if page:
            refresh(page)

    def open_deadline_dlg(pid, current_deadline):
        dl_pid_ref["id"]  = pid
        dl_field.value    = current_deadline or ""
        dl_result.value   = ""
        deadline_dlg.open = True
        if page:
            page.overlay.clear()
            page.overlay.append(deadline_dlg)
            page.update()

    # ── Add Fee Dialog ─────────────────────────────────────────────────────────
    # Step-1 widgets: case dropdown
    all_cases = get_all_cases()
    case_options = [
        ft.dropdown.Option(key=c[2], text=f"{c[2]} – {c[3]}")  # case_id, client_name
        for c in all_cases
    ]
    fee_case_dd = ft.Dropdown(
        label=t("Select Case"),
        options=case_options,
        width=360,
        border_color=_BLUE,
    )

    # Step-2 widgets: three fee fields
    court_fee_field = ft.TextField(
        label=t("Court Fee (₹)"),
        keyboard_type=ft.KeyboardType.NUMBER,
        width=400,
        hint_text="0",
    )
    adv_fee_field = ft.TextField(
        label=t("Advocate Fee (₹)"),
        keyboard_type=ft.KeyboardType.NUMBER,
        width=400,
        hint_text="0",
    )
    gen_fee_field = ft.TextField(
        label=t("General Fee (₹)"),
        keyboard_type=ft.KeyboardType.NUMBER,
        width=400,
        hint_text="0",
    )

    fee_step1 = ft.Column(visible=True, tight=True, spacing=12, controls=[
        ft.Text(t("Step 1: Select a case to assign fees"), size=13, color=_SLATE),
        fee_case_dd,
    ])

    fee_step2 = ft.Column(visible=False, tight=True, spacing=12, controls=[
        ft.Text(t("Step 2: Enter fee amounts for the case"), size=13, color=_SLATE),
        ft.Text("", size=12, color=_BLUE, italic=True),   # placeholder for selected case label
        court_fee_field,
        adv_fee_field,
        gen_fee_field,
    ])

    fee_dlg_result = ft.Text("", color=_GREEN)
    fee_next_btn   = ft.ElevatedButton(t("Next →"), bgcolor=_BLUE, color="white")
    fee_back_btn   = ft.TextButton(t("← Back"), visible=False)
    fee_save_btn   = ft.ElevatedButton(t("Declare Fees"), bgcolor=_GREEN, color="white", visible=False)

    fee_dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(t("Declare Case Fees"), weight=ft.FontWeight.BOLD),
        content=ft.Column(
            tight=True,
            width=440,
            controls=[fee_step1, fee_step2, fee_dlg_result],
        ),
        actions=[fee_back_btn, fee_next_btn, fee_save_btn,
                 ft.TextButton(t("Close"), on_click=lambda e: close_fee_dlg())],
    )

    def close_fee_dlg():
        fee_dlg.open      = False
        fee_step1.visible = True
        fee_step2.visible = False
        fee_next_btn.visible = True
        fee_back_btn.visible = False
        fee_save_btn.visible = False
        fee_case_dd.value    = None
        court_fee_field.value = ""
        adv_fee_field.value   = ""
        gen_fee_field.value   = ""
        fee_dlg_result.value  = ""
        if page:
            refresh(page)

    def go_to_step2(e):
        if not fee_case_dd.value:
            fee_dlg_result.value = t("⚠ Please select a case first.")
            fee_dlg_result.color = _AMBER
            if page:
                page.update()
            return
        fee_dlg_result.value = ""
        # Update the selected-case label in step 2
        label_ctrl = fee_step2.controls[1]
        label_ctrl.value = f"📁 {t('Case')}: {fee_case_dd.value}"
        fee_step1.visible    = False
        fee_step2.visible    = True
        fee_next_btn.visible = False
        fee_back_btn.visible = True
        fee_save_btn.visible = True
        if page:
            page.update()

    def go_back_to_step1(e):
        fee_step1.visible    = True
        fee_step2.visible    = False
        fee_next_btn.visible = True
        fee_back_btn.visible = False
        fee_save_btn.visible = False
        fee_dlg_result.value = ""
        if page:
            page.update()

    def save_fees(e):
        cid = fee_case_dd.value
        errors = []

        def _parse(field):
            try:
                v = float(field.value.strip() or "0")
                if v < 0:
                    raise ValueError
                return v
            except ValueError:
                errors.append(field.label)
                return None

        cf = _parse(court_fee_field)
        af = _parse(adv_fee_field)
        gf = _parse(gen_fee_field)

        if errors:
            fee_dlg_result.value = t("⚠ Invalid amount in: ") + ", ".join(errors)
            fee_dlg_result.color = _RED
            if page:
                page.update()
            return

        if (cf or 0) == 0 and (af or 0) == 0 and (gf or 0) == 0:
            fee_dlg_result.value = t("⚠ Please enter at least one fee amount.")
            fee_dlg_result.color = _AMBER
            if page:
                page.update()
            return

        # payment_date is None until client actually pays
        if cf and cf > 0:
            add_payment(cid, "Court Fee",    cf, "Pending", None, None)
        if af and af > 0:
            add_payment(cid, "Advocate Fee", af, "Pending", None, None)
        if gf and gf > 0:
            add_payment(cid, "General Fee",  gf, "Pending", None, None)

        fee_dlg_result.value = t("✔ Fees declared successfully!")
        fee_dlg_result.color = _GREEN
        court_fee_field.value = ""
        adv_fee_field.value   = ""
        gen_fee_field.value   = ""
        if page:
            page.update()

    fee_next_btn.on_click = go_to_step2
    fee_back_btn.on_click = go_back_to_step1
    fee_save_btn.on_click = save_fees

    def open_fee_dlg(e):
        # Refresh case list each time dialog opens
        fresh_cases = get_all_cases()
        fee_case_dd.options = [
            ft.dropdown.Option(key=c[2], text=f"{c[2]} – {c[3]}")
            for c in fresh_cases
        ]
        fee_step1.visible    = True
        fee_step2.visible    = False
        fee_next_btn.visible = True
        fee_back_btn.visible = False
        fee_save_btn.visible = False
        fee_case_dd.value    = None
        court_fee_field.value = ""
        adv_fee_field.value   = ""
        gen_fee_field.value   = ""
        fee_dlg_result.value  = ""
        fee_dlg.open = True
        if page:
            page.overlay.clear()
            page.overlay.append(fee_dlg)
            page.update()

    # ── wrapper that gets rebuilt on every refresh ─────────────────────────────
    main_col = ft.Column(scroll=ft.ScrollMode.AUTO)
    wrapper   = ft.Container(expand=True, padding=20, bgcolor=page_bg, content=main_col)

    def refresh(pg=None):
        main_col.controls.clear()
        main_col.controls.extend(build_controls())
        if page:
            page.update()

    def build_controls():
        all_payments = get_all_payments()

        total_revenue = sum(float(p[3]) for p in all_payments if p[4] == "Paid")
        pending_amt   = sum(float(p[3]) for p in all_payments if p[4] in ("Pending", "Overdue", "Pending Confirmation"))
        total_inv     = len(all_payments)
        paid_inv      = sum(1 for p in all_payments if p[4] == "Paid")

        court_rows, adv_rows, gen_rows = [], [], []

        for p in all_payments:
            pid, case_id, fee_type, amount, status, method, pay_date, deadline, cash_conf = p

            dl_colour = dl_default_col
            if deadline and status not in ("Paid",):
                try:
                    dl_dt = datetime.strptime(deadline.strip(), "%d-%m-%Y")
                    days  = (dl_dt.date() - datetime.now().date()).days
                    dl_colour = _RED if days < 0 else (_AMBER if days <= 3 else dl_default_col)
                except Exception:
                    pass

            action = ft.Row(spacing=4, controls=[
                ft.TextButton(
                    t("📅 Deadline"),
                    on_click=lambda e, _pid=pid, _dl=deadline: open_deadline_dlg(_pid, _dl),
                    style=ft.ButtonStyle(color=_BLUE),
                ),
            ])
            if status == "Pending Confirmation" and method == "Cash":
                action.controls.append(
                    ft.ElevatedButton(
                        t("Confirm Cash"), bgcolor="#5A6B7A", color="white", height=28,
                        on_click=lambda e, _pid=pid, _cid=case_id, _amt=amount, _ft=fee_type:
                            open_cash_dlg(_pid, _cid, _amt, _ft),
                    )
                )

            row = ft.DataRow(cells=[
                ft.DataCell(ft.Text(case_id,                    color=primary_text)),
                ft.DataCell(ft.Text(f"₹ {float(amount):,.0f}",  color=primary_text)),
                ft.DataCell(_status_badge(status)),
                ft.DataCell(ft.Text(method or "—",              color=secondary_text)),
                ft.DataCell(ft.Text(pay_date if status == "Paid" else "—", color=primary_text)),
                ft.DataCell(ft.Text(deadline or "—",            color=dl_colour, weight=ft.FontWeight.BOLD)),
                ft.DataCell(action),
            ])

            if fee_type == "Court Fee":      court_rows.append(row)
            elif fee_type == "Advocate Fee": adv_rows.append(row)
            else:                            gen_rows.append(row)

        def fee_col(title, icon, rows):
            cols = [
                ft.DataColumn(ft.Text(t("Case"),     color=primary_text, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text(t("Amount"),   color=primary_text, weight=ft.FontWeight.BOLD), numeric=True),
                ft.DataColumn(ft.Text(t("Status"),   color=primary_text, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text(t("Method"),   color=primary_text, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text(t("Paid On"),  color=primary_text, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text(t("Deadline"), color=primary_text, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text(t("Action"),   color=primary_text, weight=ft.FontWeight.BOLD)),
            ]
            empty = ft.Container(
                padding=12,
                content=ft.Text(t("No records"), color=_SLATE, italic=True, size=13),
            )
            return ft.Container(
                expand=True, bgcolor=card_bg, border_radius=14, padding=20,
                content=ft.Column(controls=[
                    ft.Row(spacing=8, controls=[
                        ft.Icon(icon, color=_BLUE, size=18),
                        ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=primary_text),
                    ]),
                    ft.Divider(color=divider_color),
                    ft.DataTable(columns=cols, rows=rows) if rows else empty,
                ]),
            )

        pending_cash    = get_pending_cash_payments()
        cash_alert_rows = []
        for pc in pending_cash:
            _pid, _cid, _ftype, _amt, _meth, _pdate, _dl, _user = pc
            cash_alert_rows.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ATTACH_MONEY, color="#5A6B7A"),
                    title=ft.Text(f"{_cid} — {_ftype}  ₹ {float(_amt):,.0f}", color=primary_text),
                    subtitle=ft.Text(f"{t('Client')}: {_user}   {t('Deadline')}: {_dl or '—'}", color=secondary_text),
                    trailing=ft.ElevatedButton(
                        t("Confirm"), bgcolor="#5A6B7A", color="white", height=28,
                        on_click=lambda e, p=_pid, c=_cid, a=_amt, f=_ftype: open_cash_dlg(p, c, a, f),
                    ),
                )
            )

        cash_bg = "#1E2A35" if is_dark else "#EFF4F8"
        cash_section = ft.Container()
        if cash_alert_rows:
            cash_section = ft.Container(
                bgcolor=cash_bg, border_radius=14, padding=16,
                content=ft.Column(controls=[
                    ft.Row(spacing=8, controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, color="#5A6B7A"),
                        ft.Text(t("Cash Payments Awaiting Your Confirmation"),
                                size=15, weight=ft.FontWeight.BOLD, color="#5A6B7A"),
                    ]),
                    ft.Divider(color=divider_color),
                    *cash_alert_rows,
                ]),
            )

        return [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(spacing=2, controls=[
                        ft.Text(t("Billing & Finance"), size=26, weight=ft.FontWeight.BOLD, color=primary_text),
                        ft.Text(t("Manage invoices, payments and financial overview"), size=13, color=_SLATE),
                    ]),
                    ft.Row(spacing=10, controls=[
                        ft.IconButton(
                            icon=ft.Icons.REFRESH, tooltip=t("Refresh"),
                            icon_color=_SLATE,
                            on_click=lambda e: refresh(),
                        ),
                        ft.ElevatedButton(
                            t("+ Declare Case Fees"), bgcolor=_BLUE, color="white",
                            icon=ft.Icons.RECEIPT_LONG, on_click=open_fee_dlg,
                        ),
                        ft.OutlinedButton(t("Export Report")),
                    ]),
                ],
            ),
            ft.Container(height=12),
            ft.Row(spacing=14, controls=[
                _kpi_card("Total Revenue",  f"₹ {total_revenue:,.0f}", "Paid invoices", card_bg, primary_text),
                _kpi_card("Pending Amount", f"₹ {pending_amt:,.0f}",   "Unpaid",        card_bg, primary_text),
                _kpi_card("Total Invoices", str(total_inv),             "All records",   card_bg, primary_text),
                _kpi_card("Paid Invoices",  str(paid_inv),
                          f"{round(paid_inv/total_inv*100) if total_inv else 0}% of total", card_bg, primary_text),
            ]),
            ft.Container(height=14),
            cash_section,
            ft.Container(height=10) if cash_alert_rows else ft.Container(),
            ft.Container(height=14),
            fee_col("🏛  Court Fee",   ft.Icons.GAVEL,        court_rows),
            ft.Container(height=10),
            fee_col("⚖  Advocate Fee", ft.Icons.PERSON,       adv_rows),
            ft.Container(height=10),
            fee_col("📋  General Fee",  ft.Icons.RECEIPT_LONG, gen_rows),
            ft.Container(height=20),
            ft.Divider(color=divider_color),
            ft.Text(t("VIDHI Legal AI © 2026"), size=13, color=_SLATE),
        ]

    main_col.controls.extend(build_controls())
    return wrapper
