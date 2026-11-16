from pathlib import Path
import html

try:
    import yaml
except ImportError:
    raise SystemExit("ERRORE: PyYAML non installato (pip install pyyaml).")


ROOT = Path(".")
STANDINGS_FILE = ROOT / "content" / "classifica.yml"
INDEX_FILE = ROOT / "index.html"

SARD_NAME = "sard futsal"
SARD_LOGO = "/images/logosardfutsal.png"

START_MARKER = "<!-- STANDINGS_AUTO_START -->"
END_MARKER = "<!-- STANDINGS_AUTO_END -->"


# =========================================================
# UTILITA'
# =========================================================

def to_int(value):

    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return 0


def image_path(path):

    path = str(path or "").strip()

    if not path:
        return ""

    return html.escape(path.lstrip("/"), quote=True)


def signed(number):

    return f"+{number}" if number > 0 else str(number)


# =========================================================
# LETTURA E CALCOLO
# =========================================================

if not STANDINGS_FILE.exists():
    raise SystemExit("ERRORE: content/classifica.yml non trovato.")

loaded = yaml.safe_load(
    STANDINGS_FILE.read_text(encoding="utf-8")
) or {}

update_note = str(loaded.get("aggiornamento") or "").strip()

teams = []

for item in (loaded.get("squadre") or []):

    if not isinstance(item, dict):
        continue

    name = str(item.get("team") or "").strip()

    if not name:
        continue

    won = to_int(item.get("won"))
    drawn = to_int(item.get("drawn"))
    lost = to_int(item.get("lost"))
    goals_for = to_int(item.get("goals_for"))
    goals_against = to_int(item.get("goals_against"))
    penalty = to_int(item.get("penalty"))

    is_sard = name.casefold() == SARD_NAME

    logo = str(item.get("logo") or "").strip()

    if not logo and is_sard:
        logo = SARD_LOGO

    teams.append({
        "name": name,
        "logo": logo,
        "is_sard": is_sard,
        "played": won + drawn + lost,
        "won": won,
        "drawn": drawn,
        "lost": lost,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "diff": goals_for - goals_against,
        "points": 3 * won + drawn - penalty,
        "penalty": penalty
    })


# Punti, poi differenza reti, poi gol fatti, poi nome.
teams.sort(
    key=lambda t: (
        -t["points"],
        -t["diff"],
        -t["goals_for"],
        t["name"].casefold()
    )
)


# =========================================================
# HTML
# =========================================================

def team_row(position, team):

    if team["logo"]:

        css_class = (
            "standings-logo is-sard"
            if team["is_sard"]
            else "standings-logo"
        )

        logo = (
            f'<img src="{image_path(team["logo"])}" alt="" '
            f'class="{css_class}" loading="lazy">'
        )

    else:

        logo = '<span class="standings-logo"></span>'

    row_class = "is-sard" if team["is_sard"] else ""

    penalty = (
        f' <small title="Penalizzazione">(-{team["penalty"]})</small>'
        if team["penalty"] else ""
    )

    return f"""
            <tr class="{row_class}">
              <td class="pos">{position}</td>
              <td class="team"><div class="standings-team">{logo}<span>{html.escape(team['name'])}</span></div></td>
              <td>{team['played']}</td>
              <td class="opt">{team['won']}</td>
              <td class="opt">{team['drawn']}</td>
              <td class="opt">{team['lost']}</td>
              <td class="opt">{team['goals_for']}</td>
              <td class="opt">{team['goals_against']}</td>
              <td>{signed(team['diff'])}</td>
              <td class="pts"><strong>{team['points']}</strong>{penalty}</td>
            </tr>"""


if teams:

    rows = "".join(
        team_row(position, team)
        for position, team in enumerate(teams, start=1)
    )

    note = (
        f'<p class="standings-note">{html.escape(update_note)}</p>'
        if update_note else ""
    )

    generated = f"""{note}
        <div class="standings-scroll">
          <table class="standings">
            <thead>
              <tr>
                <th class="pos">#</th>
                <th class="team">Squadra</th>
                <th title="Partite giocate">PG</th>
                <th class="opt" title="Vittorie">V</th>
                <th class="opt" title="Pareggi">N</th>
                <th class="opt" title="Sconfitte">S</th>
                <th class="opt" title="Gol fatti">GF</th>
                <th class="opt" title="Gol subiti">GS</th>
                <th title="Differenza reti">DR</th>
                <th class="pts" title="Punti">PT</th>
              </tr>
            </thead>
            <tbody>{rows}
            </tbody>
          </table>
        </div>"""

else:

    generated = (
        '<p class="standings-note">'
        "La classifica sarà pubblicata a breve."
        "</p>"
    )


# =========================================================
# INDEX.HTML
# =========================================================

if not INDEX_FILE.exists():
    raise SystemExit("ERRORE: index.html non trovato.")

content = INDEX_FILE.read_text(encoding="utf-8")

if START_MARKER not in content or END_MARKER not in content:

    raise SystemExit(
        "ERRORE: marcatori STANDINGS_AUTO_START / "
        "STANDINGS_AUTO_END non trovati in index.html"
    )

start = content.index(START_MARKER)
end = content.index(END_MARKER) + len(END_MARKER)

new_content = (
    content[:start]
    + START_MARKER
    + "\n"
    + generated
    + "\n        "
    + END_MARKER
    + content[end:]
)

INDEX_FILE.write_text(new_content, encoding="utf-8")


print()
print("=" * 50)
print("SARD FUTSAL - GENERAZIONE CLASSIFICA")
print("=" * 50)
print(f"Squadre in classifica: {len(teams)}")
print("Classifica aggiornata correttamente.")
print("=" * 50)
