"""Nouveau Cap guides: turns content/guides/*.html into printable pages in build/guides/, which
scripts/guides-pdf.js prints to docs/guides/<slug>.pdf (A4). One guide per blog article, 4 or 5 pages.

A guide file starts with header lines (title, subtitle, slug, article, updated, short), then a line with
three dashes, then the HTML body made of <section class="page"> blocks (classes in guides/guide.css).
Standard library only.
"""
import html
import re
from pathlib import Path

from blog import french_date, nbsp

ROOT = Path(__file__).parent
SRC = ROOT / "content" / "guides"
OUT = ROOT / "build" / "guides"


def french_text(fragment):
    """Applies French non-breaking spaces to the text between tags, never inside a tag."""
    parts = re.split(r"(<[^>]+>)", fragment)
    return "".join(p if p.startswith("<") else nbsp(p) for p in parts)


def read_guides():
    guides = []
    for f in sorted(SRC.glob("*.html")):
        head, _, body = f.read_text(encoding="utf-8").partition("\n---\n")
        meta = dict(l.split(": ", 1) for l in head.strip().splitlines() if ": " in l)
        meta["body"] = body.strip()
        guides.append(meta)
    return guides


PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="short" content="{short}">
<link rel="stylesheet" href="/guides/guide.css">
</head>
<body>
{body}
</body>
</html>
"""


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    guides = read_guides()
    for g in guides:
        body = g["body"].replace("{{updated}}", french_date(g["updated"]))
        (OUT / f"{g['slug']}.html").write_text(PAGE.format(
            title=html.escape(nbsp(g["title"])), short=html.escape(g.get("short", g["title"])),
            body=french_text(body)), encoding="utf-8")
    return guides


if __name__ == "__main__":
    print(f"{len(build())} guide(s) written to build/guides/")
