"""Build index.html from src/template.html.

Pulls the four tier badges (embedded images) and the Club Policy text out of the
previous index.html (or src/assets if present), applies policy edits, and writes index.html.
Run:  python3 -I src/build.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
ASSETS = os.path.join(SRC, "assets")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


# --- first run: save badges + policy from the old page so later builds don't depend on it
if not os.path.isdir(ASSETS):
    old = read(os.path.join(ROOT, "index.html"))
    os.makedirs(ASSETS)
    for tier in ("Bogey", "Par", "Birdie", "Eagle"):
        m = re.search(r'<img class="badge" src="(data:[^"]+)" alt="%s membership badge">' % tier, old)
        if not m:
            sys.exit("badge not found: " + tier)
        write(os.path.join(ASSETS, tier.lower() + ".datauri"), m.group(1))
    m = re.search(r'<details class="full" id="policy">.*?<div class="pol-body">(.*?)</div>\s*</details>', old, re.S)
    if not m:
        sys.exit("policy not found")
    write(os.path.join(ASSETS, "policy.html"), m.group(1).strip())

policy = read(os.path.join(ASSETS, "policy.html"))

# --- policy edits (guests are per DAY; no guest passes during events)
edits = [
    ("Effective October 15, 2026", "Effective October 26, 2026"),
    ("<li>Any free guest allowance depends on your tier and applies per booking. Other guests are charged at the posted guest rate and must be paid for before play.</li>",
     "<li>Any free guest allowance depends on your tier and applies per day. Other guests are charged at the posted guest rate and must be paid for before play. Guests are welcome any time the club is open, except that guest passes are not accepted during events such as Thursday Night Skins, leagues and tournaments.</li>"),
]
for a, b in edits:
    if a in policy:
        policy = policy.replace(a, b)
    elif b not in policy:
        sys.exit("policy edit target missing: " + a[:60])

page = read(os.path.join(SRC, "template.html"))
page = page.replace("{{POLICY}}", policy)
for tier in ("bogey", "par", "birdie", "eagle"):
    page = page.replace("{{BADGE_%s}}" % tier.upper(), read(os.path.join(ASSETS, tier + ".datauri")))
left = re.findall(r"\{\{[A-Z_]+\}\}", page)
if left:
    sys.exit("unfilled placeholders: %s" % left)
write(os.path.join(ROOT, "index.html"), page)
print("index.html written, %d bytes" % len(page.encode()))
