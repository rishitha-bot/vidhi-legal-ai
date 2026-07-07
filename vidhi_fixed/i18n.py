# -*- coding: utf-8 -*-
"""
i18n.py
----------------------------------------------------------------------
Lightweight translation layer for the VIDHI Legal AI Flet app.

Flet is an imperative UI framework (it is not reactive like React/Vue),
so there is no automatic re-render when text changes. To support
"Translate to Telugu" across every screen we:

  1. Keep a single global language flag (LANG["code"]).
  2. Provide t("Some English Text") -> returns the Telugu string when
     the language is set to "te", otherwise returns the text unchanged.
  3. Every view/component function calls t(...) around every literal
     string shown to the user instead of hard-coding it.
  4. When the user taps the "Translate to Telugu" button, we flip the
     language flag and rebuild whichever screen is currently mounted,
     which causes every t(...) call to re-evaluate to Telugu text.

Numbers, currency figures, IDs (e.g. "VD001"), and other non-language
content are left as-is by t() if they are not present in the
dictionary - that's intentional, since untranslated text is simply
returned unchanged.
----------------------------------------------------------------------
"""

# Current language code: "en" (English, default) or "te" (Telugu)
LANG = {"code": "en"}


def set_language(code: str):
    """Set the global language. code: 'en' or 'te'."""
    if code in ("en", "te"):
        LANG["code"] = code


def toggle_language():
    """Flip between English and Telugu. Returns the new code."""
    LANG["code"] = "te" if LANG["code"] == "en" else "en"
    return LANG["code"]


def get_language():
    return LANG["code"]


def is_telugu():
    return LANG["code"] == "te"


