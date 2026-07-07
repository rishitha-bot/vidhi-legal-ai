import flet as ft
from i18n import t

def sidebar():
    items=[("Dashboard",ft.Icons.DASHBOARD),("Matters",ft.Icons.GAVEL),("Documents",ft.Icons.DESCRIPTION),("AI Assistant",ft.Icons.SMART_TOY),("Calendar",ft.Icons.CALENDAR_MONTH),("Billing",ft.Icons.PAYMENTS),("Contacts",ft.Icons.CONTACT_PAGE),("About",ft.Icons.INFO),("Settings",ft.Icons.SETTINGS)]
    return ft.Container(width=250,bgcolor="#1E293B",padding=20,content=ft.Column(controls=[ft.Text(t("VIDHI"),size=32,color="white",weight=ft.FontWeight.BOLD),ft.Text(t("Legal AI Platform"),color="white70"),ft.Divider()]+[ft.ListTile(leading=ft.Icon(i,color="white"),title=ft.Text(t(n),color="white")) for n,i in items]))
