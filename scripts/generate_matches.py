from pathlib import Path
import re
import html
from datetime import datetime


ROOT = Path(".")
MATCHES_DIR = ROOT / "content" / "matches"
INDEX_FILE = ROOT / "index.html"

# Logo Sard Futsal
SARD_FUTSAL_LOGO = "LogoaggiornatoSardFutsal.png"


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
# LEGGI PARTITE DAL CMS
# =========================================================

matches = []


if MATCHES_DIR.exists():

    for file in MATCHES_DIR.glob("*.md"):

        text = file.read_text(
            encoding="utf-8"
        )

        data, body = parse_frontmatter(text)

        matches.append({

            "date": data.get(
                "date",
                ""
            ),

            "time": data.get(
                "time",
                ""
            ),

            "competition": data.get(
                "competition",
                ""
            ),

            "opponent": data.get(
                "opponent",
                ""
            ),

            "venue": data.get(
                "venue",
                ""
            ),

            "home_away": data.get(
                "home_away",
                "Casa"
            ),

            "status": data.get(
                "status",
                "Da giocare"
            ),

            "sard_goals": data.get(
                "sard_goals",
                ""
            ),

            "opponent_goals": data.get(
                "opponent_goals",
                ""
            ),

            "opponent_logo": data.get(
                "opponent_logo",
                ""
            )

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
        format_date(
            match["date"]
        )
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

    status = match["status"]

    sard_goals = html.escape(
        str(match["sard_goals"])
    )

    opponent_goals = html.escape(
        str(match["opponent_goals"])
    )

    opponent_logo = match["opponent_logo"]

    if opponent_logo.startswith("/"):
        opponent_logo = opponent_logo[1:]

    opponent_logo = html.escape(
        opponent_logo,
        quote=True
    )


    # =====================================================
    # STATO
    # =====================================================

    if status == "Vittoria":

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

    elif status == "Sconfitta":

        score = (
            f"{sard_goals} - "
            f"{opponent_goals}"
        )

        status_class = "loss"
        status_text = "SCONFITTA"

    else:

        score = "—"

        status_class = "upcoming"
        status_text = "DA GIOCARE"


    # =====================================================
    # CASA / TRASFERTA
    # =====================================================

    if match["home_away"] == "Trasferta":

        left_logo = opponent_logo
        left_name = opponent

        right_logo = SARD_FUTSAL_LOGO
        right_name = "SARD FUTSAL"

    else:

        left_logo = SARD_FUTSAL_LOGO
        left_name = "SARD FUTSAL"

        right_logo = opponent_logo
        right_name = opponent


    # =====================================================
    # LOGO SINISTRO
    # =====================================================

    left_logo_html = ""

    if left_logo:

        left_logo_html = f"""
            <img
                src="{html.escape(left_logo, quote=True)}"
                alt="{html.escape(left_name, quote=True)}"
                class="match-team-logo"
                loading="lazy"
            >
        """


    # =====================================================
    # LOGO DESTRO
    # =====================================================

    right_logo_html = ""

    if right_logo:

        right_logo_html = f"""
            <img
                src="{html.escape(right_logo, quote=True)}"
                alt="{html.escape(right_name, quote=True)}"
                class="match-team-logo"
                loading="lazy"
            >
        """


    # =====================================================
    # RIGA PARTITA
    # =====================================================

    rows.append(f"""
    <article class="match-card {status_class}">

        <div class="match-date-column">

            <span class="match-date-day">
                {date.split(" ")[0]}
            </span>

            <span class="match-date-month">
                {date.split(" ")[1]}
            </span>

            <span class="match-date-year">
                {date.split(" ")[2]}
            </span>

        </div>


        <div class="match-main">

            <div class="match-competition">
                {competition}
            </div>


            <div class="match-teams">

                <div class="match-team">

                    {left_logo_html}

                    <h3>
                        {html.escape(left_name)}
                    </h3>

                </div>


                <div class="match-vs">

                    <span></span>

                    <strong>VS</strong>

                    <span></span>

                </div>


                <div class="match-team">

                    {right_logo_html}

                    <h3>
                        {html.escape(right_name)}
                    </h3>

                </div>

            </div>


            <div class="match-result">

                <span class="match-status">
                    {status_text}
                </span>

                <strong class="match-score">
                    {score}
                </strong>

            </div>

        </div>


        <div class="match-time-column">

            <span class="match-time">
                {time if time else "—"}
            </span>

        </div>

    </article>
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

    generated_matches = "\n".join(
        rows
    )


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
