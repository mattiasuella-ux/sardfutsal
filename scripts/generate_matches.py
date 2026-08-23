rom pathlib import Path
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

    if text.startswith("---"):

        parts = text.split("---", 2)

        if len(parts) == 3:

            frontmatter = parts[1]
            body = parts[2].strip()

            for line in frontmatter.splitlines():

                if ":" not in line:
                    continue

                key, value = line.split(":", 1)

                data[key.strip()] = (
                    value.strip()
                    .strip('"')
                    .strip("'")
                )

    return data, body


# =========================================================
# DATA
# =========================================================

def format_date(date_string):

    if not date_string:
        return {
            "day": "",
            "month": "",
            "year": ""
        }

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
            12: "DIC"
        }

        return {
            "day": f"{date.day:02d}",
            "month": months[date.month],
            "year": str(date.year)
        }

    except ValueError:

        return {
            "day": date_string,
            "month": "",
            "year": ""
        }


# =========================================================
# PERCORSI IMMAGINI
# =========================================================

def clean_image_path(image):

    if not image:
        return ""

    image = str(image).strip()

    if image.startswith("/"):
        image = image[1:]

    return html.escape(
        image,
        quote=True
    )


# =========================================================
# LEGGI LE PARTITE
# =========================================================

matches = []

if MATCHES_DIR.exists():

    for file in sorted(
        MATCHES_DIR.glob("*.md")
    ):

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

            "sard_goals": data.get(
                "sard_goals",
                "-1"
            ),

            "opponent_goals": data.get(
                "opponent_goals",
                "-1"
            ),

            "scorers": data.get(
                "scorers",
                ""
            ),

            "home_logo": data.get(
                "home_logo",
                ""
            ),

            "away_logo": data.get(
                "away_logo",
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
# GENERAZIONE CARD
# =========================================================

cards = []


for match in matches:

    # -----------------------------------------------------
    # DATA
    # -----------------------------------------------------

    date = format_date(
        match["date"]
    )

    day = html.escape(
        date["day"]
    )

    month = html.escape(
        date["month"]
    )

    year = html.escape(
        date["year"]
    )


    # -----------------------------------------------------
    # DATI
    # -----------------------------------------------------

    time = html.escape(
        str(match["time"])
    )

    competition = html.escape(
        str(match["competition"])
    )

    opponent = html.escape(
        str(match["opponent"])
    )


    # -----------------------------------------------------
    # GOL
    # -1 = partita non disputata
    # 0 o superiore = risultato reale
    # -----------------------------------------------------

    try:
        sard_goals_value = int(
            str(match["sard_goals"]).strip()
        )
    except (ValueError, TypeError):
        sard_goals_value = -1

    try:
        opponent_goals_value = int(
            str(match["opponent_goals"]).strip()
        )
    except (ValueError, TypeError):
        opponent_goals_value = -1


    if (
        sard_goals_value >= 0
        and opponent_goals_value >= 0
    ):

        match_label = "RISULTATO FINALE"

        score = (
            f"{sard_goals_value} - "
            f"{opponent_goals_value}"
        )

    else:

        match_label = "PROSSIMA PARTITA"

        score = "VS"


    # -----------------------------------------------------
    # CASA / TRASFERTA
    # -----------------------------------------------------

    if match["home_away"] == "Casa":

        home_name = "SARD FUTSAL"
        away_name = opponent

    else:

        home_name = opponent
        away_name = "SARD FUTSAL"


    home_name = html.escape(
        home_name
    )

    away_name = html.escape(
        away_name
    )


    # -----------------------------------------------------
    # LOGHI
    # -----------------------------------------------------

    home_logo = clean_image_path(
        match["home_logo"]
    )

    away_logo = clean_image_path(
        match["away_logo"]
    )


    if home_logo:

        home_logo_html = f"""
            <img
                src="{home_logo}"
                alt="{home_name}"
                class="match-team-logo"
                loading="lazy"
            >
        """

    else:

        home_logo_html = """
            <div class="match-team-logo-placeholder"></div>
        """


    if away_logo:

        away_logo_html = f"""
            <img
                src="{away_logo}"
                alt="{away_name}"
                class="match-team-logo"
                loading="lazy"
            >
        """

    else:

        away_logo_html = """
            <div class="match-team-logo-placeholder"></div>
        """


    # -----------------------------------------------------
    # MARCATORI
    #
    # Il campo CMS "scorers" può contenere:
    # - righe separate da invio
    # - oppure elementi separati da ;
    #
    # Per ora i marcatori vengono divisi in due colonne:
    # casa a sinistra, ospite a destra.
    #
    # Per assegnare automaticamente ogni nome alla squadra
    # corretta, il formato consigliato nel CMS è:
    #
    # CASA: Nome
    # OSPITE: Nome
    #
    # Esempio:
    # CASA: Rossi
    # CASA: Piras
    # OSPITE: Bianchi
    # -----------------------------------------------------

    scorers_raw = str(
        match["scorers"]
    ).strip()

    home_scorers = []
    away_scorers = []

    if scorers_raw:

        for item in re.split(
            r"\r?\n|;",
            scorers_raw
        ):

            item = item.strip()

            if not item:
                continue

            if ":" in item:

                side, scorer = item.split(
                    ":",
                    1
                )

                side = side.strip().upper()
                scorer = scorer.strip()

                if side == "CASA":

                    home_scorers.append(
                        html.escape(scorer)
                    )

                elif side == "OSPITE":

                    away_scorers.append(
                        html.escape(scorer)
                    )

            else:

                # Se non viene specificata la squadra,
                # manteniamo il nome nella colonna casa.
                home_scorers.append(
                    html.escape(item)
                )


    home_scorers_html = ""

    if home_scorers:

        home_scorers_html = f"""
            <div class="match-scorers-home">
                {"".join(
                    f'<span>{item}</span>'
                    for item in home_scorers
                )}
            </div>
        """


    away_scorers_html = ""

    if away_scorers:

        away_scorers_html = f"""
            <div class="match-scorers-away">
                {"".join(
                    f'<span>{item}</span>'
                    for item in away_scorers
                )}
            </div>
        """


    # -----------------------------------------------------
    # CARD
    # -----------------------------------------------------

    card = f"""
    <div class="match-card-wrapper">

        <div class="match-card-label">
            {match_label}
        </div>

        <article class="match-card">

            <div class="match-main">

                <!-- CAMPIONATO -->

                <div class="match-competition">
                    {competition}
                </div>


                <!-- DATA + ORA -->

                <div class="match-date-column">

                    <div class="match-date">
                        <span class="match-date-day">{day}</span>
                        <span class="match-date-month">{month}</span>
                        <span class="match-date-year">{year}</span>
                    </div>

                    <span class="match-date-time">
                        {time if time else "—"}
                    </span>

                </div>


                <!-- SQUADRE -->

                <div class="match-teams">

                    <!-- SQUADRA CASA -->

                    <div class="match-team">

                        {home_logo_html}

                        <h3>
                            {home_name}
                        </h3>

                    </div>


                    <!-- CENTRO -->

                    <div class="match-vs">

                        <span></span>

                        <div class="match-vs-center">

                            <span class="match-time">
                                {score}
                            </span>

                        </div>

                        <span></span>

                    </div>


                    <!-- SQUADRA OSPITE -->

                    <div class="match-team">

                        {away_logo_html}

                        <h3>
                            {away_name}
                        </h3>

                    </div>

                </div>


                <!-- MARCATORI -->

                <div class="match-scorers-row">

                    {home_scorers_html}

                    <div class="match-scorers-spacer"></div>

                    {away_scorers_html}

                </div>

            </div>

        </article>

    </div>
    """

    cards.append(card)


# =========================================================
# SE NON CI SONO PARTITE
# =========================================================

if not cards:

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
        cards
    )


# =========================================================
# CONTROLLO INDEX
# =========================================================

if not INDEX_FILE.exists():

    raise SystemExit(
        "ERRORE: index.html non trovato."
    )


html_content = INDEX_FILE.read_text(
    encoding="utf-8"
)


# =========================================================
# MARCATORI INDEX
# =========================================================

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


# =========================================================
# SOSTITUZIONE BLOCCO
# =========================================================

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


# =========================================================
# SALVA INDEX
# =========================================================

INDEX_FILE.write_text(
    new_html,
    encoding="utf-8"
)


# =========================================================
# REPORT
# =========================================================

print()
print("=" * 50)
print("SARD FUTSAL - GENERAZIONE CALENDARIO")
print("=" * 50)
print()

print(
    f"Partite trovate: {len(matches)}"
)

print(
    f"Card generate: {len(cards)}"
)

print()

print(
    "Calendario aggiornato correttamente."
)

print(
    "Gestione -1 / VS attiva."
)

print(
    "Loghi casa/trasferta collegati al CMS."
)

print(
    "Marcatori separati casa/ospite."
)

print()
print("=" * 50)
