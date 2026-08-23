from pathlib import Path
import re
import html


ROOT = Path(".")
PLAYERS_DIR = ROOT / "content" / "players"
INDEX_FILE = ROOT / "index.html"


# =========================================================
# LETTURA FRONTMATTER
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

                if ":" in line:

                    key, value = line.split(":", 1)

                    data[key.strip()] = (
                        value.strip()
                        .strip('"')
                        .strip("'")
                    )

    return data, body


# =========================================================
# LETTURA GIOCATORI DAL CMS
# =========================================================

players = []


if PLAYERS_DIR.exists():

    for file in PLAYERS_DIR.glob("*.md"):

        text = file.read_text(
            encoding="utf-8"
        )

        data, body = parse_frontmatter(text)

        name = data.get(
            "name",
            file.stem
        )

        number = data.get(
            "number",
            ""
        )

        role = data.get(
            "role",
            ""
        )

        category = data.get(
            "category",
            "Giocatore di movimento"
        )

        image = data.get(
            "image",
            ""
        )

        players.append({

            "name": name,

            "number": number,

            "role": role,

            "category": category,

            "image": image

        })


# =========================================================
# ORDINA
# =========================================================

players.sort(
    key=lambda player: (
        0 if player["category"] == "Portiere" else 1,
        int(player["number"])
        if str(player["number"]).isdigit()
        else 999,
        player["name"].lower()
    )
)


# =========================================================
# GENERA CARD
# =========================================================

goalkeepers = []
movement_players = []


for player in players:

    name = html.escape(
        player["name"]
    )

    role = html.escape(
        player["role"]
    )

    number = html.escape(
        str(player["number"])
    )

    image = player["image"]

    if image.startswith("/"):
        image = image[1:]

    image = html.escape(
        image,
        quote=True
    )


    card = f"""
    <article class="player-card real-player">

      <img
        src="{image}"
        alt="{name}"
        loading="lazy"
      >

      <div class="player-number">
        {number}
      </div>

      <div>

        <h3>
          {name}
        </h3>

        <p>
          {role}
        </p>

      </div>

    </article>
"""


    if player["category"] == "Portiere":

        goalkeepers.append(card)

    else:

        movement_players.append(card)


goalkeepers_html = "\n".join(
    goalkeepers
)

movement_html = "\n".join(
    movement_players
)


# =========================================================
# ROSA COMPLETA
# =========================================================

generated_roster = f"""
<section id="squadra" class="section dark-section">

  <div class="container">

    <div class="section-heading">

      <div>

        <p class="eyebrow orange">
          LA ROSA 2026/27
        </p>

        <h2>
          La nostra <span>squadra</span>
        </h2>

      </div>

    </div>


    <div class="roster-group">

      <div class="roster-title">

        <h3>
          Portieri
        </h3>

      </div>

      <div class="player-grid player-grid-real">

{goalkeepers_html}

      </div>

    </div>


    <div class="roster-group movement-group">

      <div class="roster-title">

        <h3>
          Giocatori di movimento
        </h3>

      </div>

      <div class="player-grid player-grid-real">

{movement_html}

      </div>

    </div>

  </div>

</section>
"""


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
    "<!-- PLAYERS_AUTO_START -->"
)

end_marker = (
    "<!-- PLAYERS_AUTO_END -->"
)


if (
    start_marker not in html_content
    or
    end_marker not in html_content
):

    raise SystemExit(
        "ERRORE: marcatori "
        "PLAYERS_AUTO_START / PLAYERS_AUTO_END "
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
    + generated_roster
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
    f"Giocatori letti dal CMS: {len(players)}"
)

print(
    "Rosa aggiornata correttamente."
)
