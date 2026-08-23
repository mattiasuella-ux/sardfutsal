from pathlib import Path
import re
import html
from datetime import datetime


ROOT = Path(".")
MATCHES_DIR = ROOT / "content" / "matches"
INDEX_FILE = ROOT / "index.html"


def parse_frontmatter(text):
    data = {}
    body = text

    if text.startswith("---"):
        parts = text.split("---", 2)

        if len(parts) == 3:
            frontmatter = parts[1]
            body = parts[2].strip()

            for line in frontmatter.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)

                    data[key.strip()] = (
                        value.strip()
                        .strip('"')
                        .strip("'")
                    )

    return data, body


def format_date(date_string):
    try:
        date = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        )

        months = {
            1: "GEN",
            2: "FEB",
            3: "MAR",
            4: "APR",
            5: "MAG",
            6: "GIU",
            7: "LUG",
            8: "AGO",
            9: "SET",
            10: "OTT",
            11: "NOV",
            12: "DIC",
        }

        return (
            f"{date.day:02d} "
            f"{months[date.month]} "
            f"{date.year}"
        )

    except Exception:
        return date_string


# =========================================================
# LEGGI LE PARTITE DAL CMS
# =========================================================

matches = []

if MATCHES_DIR.exists():

    for file in MATCHES_DIR.glob("*.md"):

        text = file.read_text(
            encoding="utf-8"
        )

        data, body = parse_frontmatter(text)

        matches.append({
            "date": data.get("date", ""),
            "time": data.get("time", ""),
            "competition": data.get("competition", ""),
            "opponent": data.get("opponent", ""),
            "venue": data.get("venue", ""),
            "home_away": data.get("home_away", "Casa"),
            "status": data.get("status", "Da giocare"),
            "sard_goals": data.get("sard_goals", ""),
            "opponent_goals": data.get("opponent_goals", ""),
            "opponent_logo": data.get("opponent_logo", ""),
        })


# =========================================================
# ORDINA PER DATA
# =========================================================

matches.sort(
    key=lambda match: match["date"]
)


# =========================================================
# GENERA LE PARTITE
# =========================================================

rows = []

for match in matches:

    date = html.escape(
        format_date(match["date"])
    )

    time = html.escape(
        match["time"]
    )

    competition = html.escape(
        match["competition"]
    )

    opponent = html.escape(
        match["opponent"]
    )

    venue = html.escape(
        match["venue"]
    )

    status = html.escape(
        match["status"]
    )

    sard_goals = html.escape(
        str(match["sard_goals"])
    )

    opponent_goals = html.escape(
        str(match["opponent_goals"])
    )

    logo = match["opponent_logo"]

    if logo.startswith("/"):
        logo = logo[1:]

    logo = html.escape(
        logo,
        quote=True
    )

    # -----------------------------------------
    # STATO PARTITA
    # -----------------------------------------

    if status == "Da giocare":

        score = "—"
        status_class = "upcoming"
        status_text = "DA GIOCARE"

    elif status == "Vittoria":

        score = (
            f"{sard_goals} - "
            f"{opponent_goals}"
        )

        status_class = "win"
        status_text = "VITTORIA"

    elif status == "Pareggio":

        score = (
            f"{sard_goals} - "
            f"{opponent_goals}"
        )

        status_class = "draw"
        status_text = "PAREGGIO"

    else:

        score = (
            f"{sard_goals} - "
            f"{opponent_goals}"
        )

        status_class = "loss"
        status_text = "SCONFITTA"


    # -----------------------------------------
    # LOGO AVVERSARIO
    # -----------------------------------------

    logo_html = ""

    if logo:

        logo_html = f"""
        <img
          class="match-opponent-logo"
          src="{logo}"
          alt="{opponent}"
          loading="lazy"
        >
        """


    # -----------------------------------------
    # CARD PARTITA
    # -----------------------------------------

    rows.append(f"""
      <div class="table-row match-row {status_class}">

        <span class="match-date">
          {date}
        </span>

        <span class="match-info">

          <strong>
            {opponent}
          </strong>

          <small>
            {competition}
          </small>

        </span>

        <span class="match-score">
          {score}
        </span>

        <span class="match-status">
          {status_text}
        </span>

      </div>
""")


# =========================================================
# NESSUNA PARTITA
# =========================================================

if not rows:

    generated_matches = """
    <div class="season-status">

      <div class="season-status-icon"></div>

      <div class="season-status-content">

        <p class="status-label">
          CALENDARIO IN AGGIORNAMENTO
        </p>

        <h3>
          Pronti per una nuova stagione.
        </h3>

        <p>
          Il calendario ufficiale della stagione
          2026/27 sarà pubblicato non appena
          saranno definiti girone, avversarie
          e date delle gare.
        </p>

      </div>

    </div>
    """

else:

    generated_matches = "\n".join(rows)


# =========================================================
# AGGIORNA INDEX.HTML
# =========================================================

if not INDEX_FILE.exists():

    raise SystemExit(
        "ERRORE: index.html non trovato."
    )


html_content = INDEX_FILE.read_text(
    encoding="utf-8"
)


start_marker = (
    "<!-- MATCHES_AUTO_START -->"
)

end_marker = (
    "<!-- MATCHES_AUTO_END -->"
)


if (
    start_marker not in html_content
    or
    end_marker not in html_content
):

    raise SystemExit(
        "ERRORE: marcatori "
        "MATCHES_AUTO_START / MATCHES_AUTO_END "
        "non trovati in index.html"
    )


pattern = (
    re.escape(start_marker)
    + r".*?"
    + re.escape(end_marker)
)


replacement = (
    start_marker
    + "\n"
    + generated_matches
    + "\n"
    + end_marker
)


new_html = re.sub(
    pattern,
    replacement,
    html_content,
    flags=re.DOTALL
)


INDEX_FILE.write_text(
    new_html,
    encoding="utf-8"
)


print(
    f"Partite lette dal CMS: {len(matches)}"
)

print(
    "Calendario aggiornato correttamente."
)
