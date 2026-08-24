from pathlib import Path
import re
import html
from datetime import datetime


ROOT = Path(".")
MATCHES_DIR = ROOT / "content" / "matches"
INDEX_FILE = ROOT / "index.html"


# =========================================================
# FRONTMATTER
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
    i = 0

    while i < len(lines):
        line = lines[i]

        if ":" not in line:
            i += 1
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value in ("|", "|-"):
            multiline = []
            i += 1

            while i < len(lines):
                next_line = lines[i]

                if (
                    next_line
                    and not next_line.startswith(" ")
                    and ":" in next_line
                ):
                    break

                multiline.append(next_line.strip())
                i += 1

            data[key] = "\n".join(item for item in multiline if item)
            continue

        data[key] = value.strip('"').strip("'")
        i += 1

    return data, body


# =========================================================
# DATA
# =========================================================

def format_date(date_string):
    if not date_string:
        return {"day": "", "month": "", "year": ""}

    try:
        date = datetime.strptime(date_string, "%Y-%m-%d")
        months = {
            1: "GEN", 2: "FEB", 3: "MAR", 4: "APR",
            5: "MAG", 6: "GIU", 7: "LUG", 8: "AGO",
            9: "SET", 10: "OTT", 11: "NOV", 12: "DIC"
        }

        return {
            "day": f"{date.day:02d}",
            "month": months[date.month],
            "year": str(date.year)
        }
    except ValueError:
        return {"day": date_string, "month": "", "year": ""}


# =========================================================
# PERCORSI IMMAGINI
# =========================================================

def clean_image_path(image):
    if not image:
        return ""

    image = str(image).strip()
    if image.startswith("/"):
        image = image[1:]

    return html.escape(image, quote=True)


# =========================================================
# LEGGI LE PARTITE
# =========================================================

matches = []

if MATCHES_DIR.exists():
    for file in sorted(MATCHES_DIR.glob("*.md")):
        text = file.read_text(encoding="utf-8")
        data, body = parse_frontmatter(text)

        matches.append({
            "date": data.get("date", ""),
            "time": data.get("time", ""),
            "competition": data.get("competition", ""),
            "opponent": data.get("opponent", ""),
            "venue": data.get("venue", ""),
            "home_away": data.get("home_away", "Casa"),
            "sard_goals": data.get("sard_goals", "-1"),
            "opponent_goals": data.get("opponent_goals", "-1"),
            "scorers": data.get("scorers", ""),
            "home_logo": data.get("home_logo", ""),
            "away_logo": data.get("away_logo", "")
        })


# =========================================================
# ORDINA PER DATA
# =========================================================

matches.sort(key=lambda match: match["date"])


# =========================================================
# GENERAZIONE CARD
# =========================================================

cards = []
first_next_found = False

