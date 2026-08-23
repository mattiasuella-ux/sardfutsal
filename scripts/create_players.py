from pathlib import Path

PLAYERS_DIR = Path("content/players")

PLAYERS = [
    {
        "name": "Marco Arceri",
        "number": "",
        "role": "Portiere",
        "category": "Portiere",
        "image": "images/marco-arceri.jpeg",
    },
    {
        "name": "Samuel Tuveri",
        "number": "",
        "role": "Portiere",
        "category": "Portiere",
        "image": "images/samuel-tuveri.jpeg",
    },
    {
        "name": "Sebastiano Moi",
        "number": "",
        "role": "Portiere",
        "category": "Portiere",
        "image": "images/sebastiano-moi.jpeg",
    },
    {
        "name": "Nicola Carboni",
        "number": "",
        "role": "Centrale",
        "category": "Giocatore di movimento",
        "image": "images/nicola-carboni.jpeg",
    },
    {
        "name": "Christian Cabriolu",
        "number": "",
        "role": "Centrale",
        "category": "Giocatore di movimento",
        "image": "images/christian-cabriolu.jpeg",
    },
    {
        "name": "Davide Farris",
        "number": "",
        "role": "Pivot",
        "category": "Giocatore di movimento",
        "image": "images/davide-farris.jpeg",
    },
    {
        "name": "Antonio Barracca",
        "number": "",
        "role": "Pivot",
        "category": "Giocatore di movimento",
        "image": "images/antonio-barracca.jpeg",
    },
    {
        "name": "Luca Montis",
        "number": "",
        "role": "Pivot",
        "category": "Giocatore di movimento",
        "image": "images/luca-montis.jpeg",
    },
    {
        "name": "Emanuele Lisci",
        "number": "",
        "role": "Laterale",
        "category": "Giocatore di movimento",
        "image": "images/emanuele-lisci.jpeg",
    },
    {
        "name": "Carlo Serra",
        "number": "",
        "role": "Laterale",
        "category": "Giocatore di movimento",
        "image": "images/carlo-serra.jpeg",
    },
    {
        "name": "Gianluca Escana",
        "number": "",
        "role": "Laterale",
        "category": "Giocatore di movimento",
        "image": "images/gianluca-escana.jpeg",
    },
    {
        "name": "Nicola Massa",
        "number": "",
        "role": "Laterale",
        "category": "Giocatore di movimento",
        "image": "images/nicola-massa.jpeg",
    },
    {
        "name": "Emmanuele Cuccu",
        "number": "",
        "role": "Laterale",
        "category": "Giocatore di movimento",
        "image": "images/emmanuele-cuccu.jpeg",
    },
    {
        "name": "Mattia Cuccu",
        "number": "",
        "role": "Universale",
        "category": "Giocatore di movimento",
        "image": "images/mattia-cuccu.jpeg",
    },
    {
        "name": "Alessandro Carboni",
        "number": "",
        "role": "Universale",
        "category": "Giocatore di movimento",
        "image": "images/alessandro-carboni.jpeg",
    },
    {
        "name": "Gianluca Nocerino",
        "number": "",
        "role": "Universale",
        "category": "Giocatore di movimento",
        "image": "images/gianluca-nocerino.png",
    },
]


def slugify(name):
    replacements = {
        "à": "a",
        "è": "e",
        "é": "e",
        "ì": "i",
        "ò": "o",
        "ù": "u",
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    return name.lower().replace(" ", "-")


PLAYERS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


for player in PLAYERS:

    slug = slugify(
        player["name"]
    )

    file_path = (
        PLAYERS_DIR / f"{slug}.md"
    )

    content = f"""---
name: "{player['name']}"
number: "{player['number']}"
role: "{player['role']}"
category: "{player['category']}"
image: "{player['image']}"
---
"""

    file_path.write_text(
        content,
        encoding="utf-8"
    )

    print(
        f"Creato: {file_path}"
    )


print()
print(
    f"Totale giocatori creati: {len(PLAYERS)}"
)
