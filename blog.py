"""Blog of the Nouveau Cap website: reads content/blog/*.md and writes the article pages, the blog index
and the RSS feed. Articles use a small Markdown subset (## and ### headings, paragraphs, - and 1. lists,
**bold**, [links](url), | tables |) after a header block (title, description, slug, keyword, updated)
closed by a line with three dashes. Standard library only.
"""
import html
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
BLOG_DIR = ROOT / "content" / "blog"
MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
esc = html.escape


def french_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def inline(text):
    """Escapes text, then applies **bold** and [links](url). Internal links stay relative."""
    out = esc(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)

    def link(m):
        label, url = m.group(1), html.unescape(m.group(2))
        ext = url.startswith("http")
        attrs = ' rel="noopener"' if ext else ""
        return f'<a href="{esc(url)}"{attrs}>{label}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, out)


def slugify(text):
    t = text.lower()
    for a, b in (("àâä", "a"), ("éèêë", "e"), ("îï", "i"), ("ôö", "o"), ("ùûü", "u"), ("ç", "c")):
        for ch in a:
            t = t.replace(ch, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60]


def markdown(md, widgets):
    """Converts the article Markdown subset to HTML. Returns (html, toc, faq)."""
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    lines = md.splitlines()
    out, toc, faq = [], [], []
    para, i = [], 0
    section = ""

    def flush():
        if para:
            text = " ".join(p.strip() for p in para)
            out.append(f"<p>{inline(text)}</p>")
            if section == "faq" and faq and not faq[-1][1]:
                faq[-1][1] = text
            para.clear()

    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()
        if not s:
            flush(); i += 1; continue
        if s in widgets:
            flush(); out.append(widgets[s]); i += 1; continue
        if s.startswith("### "):
            flush()
            title = s[4:].strip()
            out.append(f"<h3>{inline(title)}</h3>")
            if section == "faq":
                faq.append([re.sub(r"\*\*|\[|\]\([^)]*\)", "", title), ""])
            i += 1; continue
        if s.startswith("## "):
            flush()
            title = s[3:].strip()
            anchor = slugify(title)
            out.append(f'<h2 id="{anchor}">{inline(title)}</h2>')
            toc.append((anchor, title))
            section = "faq" if "questions fr" in title.lower() else ""
            i += 1; continue
        if s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                    rows.append(cells)
                i += 1
            head, body = rows[0], rows[1:]
            t = '<div class="table"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            t += "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(t + "</tbody></table></div>")
            continue
        m_ul, m_ol = re.match(r"^[-*] (.+)", s), re.match(r"^\d+[.)] (.+)", s)
        if m_ul or m_ol:
            flush()
            tag = "ul" if m_ul else "ol"
            items = []
            while i < len(lines):
                t = lines[i].strip()
                m = re.match(r"^[-*] (.+)", t) if tag == "ul" else re.match(r"^\d+[.)] (.+)", t)
                if m:
                    items.append(m.group(1)); i += 1
                elif t and lines[i].startswith(("  ", "\t")) and items:
                    items[-1] += " " + t; i += 1
                else:
                    break
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            if section == "faq" and faq and not faq[-1][1]:
                faq[-1][1] = " ".join(items)
            continue
        para.append(line); i += 1
    flush()
    return "\n".join(out), toc, [(q, a) for q, a in faq if a]


def nbsp(text):
    """French typography: a non-breaking space before : ; ? ! and inside « », so no line starts with them."""
    text = re.sub(r" ([:;?!»])", " \\1", text)
    return text.replace("« ", "« ")


def read_articles():
    arts = []
    for f in sorted(BLOG_DIR.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        head, _, body = text.partition("\n---\n")
        meta = dict(l.split(": ", 1) for l in head.strip().splitlines() if ": " in l)
        for k in ("title", "description"):
            meta[k] = nbsp(meta.get(k, ""))
        meta["body"] = nbsp(body.strip())
        meta["order"] = int(meta.get("order", "99"))
        meta["words"] = len(re.findall(r"\w+", body))
        arts.append(meta)
    return sorted(arts, key=lambda a: a["order"])


CALCULATOR = """<div class="calc glass" data-calc>
  <p class="eyebrow">Calculateur</p>
  <h3>Combien de mois pouvez-vous tenir&nbsp;?</h3>
  <p class="note">Saisissez vos montants mensuels. Le calcul se fait sur votre appareil : rien n’est envoyé.</p>
  <div class="calc-grid">
    <label>Épargne que vous pouvez mobiliser<input type="number" inputmode="decimal" min="0" step="100" name="savings" value="40000"><span class="unit">€</span></label>
    <label>Montant à garder de côté quoi qu’il arrive <input type="number" inputmode="decimal" min="0" step="100" name="reserve" value="5000"><span class="unit">€</span></label>
    <label>Dépenses du foyer par mois <input type="number" inputmode="decimal" min="0" step="50" name="expenses" value="3200"><span class="unit">€</span></label>
    <label>Allocation chômage (ARE) par mois <input type="number" inputmode="decimal" min="0" step="50" name="are" value="2100"><span class="unit">€</span></label>
    <label>Mois de droits ARE restants <input type="number" inputmode="numeric" min="0" step="1" name="months" value="18"><span class="unit">mois</span></label>
    <label>Autres revenus du foyer par mois <input type="number" inputmode="decimal" min="0" step="50" name="income" value="0"><span class="unit">€</span></label>
  </div>
  <div class="calc-out" aria-live="polite">
    <p class="calc-big"><span data-out="runway">…</span></p>
    <p data-out="detail"></p>
  </div>
  <p class="note">Valeurs par défaut : un exemple fictif, à remplacer par les vôtres. Les montants et la durée de vos droits ARE sont ceux indiqués par France Travail : ce calculateur ne les calcule pas. Il ne tient pas compte des impôts à venir ni des dépenses exceptionnelles.</p>
</div>"""

WIDGETS = {"[[CALCULATEUR]]": CALCULATOR}