for match in matches:
    date = format_date(match["date"])
    day = html.escape(date["day"])
    month = html.escape(date["month"])
    year = html.escape(date["year"])

    time = html.escape(str(match["time"]))
    competition = html.escape(str(match["competition"]))
    opponent = html.escape(str(match["opponent"]))

    try:
        sard_goals_value = int(str(match["sard_goals"]).strip())
    except (ValueError, TypeError):
        sard_goals_value = -1

    try:
        opponent_goals_value = int(str(match["opponent_goals"]).strip())
    except (ValueError, TypeError):
        opponent_goals_value = -1

    extra_card_class = ""

    if sard_goals_value == -2 and opponent_goals_value == -2:
        match_label = "CALENDARIO IN AGGIORNAMENTO"
        card = f"""
        <div class="match-card-wrapper">
            <div class="match-card-label">{match_label}</div>
            <article class="match-card match-card-update">
                <div class="match-card-image-container">
                    <img src="images/calendario-aggiornamento.png" alt="Calendario in aggiornamento" class="calendar-update-image">
                </div>
            </article>
        </div>
        """
        cards.append(card)
        continue

    elif sard_goals_value >= 0 and opponent_goals_value >= 0:
        match_label = "RISULTATO FINALE"
        score = f"{sard_goals_value} - {opponent_goals_value}"
    else:
        if not first_next_found:
            match_label = "PROSSIMO IMPEGNO • NEXT MATCH"
            extra_card_class = "is-next-match"
            first_next_found = True
        else:
            match_label = "PROSSIMA PARTITA"
        score = "VS"

    if match["home_away"] == "Casa":
        home_name = "SARD FUTSAL"
        away_name = opponent
    else:
        home_name = opponent
        away_name = "SARD FUTSAL"

    home_name = html.escape(home_name)
    away_name = html.escape(away_name)

    home_logo = clean_image_path(match["home_logo"])
    away_logo = clean_image_path(match["away_logo"])

    home_logo_html = f'<img src="{home_logo}" alt="{home_name}" class="match-team-logo" loading="lazy">' if home_logo else '<div class="match-team-logo-placeholder"></div>'
    away_logo_html = f'<img src="{away_logo}" alt="{away_name}" class="match-team-logo" loading="lazy">' if away_logo else '<div class="match-team-logo-placeholder"></div>'

    scorers_raw = str(match["scorers"]).strip()
    home_scorers = []
    away_scorers = []

    if scorers_raw:
        for item in re.split(r"\r?\n|;", scorers_raw):
            item = item.strip()
            if not item:
                continue

            if ":" in item:
                side, scorer = item.split(":", 1)
                side = side.strip().upper()
                scorer = scorer.strip()

                if side == "CASA":
                    home_scorers.append(html.escape(scorer))
                elif side == "OSPITE":
                    away_scorers.append(html.escape(scorer))
            else:
                home_scorers.append(html.escape(item))

    home_scorers_html = f'<div class="match-scorers-home">{"".join(f"<span>{item}</span>" for item in home_scorers)}</div>' if home_scorers else ""
    away_scorers_html = f'<div class="match-scorers-away">{"".join(f"<span>{item}</span>" for item in away_scorers)}</div>' if away_scorers else ""

    card = f"""
    <div class="match-card-wrapper {extra_card_class}">
        <div class="match-card-label">{match_label}</div>
        <article class="match-card">
            <div class="match-main">
                <div class="match-competition">{competition}</div>
                <div class="match-date-column">
                    <div class="match-date">
                        <span class="match-date-day">{day}</span>
                        <span class="match-date-month">{month}</span>
                        <span class="match-date-year">{year}</span>
                    </div>
                    <span class="match-date-time">{time if time else "—"}</span>
                </div>
                <div class="match-teams">
                    <div class="match-team">
                        {home_logo_html}
                        <h3>{home_name}</h3>
                    </div>
                    <div class="match-vs">
                        <span></span>
                        <div class="match-vs-center">
                            <span class="match-time">{score}</span>
                        </div>
                        <span></span>
                    </div>
                    <div class="match-team">
                        {away_logo_html}
                        <h3>{away_name}</h3>
                    </div>
                </div>
                <div class="match-scorers-row">
                    {home_scorers_html}
                    <div class="match-scorers-spacer"></div>
                    {away_scorers_html}
                </div>
            </div>
        </article>
    </div>
    """
  


# =========================================================
# SE NON CI SONO PARTITE
# =========================================================

if not cards:
    generated_matches = """
    <div class="season-status">
        <div class="season-status-icon"></div>
        <div class="season-status-content">
            <p class="status-label">CALENDARIO IN AGGIORNAMENTO</p>
            <h3>Pronti per una nuova stagione.</h3>
            <p>Il calendario ufficiale della stagione 2026/27 sarà pubblicato non appena saranno definiti girone, avversarie e date delle gare.</p>
        </div>
    </div>
    """
else:
    generated_matches = "\n".join(cards)


# =========================================================
# CONTROLLO E AGGIORNAMENTO INDEX.HTML
# =========================================================

if not INDEX_FILE.exists():
    raise SystemExit("ERRORE: index.html non trovato.")

html_content = INDEX_FILE.read_text(encoding="utf-8")

start_marker = "<!-- MATCHES_AUTO_START -->"
end_marker = "<!-- MATCHES_AUTO_END -->"

if start_marker not in html_content or end_marker not in html_content:
    raise SystemExit("ERRORE: marcatori MATCHES_AUTO_START / MATCHES_AUTO_END non trovati in index.html")

pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)
replacement = start_marker + "\n" + generated_matches + "\n" + end_marker

new_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
INDEX_FILE.write_text(new_html, encoding="utf-8")

print()
print("=" * 50)
print("SARD FUTSAL - GENERAZIONE CALENDARIO")
print("=" * 50)
print(f"Partite trovate: {len(matches)}")
print(f"Card generate: {len(cards)}")
print("Calendario aggiornato correttamente.")
print("=" * 50)