# ----------------------------------------------------------------------
# English -> Telugu dictionary
# ----------------------------------------------------------------------
TRANSLATIONS = {
    # ---- Branding / common ----
    "VIDHI": "విధి",
    "VIDHI LEGAL AI": "విధి లీగల్ AI",
    "VIDHI Legal AI": "విధి లీగల్ AI",
    "VIDHI Legal AI © 2026": "విధి లీగల్ AI © 2026",
    "Legal AI Platform": "లీగల్ AI ప్లాట్‌ఫారమ్",
    "AI-Powered Legal Intelligence Platform": "AI ఆధారిత న్యాయ మేధో వేదిక",
    "Powered by Artificial Intelligence": "కృత్రిమ మేధస్సుతో శక్తివంతం",
    "Powered by AI": "AI శక్తితో",

    # ---- Home page ----
    "Case Management": "కేసు నిర్వహణ",
    "Document Intelligence": "పత్రాల విశ్లేషణ",
    "Legal Research": "న్యాయ పరిశోధన",
    "Smarter Legal Work,": "తెలివైన న్యాయ పని,",
    "Manage cases, analyze documents and conduct legal research":
        "కేసులను నిర్వహించండి, పత్రాలను విశ్లేషించండి మరియు న్యాయ పరిశోధన చేయండి",
    "with intelligent tools built for legal professionals.":
        "న్యాయ నిపుణుల కోసం రూపొందించిన తెలివైన సాధనాలతో.",
    "Client": "కక్షిదారు",
    "Track your cases\nand updates": "మీ కేసులను\nమరియు అప్‌డేట్‌లను ట్రాక్ చేయండి",
    "Advocate": "న్యాయవాది",
    "Manage clients\nand matters": "కక్షిదారులను\nమరియు కేసులను నిర్వహించండి",
    "Continue  →": "కొనసాగించు  →",
    "Translate to Telugu": "తెలుగులోకి అనువదించండి",
    "Translate to English": "ఆంగ్లంలోకి మార్చండి",
    "తెలుగు": "తెలుగు",
    "English": "ఆంగ్లం",

    # ---- Login ----
    "← Back to Home": "← హోమ్‌కు తిరిగి వెళ్ళండి",
    "Login / Register": "లాగిన్ / నమోదు",
    "Email ID / Phone Number": "ఇమెయిల్ ఐడి / ఫోన్ నంబర్",
    "Username": "వినియోగదారు పేరు",
    "Password": "పాస్‌వర్డ్",
    "Login": "లాగిన్",
    "Create Account": "ఖాతా సృష్టించండి",
    "Fill all fields": "అన్ని ఫీల్డ్‌లను పూరించండి",
    "Enter valid Phone Number or Email": "సరైన ఫోన్ నంబర్ లేదా ఇమెయిల్ నమోదు చేయండి",
    "Username must be at least 4 characters": "వినియోగదారు పేరు కనీసం 4 అక్షరాలు ఉండాలి",
    "Password must be at least 6 characters": "పాస్‌వర్డ్ కనీసం 6 అక్షరాలు ఉండాలి",
    "Invalid Username or Password": "తప్పు వినియోగదారు పేరు లేదా పాస్‌వర్డ్",

    # ---- Sidebar / Nav ----
    "Dashboard": "డాష్‌బోర్డ్",
    "Active Matters": "క్రియాశీల కేసులు",
    "Matters": "కేసులు",
    "All Matters": "అన్ని కేసులు",
    "Documents": "పత్రాలు",
    "Documentation": "పత్రావళి",
    "AI Assistant": "AI సహాయకుడు",
    "Calendar": "క్యాలెండర్",
    "Billing": "బిల్లింగ్",
    "Billing & Payments": "బిల్లింగ్ & చెల్లింపులు",
    "Billing & Finance": "బిల్లింగ్ & ఆర్థిక వ్యవహారాలు",
    "Contacts": "పరిచయాలు",
    "About": "గురించి",
    "Settings": "సెట్టింగ్‌లు",
    "Logout": "లాగ్అవుట్",
    "Today": "ఈరోజు",
    "Logged in as ": "ఇలా లాగిన్ అయ్యారు: ",

    # ---- Dashboard ----
    "Service Requests": "సేవా అభ్యర్థనలు",
    "View": "వీక్షించండి",
    "Click to open": "తెరవడానికి క్లిక్ చేయండి",
    "Annual Revenue": "వార్షిక ఆదాయం",
    "FY 2025-26": "ఆర్థిక సంవత్సరం 2025-26",
    "Hearings This Week": "ఈ వారం విచారణలు",
    "Upcoming": "రాబోయేవి",
    "Open Requests": "అభ్యర్థనలను తెరువు",
    "Cases Won": "గెలిచిన కేసులు",
    "Cases Lost": "ఓడిన కేసులు",
    "Win Probability": "గెలుపు అవకాశం",
    "Average": "సగటు",
    "Case Stage Funnel": "కేసు దశల విశ్లేషణ",
    "Filed": "దాఖలు చేయబడింది",
    "Hearing Scheduled": "విచారణ నిర్ణయించబడింది",
    "Under Judgment": "తీర్పు పరిశీలనలో",
    "Closed": "ముగిసింది",
    "Recent Cases": "ఇటీవలి కేసులు",
    "Quick Actions": "త్వరిత చర్యలు",
    "Case Performance": "కేసు పనితీరు",
    "Case Analytics": "కేసు విశ్లేషణలు",
    "Win %": "గెలుపు %",
    "No data available": "డేటా అందుబాటులో లేదు",
    "My Current Status": "నా ప్రస్తుత స్థితి",
    "Upcoming Hearings": "రాబోయే విచారణలు",
    "No hearings scheduled": "విచారణలు ఏవీ నిర్ణయించబడలేదు",
    "Suggested Legal Insights": "సూచించిన న్యాయ అంతర్దృష్టులు",
    "Selected Matter": "ఎంచుకున్న కేసు",
    "No Cases": "కేసులు లేవు",

    # ---- Active Cases / Service requests ----
    "Active Cases": "క్రియాశీల కేసులు",
    "Active Service Requests": "క్రియాశీల సేవా అభ్యర్థనలు",
    "Click on a request to view details": "వివరాలు చూడటానికి అభ్యర్థనపై క్లిక్ చేయండి",
    "Request Information": "అభ్యర్థన సమాచారం",
    "Request ID": "అభ్యర్థన ఐడి",
    "Client Name": "కక్షిదారు పేరు",
    "Case Type:": "కేసు రకం:",
    "Urgency:": "ప్రాధాన్యత:",
    "Status:": "స్థితి:",
    "Status : ": "స్థితి : ",
    "Advocate Actions": "న్యాయవాది చర్యలు",
    "Approve Request": "అభ్యర్థనను ఆమోదించండి",
    "Reject Request": "అభ్యర్థనను తిరస్కరించండి",
    "Schedule Hearing": "విచారణ నిర్ణయించండి",
    "Delete Service Request": "సేవా అభ్యర్థనను తొలగించండి",
    "This will permanently remove the request and all associated payments. This cannot be undone.":
        "ఇది అభ్యర్థనను మరియు సంబంధిత చెల్లింపులన్నింటినీ శాశ్వతంగా తొలగిస్తుంది. దీన్ని తిరిగి పొందలేరు.",
    "Cancel": "రద్దు చేయండి",
    "Yes, Delete": "అవును, తొలగించండి",
    "Request Approved": "అభ్యర్థన ఆమోదించబడింది",
    "Request Rejected": "అభ్యర్థన తిరస్కరించబడింది",
    "Enter hearing date": "విచారణ తేదీని నమోదు చేయండి",
    "No cases found.": "కేసులు ఏవీ కనుగొనబడలేదు.",
    "Pending": "పెండింగ్‌లో",
    "Active": "క్రియాశీలం",
    "Awaiting advocate": "న్యాయవాది కోసం ఎదురుచూస్తోంది",

    # ---- New case ----
    "Add Service Request": "సేవా అభ్యర్థనను జోడించండి",
    "Initiate a new legal matter": "కొత్త న్యాయ వ్యవహారాన్ని ప్రారంభించండి",
    "Fill in your case details and choose an advocate.": "మీ కేసు వివరాలను పూరించి న్యాయవాదిని ఎంచుకోండి.",
    "Type of Case / Legal Issue": "కేసు రకం / న్యాయ సమస్య",
    "e.g. Property dispute, Criminal case, Divorce...": "ఉదా. ఆస్తి వివాదం, నేర కేసు, విడాకులు...",
    "Brief Description": "సంక్షిప్త వివరణ",
    "Describe your case in brief...": "మీ కేసును క్లుప్తంగా వివరించండి...",
    "Urgency": "ప్రాధాన్యత",
    "Low": "తక్కువ",
    "Normal": "సాధారణ",
    "High": "ఎక్కువ",
    "Urgent": "అత్యవసరం",
    "Very Urgent": "చాలా అత్యవసరం",
    "Select an Advocate": "న్యాయవాదిని ఎంచుకోండి",
    "Submit Request": "అభ్యర్థనను సమర్పించండి",
    "+ New Matter": "+ కొత్త కేసు",

    # ---- Case detail ----
    "Case Details": "కేసు వివరాలు",
    "Case not found": "కేసు కనుగొనబడలేదు",
    "Case Number: VD001": "కేసు సంఖ్య: VD001",
    "Client: State vs Kumar": "కక్షిదారు: స్టేట్ vs కుమార్",
    "Court: High Court": "కోర్టు: హైకోర్టు",
    "Next Hearing: 12 Jun 2026": "తదుపరి విచారణ: 12 జూన్ 2026",
    "Priority: High": "ప్రాధాన్యత: ఎక్కువ",
    "Hearing History": "విచారణ చరిత్ర",
    "Case ID": "కేసు ఐడి",
    "Case Name": "కేసు పేరు",
    "Case No": "కేసు సంఖ్య",
    "Court": "కోర్టు",
    "Court:": "కోర్టు:",
    "Judge Name": "న్యాయమూర్తి పేరు",
    "Judge Name (Auto-assigned)": "న్యాయమూర్తి పేరు (స్వయంచాలకంగా కేటాయించబడింది)",
    "Hearing Date": "విచారణ తేదీ",
    "Status": "స్థితి",
    "Priority": "ప్రాధాన్యత",
    "Description:": "వివరణ:",
    "Advocate:": "న్యాయవాది:",
    "DD-MM-YYYY": "DD-MM-YYYY",
    "DD Mon YYYY": "DD Mon YYYY",
    "No records": "రికార్డులు లేవు",
    "No records yet": "ఇంకా రికార్డులు లేవు",
    "Save": "సేవ్ చేయండి",
    "Save Settings": "సెట్టింగ్‌లను సేవ్ చేయండి",

    # ---- Matters ----
    "Select case": "కేసును ఎంచుకోండి",
    "Search Cases...": "కేసులను శోధించండి...",

    # ---- Documents ----
    "Choose a case to manage documents": "పత్రాలను నిర్వహించడానికి కేసును ఎంచుకోండి",
    "Select a case above to view or upload its documents":
        "దాని పత్రాలను చూడటానికి లేదా అప్‌లోడ్ చేయడానికి పైన కేసును ఎంచుకోండి",
    "Select a case folder to view documents": "పత్రాలను చూడటానికి కేసు ఫోల్డర్‌ను ఎంచుకోండి",
    "No files yet in this folder. Upload the first one!":
        "ఈ ఫోల్డర్‌లో ఇంకా ఫైళ్ళు లేవు. మొదటి దాన్ని అప్‌లోడ్ చేయండి!",
    "No files yet. Upload the first one!": "ఇంకా ఫైళ్ళు లేవు. మొదటి దాన్ని అప్‌లోడ్ చేయండి!",
    "Upload File": "ఫైల్ అప్‌లోడ్ చేయండి",
    "Upload Document for a Case": "కేసు కోసం పత్రాన్ని అప్‌లోడ్ చేయండి",
    "Folder / category": "ఫోల్డర్ / వర్గం",
    "Client Documents": "కక్షిదారు పత్రాలు",
    "Pick a case and a folder, then upload any file type - PDF, Word (.doc/.docx), Excel, images, text and more.":
        "కేసు మరియు ఫోల్డర్‌ను ఎంచుకుని, ఏదైనా ఫైల్ రకాన్ని అప్‌లోడ్ చేయండి - PDF, Word (.doc/.docx), Excel, చిత్రాలు, వచనం మరియు మరిన్ని.",
    "Merkle-verified document store — PDF, Word, Excel, Images and more":
        "మెర్కిల్-ధృవీకరించబడిన పత్ర నిల్వ — PDF, Word, Excel, చిత్రాలు మరియు మరిన్ని",

    # ---- AI Assistant ----
    "VIDHI AI Assistant": "విధి AI సహాయకుడు",
    "VIDHI AI Assistant Module": "విధి AI సహాయక మాడ్యూల్",
    "Legal AI Chat": "న్యాయ AI చాట్",
    "Ask VIDHI": "విధిని అడగండి",
    "Type your legal question...": "మీ న్యాయ ప్రశ్నను టైప్ చేయండి...",
    "Send Query": "ప్రశ్న పంపండి",
    "Analyze Contract": "ఒప్పందాన్ని విశ్లేషించండి",
    "Summarize Case": "కేసును సంక్షిప్తీకరించండి",
    "Draft Legal Notice": "న్యాయ నోటీసు రూపొందించండి",
    "Generate Petition": "పిటిషన్ రూపొందించండి",
    "Find Relevant Acts": "సంబంధిత చట్టాలను కనుగొనండి",
    "Research Precedents": "పూర్వ తీర్పులను పరిశోధించండి",
    "AI Document Analysis": "AI పత్ర విశ్లేషణ",
    "Document Review Ready": "పత్ర సమీక్ష సిద్ధంగా ఉంది",
    "Risk Score: Low": "ప్రమాద స్కోరు: తక్కువ",
    "Missing Clauses: None": "తప్పిపోయిన నిబంధనలు: ఏవీ లేవు",
    "User: Summarize the employment agreement.": "వినియోగదారు: ఉద్యోగ ఒప్పందాన్ని సంక్షిప్తీకరించండి.",
    "VIDHI AI: This agreement establishes a 24-month employment relationship with confidentiality, termination and dispute resolution clauses.":
        "విధి AI: ఈ ఒప్పందం గోప్యత, రద్దు మరియు వివాద పరిష్కార నిబంధనలతో 24 నెలల ఉద్యోగ సంబంధాన్ని ఏర్పరుస్తుంది.",
    "VIDHI AI: No major legal risks were identified in the uploaded document.":
        "విధి AI: అప్‌లోడ్ చేసిన పత్రంలో పెద్ద న్యాయ ప్రమాదాలు ఏవీ గుర్తించబడలేదు.",
    "• AI confidence score: 96%": "• AI నమ్మక స్కోరు: 96%",
    "• Contract contains standard termination clause.": "• ఒప్పందంలో ప్రామాణిక రద్దు నిబంధన ఉంది.",
    "• Potential compliance risk detected.": "• సంభావ్య నియమ ఉల్లంఘన ప్రమాదం గుర్తించబడింది.",
    "• Relevant acts identified automatically.": "• సంబంధిత చట్టాలు స్వయంచాలకంగా గుర్తించబడ్డాయి.",
    "• Similar judgments found in 3 previous cases.": "• 3 మునుపటి కేసుల్లో ఇలాంటి తీర్పులు కనుగొనబడ్డాయి.",

    # ---- Calendar ----
    "Calendar & Hearings": "క్యాలెండర్ & విచారణలు",

    # ---- Billing ----
    "Manage invoices, payments and financial overview": "ఇన్‌వాయిస్‌లు, చెల్లింపులు మరియు ఆర్థిక సమీక్షను నిర్వహించండి",
    "Track all fee records and make payments": "అన్ని ఫీజు రికార్డులను ట్రాక్ చేసి చెల్లింపులు చేయండి",
    "+ Create Invoice": "+ ఇన్‌వాయిస్ సృష్టించండి",
    "Add Payment": "చెల్లింపు జోడించండి",
    "Create Payment": "చెల్లింపు సృష్టించండి",
    "Confirm Payment": "చెల్లింపును నిర్ధారించండి",
    "Confirm Cash": "నగదును నిర్ధారించండి",
    "Confirm Cash Payment": "నగదు చెల్లింపును నిర్ధారించండి",
    "Confirm Received": "స్వీకరించినట్లు నిర్ధారించండి",
    "Cash Payments Awaiting Your Confirmation": "మీ నిర్ధారణ కోసం ఎదురుచూస్తున్న నగదు చెల్లింపులు",
    "Pay Now": "ఇప్పుడే చెల్లించండి",
    "Pay in cash to your advocate": "మీ న్యాయవాదికి నగదులో చెల్లించండి",
    "Pay via PhonePe / GPay / Paytm": "PhonePe / GPay / Paytm ద్వారా చెల్లించండి",
    "NEFT / IMPS / RTGS bank transfer": "NEFT / IMPS / RTGS బ్యాంక్ బదిలీ",
    "Payment Method": "చెల్లింపు పద్ధతి",
    "Method": "పద్ధతి",
    "Cash": "నగదు",
    "UPI": "UPI",
    "Bank Transfer": "బ్యాంక్ బదిలీ",
    "UPI ID / QR reference": "UPI ఐడి / QR సూచన",
    "Bank reference / UTR number": "బ్యాంక్ సూచన / UTR సంఖ్య",
    "Amount": "మొత్తం",
    "Fee Type": "ఫీజు రకం",
    "Advocate Fee": "న్యాయవాది ఫీజు",
    "Court Fee": "కోర్టు ఫీజు",
    "General Fee": "సాధారణ ఫీజు",
    "Set Payment Deadline": "చెల్లింపు గడువును నిర్ణయించండి",
    "Payment Deadline (e.g. 30 Jun 2025)": "చెల్లింపు గడువు (ఉదా. 30 జూన్ 2025)",
    "Deadline (e.g. 30 Jun 2025)": "గడువు (ఉదా. 30 జూన్ 2025)",
    "Deadline": "గడువు",
    "Date": "తేదీ",
    "Paid On": "చెల్లించిన తేదీ",
    "Payment Added Successfully": "చెల్లింపు విజయవంతంగా జోడించబడింది",
    "Report Type": "నివేదిక రకం",
    "Weekly": "వారానికోసారి",
    "Monthly": "నెలవారీ",
    "Yearly": "వార్షిక",
    "✓ Paid": "✓ చెల్లించబడింది",
    "✔ Payment will be marked Paid instantly.": "✔ చెల్లింపు తక్షణమే చెల్లించినట్లుగా గుర్తించబడుతుంది.",
    "⚠ Cash payments are marked Paid ONLY after your advocate confirms receipt. Status will show 'Pending Confirmation' until then.":
        "⚠ మీ న్యాయవాది రసీదును నిర్ధారించిన తర్వాతే నగదు చెల్లింపులు చెల్లించినట్లుగా గుర్తించబడతాయి. అప్పటి వరకు స్థితి 'నిర్ధారణ పెండింగ్‌లో' అని చూపిస్తుంది.",
    "⏰ Due Date": "⏰ గడువు తేదీ",
    "📅 Deadline": "📅 గడువు",

    # ---- Contacts ----
    "Contact Directory": "పరిచయాల జాబితా",
    "Tap a card to select. You can see their location and contact number.":
        "ఎంచుకోవడానికి కార్డుపై నొక్కండి. మీరు వారి స్థానం మరియు సంప్రదింపు సంఖ్యను చూడవచ్చు.",
    "Advocate Name": "న్యాయవాది పేరు",
    "Senior Advocate": "సీనియర్ న్యాయవాది",
    "Legal Consultant": "న్యాయ సలహాదారు",

    # ---- About ----
    "About VIDHI Legal AI": "విధి లీగల్ AI గురించి",
    "VIDHI Legal AI is an AI-powered legal management platform.":
        "విధి లీగల్ AI అనేది AI ఆధారిత న్యాయ నిర్వహణ వేదిక.",
    "Technology Stack": "సాంకేతిక పరిజ్ఞానం",
    "• Python": "• పైథాన్",
    "• Flet": "• ఫ్లెట్",
    "• VS Code": "• VS కోడ్",
    "Modules": "మాడ్యూళ్ళు",
    "• Dashboard": "• డాష్‌బోర్డ్",
    "• Matters": "• కేసులు",
    "• Documents": "• పత్రాలు",
    "• AI Assistant": "• AI సహాయకుడు",
    "• Calendar": "• క్యాలెండర్",
    "• Billing": "• బిల్లింగ్",
    "• Contacts": "• పరిచయాలు",
    "• Settings": "• సెట్టింగ్‌లు",
    "Version 1.0": "వెర్షన్ 1.0",
    "Developer: Rishi": "డెవలపర్: రిషి",

    # ---- Sample / demo case data (sidebar/cards in code) ----
    "Civil Court": "సివిల్ కోర్టు",
    "District Court": "జిల్లా కోర్టు",
    "High Court": "హైకోర్టు",
    "Property Dispute": "ఆస్తి వివాదం",
    "Property Registration": "ఆస్తి నమోదు",
    "Contract Breach": "ఒప్పంద ఉల్లంఘన",
    "Criminal Appeal": "నేర అప్పీలు",
    "State vs Kumar": "స్టేట్ vs కుమార్",
    "Ramesh Kumar": "రమేష్ కుమార్",
    "Anjali Rao": "అంజలి రావు",
    "Adv. Sharma": "న్యాయవాది శర్మ",

    # ---- Generic / Misc ----
    "Action": "చర్య",
    "Close": "మూసివేయి",
    "Confirm": "నిర్ధారించండి",
    "Clear": "క్లియర్ చేయండి",
    "—": "—",
    "Case": "కేసు",
    "Pay": "చెల్లించు",
    "Amount due": "చెల్లించాల్సిన మొత్తం",
    "Click to view details": "వివరాలు చూడటానికి క్లిక్ చేయండి",
    "Pending Review": "సమీక్ష పెండింగ్‌లో",
    "Merkle root": "మెర్కిల్ రూట్",
    "Cannot open": "తెరవలేకపోయింది",

    # ---- Dynamic status / confirmation messages ----
    "✔ Deadline saved.": "✔ గడువు సేవ్ చేయబడింది.",
    "Rejected": "తిరస్కరించబడింది",
    "✔ UPI payment successful! Marked as Paid.": "✔ UPI చెల్లింపు విజయవంతమైంది! చెల్లించినట్లు గుర్తించబడింది.",
    "✔ Bank Transfer recorded! Marked as Paid.": "✔ బ్యాంక్ బదిలీ నమోదైంది! చెల్లించినట్లు గుర్తించబడింది.",
    "⏳ Cash recorded. Awaiting advocate confirmation.": "⏳ నగదు నమోదైంది. న్యాయవాది నిర్ధారణ కోసం ఎదురుచూస్తోంది.",
    "Please enter the type of case.": "దయచేసి కేసు రకాన్ని నమోదు చేయండి.",
    "Please select an advocate.": "దయచేసి న్యాయవాదిని ఎంచుకోండి.",

    # ---- Document folder categories ----
    "Identity Documents": "గుర్తింపు పత్రాలు",
    "Case Documents": "కేసు పత్రాలు",
    "Evidence Files": "సాక్ష్యాధార ఫైళ్ళు",
    "Supporting Documents": "మద్దతు పత్రాలు",
    "Complaints & Notices": "ఫిర్యాదులు & నోటీసులు",
}


def t(text):
    """
    Translate text to Telugu if Telugu is the active language,
    otherwise return the original (English) text unchanged.
    Falls back to the original text if no translation is found.
    """
    if text is None:
        return text
    if LANG["code"] == "te":
        return TRANSLATIONS.get(text, text)
    return text
