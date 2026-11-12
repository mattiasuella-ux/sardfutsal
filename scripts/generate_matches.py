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
    last_key = None

    # Riconosce una riga "chiave: valore" solo se la parte prima dei ":"
    # è una chiave semplice (senza spazi): evita di confondere con i due
    # punti che possono comparire dentro un testo libero.
    key_line = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*:")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if not key_line.match(stripped):
            # Riga di continuazione di un valore "piegato" su più righe
            # (es. salvato dal CMS su due righe): la riattacchiamo al
            # valore precedente.
            if last_key is not None:
                data[last_key] = (data[last_key] + " " + stripped).strip()
            i += 1
            continue

        key, value = stripped.split(":", 1)
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

            data[key] = "\n".join(
                item for item in multiline if item
            )
            last_key = key

            continue

        data[key] = value.strip('"').strip("'")
        last_key = key
        i += 1

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

            "scorers_home": data.get(
                "scorers_home",
                ""
            ),

            "scorers_away": data.get(
                "scorers_away",
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
# CALENDARIO STAGIONE (content/calendario.yml, da Pages CMS)
# =========================================================

CALENDAR_FILE = ROOT / "content" / "calendario.yml"

SARD_LOGO = "/images/logosardfutsal.png"

CALENDAR_FIELDS = (
    "date", "time", "competition", "opponent", "venue", "home_away",
    "status", "sard_goals", "opponent_goals", "scorers_home",
    "scorers_away", "home_logo", "away_logo"
)


def yaml_text(key, value):

    if value is None:
        return ""

    # YAML 1.1 legge 21:30 come numero sessagesimale (1290 minuti)
    if (
        key == "time"
        and isinstance(value, int)
        and not isinstance(value, bool)
    ):
        return f"{value // 60:02d}:{value % 60:02d}"

    # le date arrivano come oggetti data
    if hasattr(value, "isoformat"):
        return value.isoformat()[:10]

    return str(value).strip()


def match_key(match):

    return (
        str(match["date"]).strip(),
        str(match["opponent"]).strip().casefold()
    )


calendar_entries = []

if CALENDAR_FILE.exists():

    try:
        import yaml
    except ImportError:
        yaml = None
        print(
            "ATTENZIONE: PyYAML non installato: "
            "content/calendario.yml ignorato."
        )

    if yaml:

        try:

            loaded = yaml.safe_load(
                CALENDAR_FILE.read_text(encoding="utf-8")
            ) or {}

        except yaml.YAMLError as error:

            loaded = {}
            print(f"ATTENZIONE: content/calendario.yml non valido: {error}")

        for item in (loaded.get("partite") or []):

            if not isinstance(item, dict):
                continue

            row = {
                key: yaml_text(key, item.get(key))
                for key in CALENDAR_FIELDS
            }

            if not row["date"] or not row["opponent"]:
                continue

            row["home_away"] = row["home_away"] or "Casa"
            row["status"] = row["status"] or "Da giocare"

            # il logo di Sard Futsal e' sempre lo stesso: non serve inserirlo
            if row["home_away"] == "Casa":
                row["home_logo"] = row["home_logo"] or SARD_LOGO
            else:
                row["away_logo"] = row["away_logo"] or SARD_LOGO

            calendar_entries.append(row)


# La stessa partita (data + avversario) inserita sia nel calendario sia
# come file singolo: vale quella del calendario.
calendar_keys = {match_key(m) for m in calendar_entries}

matches = [
    m for m in matches
    if match_key(m) not in calendar_keys
] + calendar_entries


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
first_next_found = False


# =========================================================
# MARCATORI
# =========================================================

# Un marcatore per riga (o separato da ";"): se lo stesso nome compare
# piu' volte i gol vengono sommati, cosi' compare una volta sola con
# tanti palloni quanti sono i gol. Si puo' anche scrivere "Rossi x2"
# o "Rossi (2)".

GOAL_EMOJI = "⚽"

SCORER_COUNT = re.compile(
    r"^(?P<name>.*?)\s*(?:[x×]\s*(?P<n1>\d+)|\((?P<n2>\d+)\))$",
    re.IGNORECASE
)


def group_scorers(raw):

    totals = {}

    for item in re.split(r"\r?\n|;", raw):

        item = item.strip()

        if not item:
            continue

        goals = 1
        found = SCORER_COUNT.match(item)

        if found and found.group("name").strip():

            item = found.group("name").strip()
            goals = int(found.group("n1") or found.group("n2"))

        key = " ".join(item.split()).casefold()

        if key in totals:
            totals[key][1] += goals
        else:
            totals[key] = [" ".join(item.split()), goals]

    return [(name, goals) for name, goals in totals.values()]


def scorers_html(raw, css_class):

    scorers = group_scorers(raw)

    if not scorers:
        return f'<div class="{css_class}"></div>'

    rows = "".join(
        '<span class="match-scorer">'
        f'<span class="match-scorer-name">{html.escape(name)}</span>'
        f'<span class="match-scorer-goals">{GOAL_EMOJI * min(goals, 12)}</span>'
        '</span>'
        for name, goals in scorers
    )

    return f'<div class="{css_class}">{rows}</div>'


def match_status(match):

    return (
        str(match.get("status", "Da giocare")).strip()
        or "Da giocare"
    )


# Le card in evidenza sono solo due: l'ultimo risultato e il prossimo
# impegno. Tutte le altre partite compaiono nel "Calendario completo".
featured = set()

finished_matches = [
    m for m in matches
    if match_status(m) == "Terminata"
]

upcoming_matches = [
    m for m in matches
    if match_status(m) not in (
        "Terminata",
        "Calendario in aggiornamento"
    )
]

if finished_matches:
    featured.add(id(finished_matches[-1]))

if upcoming_matches:
    featured.add(id(upcoming_matches[0]))


for match in matches:

    if (
        match_status(match) != "Calendario in aggiornamento"
        and id(match) not in featured
    ):
        continue

    # =====================================================
    # DATA
    # =====================================================

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


    # =====================================================
    # DATI TESTUALI
    # =====================================================

    time = html.escape(
        str(match["time"])
    )

    competition = html.escape(
        str(match["competition"])
    )

    opponent = html.escape(
        str(match["opponent"])
    )


    # =====================================================
    # STATO PARTITA
    # =====================================================

    status = str(
        match.get(
            "status",
            "Da giocare"
        )
    ).strip()

    extra_card_class = ""


    # =====================================================
    # CALENDARIO IN AGGIORNAMENTO
    # =====================================================

    if status == "Calendario in aggiornamento":

        match_label = (
            "CALENDARIO IN AGGIORNAMENTO"
        )

        card = f"""
        <div class="match-card-wrapper">

            <div class="match-card-label">
                {match_label}
            </div>

            <article class="match-card match-card-update">

                <div class="match-card-image-container">

                    <img
                        src="images/calendario-aggiornamento.png"
                        alt="Calendario in aggiornamento"
                        class="calendar-update-image"
                    >

                </div>

            </article>

        </div>
        """

        cards.append(card)

        continue


    # =====================================================
    # PARTITA TERMINATA
    # =====================================================

    elif status == "Terminata":

        try:

            sard_goals_value = int(
                str(
                    match.get(
                        "sard_goals",
                        0
                    )
                ).strip()
            )

        except (
            ValueError,
            TypeError
        ):

            sard_goals_value = 0


        try:

            opponent_goals_value = int(
                str(
                    match.get(
                        "opponent_goals",
                        0
                    )
                ).strip()
            )

        except (
            ValueError,
            TypeError
        ):

            opponent_goals_value = 0


        match_label = (
            "RISULTATO FINALE"
        )

        score = (
            f"{sard_goals_value} - "
            f"{opponent_goals_value}"
        )


    # =====================================================
    # PARTITA DA GIOCARE
    # =====================================================

    else:

        if not first_next_found:

            match_label = (
                "PROSSIMO IMPEGNO • NEXT MATCH"
            )

            extra_card_class = (
                "is-next-match"
            )

            first_next_found = True

        else:

            match_label = (
                "PROSSIMA PARTITA"
            )

        score = "VS"


    # =====================================================
    # CASA / TRASFERTA
    # =====================================================

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


    # =====================================================
    # LOGHI
    # =====================================================

    home_logo = clean_image_path(
        match["home_logo"]
    )

    away_logo = clean_image_path(
        match["away_logo"]
    )


    if home_logo:

        home_logo_html = (
            f'<img '
            f'src="{home_logo}" '
            f'alt="{home_name}" '
            f'class="match-team-logo" '
            f'loading="lazy">'
        )

    else:

        home_logo_html = (
            '<div '
            'class="match-team-logo-placeholder">'
            '</div>'
        )


    if away_logo:

        away_logo_html = (
            f'<img '
            f'src="{away_logo}" '
            f'alt="{away_name}" '
            f'class="match-team-logo" '
            f'loading="lazy">'
        )

    else:

        away_logo_html = (
            '<div '
            'class="match-team-logo-placeholder">'
            '</div>'
        )


    # =====================================================
    # MARCATORI CASA / TRASFERTA
    # =====================================================

    home_scorers_html = scorers_html(
        match.get("scorers_home", ""),
        "match-scorers-home"
    )

    away_scorers_html = scorers_html(
        match.get("scorers_away", ""),
        "match-scorers-away"
    )


    # =====================================================
    # GENERAZIONE CARD
    # =====================================================

    card = f"""
    <div class="match-card-wrapper {extra_card_class}">

        <div class="match-card-label">
            {match_label}
        </div>

        <article class="match-card">

            <div class="match-main">

                <div class="match-competition">
                    {competition}
                </div>


                <div class="match-date-column">

                    <div class="match-date">

                        <span class="match-date-day">
                            {day}
                        </span>

                        <span class="match-date-month">
                            {month}
                        </span>

                        <span class="match-date-year">
                            {year}
                        </span>

                    </div>

                    <span class="match-date-time">
                        {time if time else "—"}
                    </span>

                </div>


                <div class="match-teams">


                    <div class="match-team">

                        {home_logo_html}

                        <h3>
                            {home_name}
                        </h3>

                    </div>


                    <div class="match-vs">

                        <span></span>

                        <div class="match-vs-center">

                            <span class="match-time">
                                {score}
                            </span>

                        </div>

                        <span></span>

                    </div>


                    <div class="match-team">

                        {away_logo_html}

                        <h3>
                            {away_name}
                        </h3>

                    </div>


                </div>


                <div class="match-scorers-row">

                    {home_scorers_html}

                    <div class="match-scorers-spacer">
                    </div>

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

        <div class="season-status-icon">
        </div>

        <div class="season-status-content">

            <p class="status-label">
                CALENDARIO IN AGGIORNAMENTO
            </p>

            <h3>
                Pronti per una nuova stagione.
            </h3>

            <p>
                Il calendario ufficiale della stagione
                2026/27 sarà pubblicato non appena saranno
                definiti girone, avversarie e date delle gare.
            </p>

        </div>

    </div>
    """

else:

    generated_matches = "\n".join(
        cards
    )


# =========================================================
# CONTROLLO INDEX.HTML
# =========================================================

if not INDEX_FILE.exists():

    raise SystemExit(
        "ERRORE: index.html non trovato."
    )


html_content = INDEX_FILE.read_text(
    encoding="utf-8"
)


# =========================================================
# MARCATORI
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
        "MATCHES_AUTO_START / "
        "MATCHES_AUTO_END "
        "non trovati in index.html"
    )


