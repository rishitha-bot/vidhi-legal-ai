# Shared mock case data used across the dashboard, active cases list,
# and case detail pages. Keeping this centralized makes it easy for
# your friend to later replace with real DB data.

CASES = [
    {
        "case_id": "VD001",
        "case_name": "State vs Kumar",
        "hearing_date": "12 Jun 2026",
        "court": "High Court",
        "judge": "Justice Sharma",
        "win_probability": 82,
        "status": "Active",
        "client": "Mr. Kumar",
        "case_type": "Criminal",
        "filed_date": "02 Jan 2026",
        "next_hearing": "12 Jun 2026",
        "hearing_history": [
            {"date": "02 Jan 2026", "note": "Case filed", "win_probability": 60},
            {"date": "15 Feb 2026", "note": "First hearing - evidence submitted", "win_probability": 68},
            {"date": "10 Apr 2026", "note": "Witness examination", "win_probability": 75},
            {"date": "12 Jun 2026", "note": "Arguments scheduled", "win_probability": 82},
        ],
    },
    {
        "case_id": "VD002",
        "case_name": "Property Dispute",
        "hearing_date": "14 Jun 2026",
        "court": "District Court",
        "judge": "Justice Rao",
        "win_probability": 67,
        "status": "Active",
        "client": "Mrs. Reddy",
        "case_type": "Civil",
        "filed_date": "10 Feb 2026",
        "next_hearing": "14 Jun 2026",
        "hearing_history": [
            {"date": "10 Feb 2026", "note": "Case filed", "win_probability": 55},
            {"date": "20 Mar 2026", "note": "Title documents reviewed", "win_probability": 60},
            {"date": "14 Jun 2026", "note": "Hearing on possession claim", "win_probability": 67},
        ],
    },
    {
        "case_id": "VD003",
        "case_name": "Contract Breach",
        "hearing_date": "16 Jun 2026",
        "court": "Civil Court",
        "judge": "Justice Kumar",
        "win_probability": 74,
        "status": "Active",
        "client": "Sharma Traders",
        "case_type": "Commercial",
        "filed_date": "05 Mar 2026",
        "next_hearing": "16 Jun 2026",
        "hearing_history": [
            {"date": "05 Mar 2026", "note": "Case filed", "win_probability": 65},
            {"date": "18 Apr 2026", "note": "Contract terms reviewed", "win_probability": 70},
            {"date": "16 Jun 2026", "note": "Final arguments", "win_probability": 74},
        ],
    },
    {
        "case_id": "VD004",
        "case_name": "Property Registration",
        "hearing_date": "18 Jun 2026",
        "court": "District Court",
        "judge": "Justice Reddy",
        "win_probability": 91,
        "status": "Active",
        "client": "Mr. Naidu",
        "case_type": "Civil",
        "filed_date": "12 Jan 2026",
        "next_hearing": "18 Jun 2026",
        "hearing_history": [
            {"date": "12 Jan 2026", "note": "Case filed", "win_probability": 80},
            {"date": "25 Feb 2026", "note": "Document verification", "win_probability": 85},
            {"date": "18 Jun 2026", "note": "Final registration hearing", "win_probability": 91},
        ],
    },
    {
        "case_id": "VD005",
        "case_name": "Cheque Bounce Case",
        "hearing_date": "19 Jun 2026",
        "court": "Magistrate Court",
        "judge": "Justice Singh",
        "win_probability": 58,
        "status": "Active",
        "client": "Mr. Verma",
        "case_type": "Criminal",
        "filed_date": "01 Apr 2026",
        "next_hearing": "19 Jun 2026",
        "hearing_history": [
            {"date": "01 Apr 2026", "note": "Case filed", "win_probability": 50},
            {"date": "10 May 2026", "note": "Notice served to defendant", "win_probability": 54},
            {"date": "19 Jun 2026", "note": "Reply hearing", "win_probability": 58},
        ],
    },
]


# Monthly win-rate trend used in the Case Performance line chart.
WIN_RATE_TREND = [
    {"month": "Jan", "win_rate": 70},
    {"month": "Feb", "win_rate": 73},
    {"month": "Mar", "win_rate": 75},
    {"month": "Apr", "win_rate": 78},
    {"month": "May", "win_rate": 80},
    {"month": "Jun", "win_rate": 86},
]


def get_case_by_id(case_id):
    for c in CASES:
        if c["case_id"] == case_id:
            return c
    return None


def get_active_cases():
    return [c for c in CASES if c["status"] == "Active"]
