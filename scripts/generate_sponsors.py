from pathlib import Path
import re
import html


ROOT = Path(".")
SPONSORS_DIR = ROOT / "content" / "sponsors"
INDEX_FILE = ROOT / "index.html"


# =========================================================
# LETTURA FRONTMATTER
# =========================================================

def parse_frontmatter(text):

    data = {}
    body = text

    if not text.startswith("---"):
        return data, body

    parts = text.split("---", 2)

    if len(parts) != 3:
        return data, body

    frontmatter = parts[1]
    body = parts[2].strip()

    lines = frontmatter.splitlines()
    last_key = None

    key_line = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*:")

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if not key_line.match(stripped):
            if last_key is not None:
                data[last_key] = (data[last_key] + " " + stripped).strip()
            continue

        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        data[key] = value
        last_key = key

    return data, body


# =========================================================
# LETTURA SPONSOR DAL CMS
# =========================================================

sponsors = []


if SPONSORS_DIR.exists():

    for file in SPONSORS_DIR.glob("*.md"):

        text = file.read_text(encoding="utf-8")

        data, body = parse_frontmatter(text)

        name = data.get("name", file.stem)
        logo = data.get("logo", "")
        website = data.get("website", "")

        try:
            order = int(data.get("order", "0"))
        except ValueError:
            order = 0

        sponsors.append({
            "name": name,
            "logo": logo,
            "website": website,
            "order": order,
        })


sponsors.sort(key=lambda s: s["order"])


# =========================================================
# GENERA I LOGHI (DUPLICATI PER LO SCORRIMENTO CONTINUO)
# =========================================================

def build_logo_html(sponsor):

    logo = sponsor["logo"]

    if logo.startswith("/"):
        logo = logo[1:]

    logo = html.escape(logo, quote=True)
    name = html.escape(sponsor["name"], quote=True)
    website = sponsor.get("website", "").strip()

    img_tag = f'<img src="{logo}" alt="{name}">'

    if website:
        website_escaped = html.escape(website, quote=True)
        inner = f'<a href="{website_escaped}" target="_blank" rel="noopener">{img_tag}</a>'
    else:
        inner = img_tag

    return f'''
        <div class="partner-logo">
          {inner}
        </div>
'''


logos_html = "".join(build_logo_html(s) for s in sponsors)

# Il set viene duplicato una seconda volta per l'effetto di scorrimento continuo (marquee)
generated_track = logos_html + logos_html


# =========================================================
# AGGIORNA INDEX.HTML
# =========================================================

if not INDEX_FILE.exists():
    raise SystemExit("ERRORE: index.html non trovato.")


html_content = INDEX_FILE.read_text(encoding="utf-8")


start_marker = "<!-- SPONSORS_AUTO_START -->"
end_marker = "<!-- SPONSORS_AUTO_END -->"


if start_marker not in html_content or end_marker not in html_content:
    raise SystemExit(
        "ERRORE: marcatori SPONSORS_AUTO_START / SPONSORS_AUTO_END "
        "non trovati in index.html"
    )


pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)

replacement = start_marker + "\n" + generated_track + "\n" + end_marker

new_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

INDEX_FILE.write_text(new_html, encoding="utf-8")

print(f"Sponsor letti dal CMS: {len(sponsors)}")
print("Striscia sponsor aggiornata correttamente.")