# =========================================================
# SOSTITUZIONE
# =========================================================

pattern = (
    re.escape(start_marker)
    +
    r".*?"
    +
    re.escape(end_marker)
)


replacement = (
    start_marker
    +
    "\n"
    +
    generated_matches
    +
    "\n"
    +
    end_marker
)


new_html = re.sub(
    pattern,
    replacement,
    html_content,
    flags=re.DOTALL
)


# =========================================================
# CALENDARIO COMPLETO
# =========================================================

def goals_value(value):

    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None


def calendar_row(match):

    date = format_date(match["date"])

    sard_goals = goals_value(match.get("sard_goals"))
    opponent_goals = goals_value(match.get("opponent_goals"))

    finished = (
        match_status(match) == "Terminata"
        and sard_goals is not None
        and opponent_goals is not None
    )

    is_home = match["home_away"] == "Casa"

    opponent = html.escape(str(match["opponent"]))

    if is_home:
        teams = f'<b>SARD FUTSAL</b> <em>vs</em> {opponent}'
        home_goals, away_goals = sard_goals, opponent_goals
    else:
        teams = f'{opponent} <em>vs</em> <b>SARD FUTSAL</b>'
        home_goals, away_goals = opponent_goals, sard_goals

    row_class = "calendar-row"

    if finished:

        if sard_goals > opponent_goals:
            row_class += " is-win"
        elif sard_goals < opponent_goals:
            row_class += " is-loss"
        else:
            row_class += " is-draw"

        result = f"{home_goals} - {away_goals}"

    else:

        row_class += " is-upcoming"
        result = "—"

    meta = [
        html.escape(str(match["competition"])),
        html.escape(str(match["time"])),
        html.escape(str(match["venue"]).strip())
    ]

    meta = " · ".join(item for item in meta if item)

    tag = "CASA" if is_home else "TRASFERTA"

    return f"""
        <div class="{row_class}">
            <div class="calendar-date">
                <strong>{html.escape(date['day'])}</strong>
                <span>{html.escape(date['month'])}</span>
            </div>
            <div class="calendar-info">
                <div class="calendar-teams">{teams}</div>
                <div class="calendar-meta">{meta}</div>
            </div>
            <div class="calendar-side">
                <span class="calendar-tag">{tag}</span>
                <span class="calendar-score">{result}</span>
            </div>
        </div>"""


