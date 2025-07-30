import re
import requests # type: ignore
from rich.console import Console # type: ignore
from rich.panel import Panel # type: ignore
from rich.align import Align # type: ignore

def is_valid_username(username):
    return re.match(r"^[a-zA-Z0-9_]{3,20}$", username) is not None

def is_valid_password(password):
    return len(password) >= 8

API_BASE_URL = "https://glyph-sh.pizzalover125.hackclub.app/api"

def api_request(method, endpoint, data=None):
    url = f"{API_BASE_URL}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        
        return response.json()
    except requests.exceptions.RequestException:
        return {"success": False, "message": "Connection error"}
    
def pad_panel_to_height(panel, height):
    rendered = Console().render_str(str(panel))
    lines = str(panel).splitlines()
    current_height = len(lines)
    missing_lines = height - current_height
    content = Align.center(panel.renderable, vertical="top", height=height)
    return Panel(
        content,
        title=panel.title,
        border_style=panel.border_style,
        box=panel.box,
        padding=panel.padding
    )








"""
## 3.11: Balancing Majority and Minority Rights
- Objective: Explain how gov has responded to social movements. Explain how SCOTUS allowed restriction of civil rights of minority groups and other times has protected them.
- Civil Rights Movement's goal was to end racial segregation.
- Key SCOTUS cases:
    - Plessy v Ferguson (1896) upheld "separate but equal" doctrine, allowing racial segregation.
        - Separate but equal doctrine was used to justify segregation in public facilities.
        - Restriction of minority civil rights.
    - Brown v Board of Education (1954) overturned Plessy, declaring segregation in public schools unconstitutional. (see below)
        - Upheld minority rights.
- Key Congress legislation:
    - Civil Rights Act of 1964 prohibited discrimination based on race.
    - Voting Rights Act of 1965 aimed to eliminate barriers to voting for African Americans
    - 24th Amendment (1964) abolished poll taxes in federal elections, removing a barrier to voting.
    - Title IX of the Education Amendments of 1972 prohibited discrimination based on gender and race.
        - Caused a boom in female college sports.
- Majority-Minority Rights:
    - Congressional district where majority groups are minorities
    - Thornburg v Gingles (1986) established criteria for determining if districting dilutes minority voting strength. (minority rights upheld)
    - Shaw v Reno (1993) ruled that racial gerrymandering is unconstitutional. (see required document) (majority rights upheld)

"""