calendar_matches = [
    m for m in matches
    if match_status(m) != "Calendario in aggiornamento"
    and m["date"]
]

if calendar_matches:

    generated_calendar = (
        '<div class="calendar-block">'
        '<div class="calendar-title">CALENDARIO COMPLETO</div>'
        + "".join(calendar_row(m) for m in calendar_matches)
        + "\n    </div>"
    )

else:

    generated_calendar = ""


calendar_start = "<!-- CALENDAR_AUTO_START -->"
calendar_end = "<!-- CALENDAR_AUTO_END -->"

if calendar_start in new_html and calendar_end in new_html:

    new_html = re.sub(
        re.escape(calendar_start) + r".*?" + re.escape(calendar_end),
        lambda _: (
            calendar_start + "\n" + generated_calendar
            + "\n" + calendar_end
        ),
        new_html,
        flags=re.DOTALL
    )

else:

    print(
        "ATTENZIONE: marcatori CALENDAR_AUTO_START / "
        "CALENDAR_AUTO_END non trovati: calendario completo saltato."
    )


# =========================================================
# SALVATAGGIO
# =========================================================

INDEX_FILE.write_text(
    new_html,
    encoding="utf-8"
)


# =========================================================
# OUTPUT
# =========================================================

print()
print("=" * 50)
print(
    "SARD FUTSAL - GENERAZIONE CALENDARIO"
)
print("=" * 50)
print(
    f"Partite trovate: {len(matches)}"
)
print(
    f"Card generate: {len(cards)}"
)
print(
    "Calendario aggiornato correttamente."
)
print("=" * 50)
