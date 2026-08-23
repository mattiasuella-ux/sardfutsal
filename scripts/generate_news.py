from pathlib import Path
import re
import html
from datetime import datetime


ROOT = Path(".")
NEWS_DIR = ROOT / "content" / "news"
NEWS_FILE = ROOT / "news.html"
NEWS_PAGES_DIR = ROOT / "news"


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

                if ":" in line:

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

    months = {
        "01": "GENNAIO",
        "02": "FEBBRAIO",
        "03": "MARZO",
        "04": "APRILE",
        "05": "MAGGIO",
        "06": "GIUGNO",
        "07": "LUGLIO",
        "08": "AGOSTO",
        "09": "SETTEMBRE",
        "10": "OTTOBRE",
        "11": "NOVEMBRE",
        "12": "DICEMBRE",
    }

    try:

        date = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        )

        month = date.strftime("%m")
        year = date.strftime("%Y")

        return f"{months[month]} {year}"

    except Exception:

        return date_string


# =========================================================
# SLUG
# =========================================================

def slugify(text):

    text = text.lower()

    replacements = {
        "à": "a",
        "è": "e",
        "é": "e",
        "ì": "i",
        "ò": "o",
        "ù": "u",
    }

    for old, new in replacements.items():

        text = text.replace(old, new)

    text = re.sub(
        r"[^a-z0-9]+",
        "-",
        text
    )

    return text.strip("-")


# =========================================================
# PARAGRAFI
# =========================================================

def extract_paragraphs(body):

    paragraphs = []

    for paragraph in re.split(
        r"\n\s*\n",
        body.strip()
    ):

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        paragraph = re.sub(
            r"^#+\s*",
            "",
            paragraph
        )

        paragraph = paragraph.replace(
            "\n",
            " "
        )

        paragraphs.append(
            html.escape(paragraph)
        )

    return paragraphs


# =========================================================
# IMMAGINE
# =========================================================

def normalize_image_path(image):

    image = image.strip()

    if not image:
        return ""

    if image.startswith("http://"):
        return image

    if image.startswith("https://"):
        return image

    if image.startswith("/"):
        return image

    if image.startswith("./"):
        image = image[2:]

    return "/" + image


# =========================================================
# RACCOLTA NEWS DAL CMS
# =========================================================

news_items = []


if not NEWS_DIR.exists():

    print("Nessuna cartella content/news trovata.")

else:

    for file in NEWS_DIR.glob("*.md"):

        text = file.read_text(
            encoding="utf-8"
        )

        data, body = parse_frontmatter(text)

        title = data.get(
            "title",
            file.stem
        )

        category = data.get(
            "category",
            "NEWS"
        )

        date = data.get(
            "date",
            ""
        )

        image = data.get(
            "image",
            ""
        )

        excerpt = data.get(
            "excerpt",
            ""
        )

        paragraphs = extract_paragraphs(
            body
        )

        news_items.append({

            "title": title,

            "category": category,

            "date": date,

            "image": image,

            "excerpt": excerpt,

            "paragraphs": paragraphs,

            "slug": slugify(title)

        })


# =========================================================
# ORDINA NEWS
# =========================================================

news_items.sort(
    key=lambda x: x["date"],
    reverse=True
)


# =========================================================
# GENERAZIONE NEWS.HTML
# =========================================================

cards = []


for news in news_items:

    paragraphs_html = "\n".join(

        f"              <p>{paragraph}</p>"

        for paragraph in news["paragraphs"]

    )

    if not paragraphs_html:

        paragraphs_html = (
            f"              <p>"
            f"{html.escape(news['excerpt'])}"
            f"</p>"
        )


    image_html = ""

    if news["image"]:

        image_url = normalize_image_path(
            news["image"]
        )

        image_html = f"""
            <div class="news-story-image">
              <img
                src="{html.escape(image_url, quote=True)}"
                alt="{html.escape(news['title'], quote=True)}"
                loading="lazy"
              >
            </div>
"""


    cards.append(

        f"""          <article
            class="news-story"
            id="{news['slug']}"
          >

{image_html}

            <div class="news-story-meta">
              {html.escape(news['category'])}
              ·
              {format_date(news['date'])}
            </div>

            <div>

              <h2>
                {html.escape(news['title'])}
              </h2>

              <p class="news-excerpt">
                {html.escape(news['excerpt'])}
              </p>

{paragraphs_html}

            </div>

          </article>"""

    )


generated_news = "\n\n".join(
    cards
)


# =========================================================
# AGGIORNA NEWS.HTML
# =========================================================

if not NEWS_FILE.exists():

    raise SystemExit(
        "ERRORE: news.html non trovato."
    )


html_content = NEWS_FILE.read_text(
    encoding="utf-8"
)


start_marker = (
    "<!-- NEWS_AUTO_START -->"
)

end_marker = (
    "<!-- NEWS_AUTO_END -->"
)


if (
    start_marker not in html_content
    or
    end_marker not in html_content
):

    raise SystemExit(
        "ERRORE: marcatori "
        "NEWS_AUTO_START / NEWS_AUTO_END "
        "non trovati in news.html"
    )


pattern = (
    re.escape(start_marker)
    + r".*?"
    + re.escape(end_marker)
)


replacement = (

    start_marker

    + "\n"

    + generated_news

    + "\n          "

    + end_marker

)


new_html = re.sub(

    pattern,

    replacement,

    html_content,

    flags=re.DOTALL

)


NEWS_FILE.write_text(

    new_html,

    encoding="utf-8"

)


# =========================================================
# CREA CARTELLA PAGINE SINGOLE
# =========================================================

NEWS_PAGES_DIR.mkdir(
    exist_ok=True
)


# =========================================================
# GENERA PAGINE SINGOLE
# =========================================================

expected_pages = set()


for news in news_items:

    slug = news["slug"]

    page_file = (
        NEWS_PAGES_DIR
        / f"{slug}.html"
    )

    expected_pages.add(
        page_file.name
    )


    paragraphs_html = "\n".join(

        f"""
        <p>{paragraph}</p>
        """

        for paragraph in news["paragraphs"]

    )


    if not paragraphs_html:

        paragraphs_html = f"""
        <p>{html.escape(news['excerpt'])}</p>
        """


    image_html = ""

    if news["image"]:

        image_url = normalize_image_path(
            news["image"]
        )

        image_html = f"""
        <div class="article-image">
          <img
            src="{html.escape(image_url, quote=True)}"
            alt="{html.escape(news['title'], quote=True)}"
            loading="lazy"
          >
        </div>
        """


    page_html = f"""<!DOCTYPE html>
<html lang="it">

<head>

  <meta charset="UTF-8">

  <meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
  >

  <meta
    name="description"
    content="{html.escape(news['excerpt'], quote=True)}"
  >

  <title>
    {html.escape(news['title'])} | Sard Futsal
  </title>

  <link
    rel="icon"
    type="image/png"
    href="../favicon.png"
  >

  <link
    rel="canonical"
    href="https://www.sardfutsal.it/news/{slug}.html"
  >

  <link
    rel="stylesheet"
    href="../style.css"
  >

  <link
    rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"
  >

  <script
    src="../script.js"
    defer
  ></script>

</head>


<body>


<header class="site-header">

  <div class="container nav">

    <a
      class="brand"
      href="../index.html#home"
    >

      <img
        class="brand-logo"
        src="../sard-futsal-logo.png"
        alt="Logo Sard Futsal"
      >

      <span>SARD FUTSAL</span>

    </a>


    <button
      class="menu-toggle"
      aria-label="Apri menu"
      aria-expanded="false"
    >
      ☰
    </button>


    <nav id="main-nav">

      <a href="../index.html#home">
        Home
      </a>

      <a href="../index.html#societa">
        Società
      </a>

      <a href="../index.html#squadra">
        Squadra
      </a>

      <a href="../index.html#risultati">
        Risultati
      </a>

      <a
        class="active"
        href="../news.html"
      >
        News
      </a>

      <a href="../index.html#sponsor">
        Sponsor
      </a>

      <a
        class="nav-cta"
        href="../index.html#contatti"
      >
        Contatti
      </a>

    </nav>

  </div>

</header>


<main>

  <article class="news-article">

    <div class="container">


      <header class="news-article-header">

        <div class="news-story-meta">

          {html.escape(news['category'])}
          ·
          {format_date(news['date'])}

        </div>


        <h1>
          {html.escape(news['title'])}
        </h1>


        <p class="news-excerpt">

          {html.escape(news['excerpt'])}

        </p>

      </header>


      {image_html}


      <div class="news-article-content">

        {paragraphs_html}

      </div>


      <div class="news-back">

        <a
          class="btn btn-primary"
          href="../news.html"
        >
          ← Torna alle news
        </a>

      </div>


    </div>

  </article>

</main>


<footer class="site-footer">

  <div class="container">

    <div
      class="footer-bottom"
      style="margin-top: 0;"
    >

      <p>
        © 2025 Sard Futsal · Tutti i diritti riservati
      </p>

      <p>

        <a href="../privacy.html">
          Privacy Policy
        </a>

        ·

        <a href="../cookie.html">
          Cookie Policy
        </a>

        ·

        <a
          href="javascript:void(0)"
          onclick="window.sardFutsalOpenCookieSettings && window.sardFutsalOpenCookieSettings();"
        >
          Gestisci cookie
        </a>

      </p>

    </div>

  </div>

</footer>


</body>

</html>
"""


    page_file.write_text(
        page_html,
        encoding="utf-8"
    )


# =========================================================
# CANCELLA LE VECCHIE PAGINE
# =========================================================

deleted_pages = []


if NEWS_PAGES_DIR.exists():

    for old_page in NEWS_PAGES_DIR.glob("*.html"):

        if old_page.name not in expected_pages:

            old_page.unlink()

            deleted_pages.append(
                old_page.name
            )


# =========================================================
# RISULTATO
# =========================================================

print(
    f"News generate: {len(news_items)}"
)

print(
    f"Pagine generate: {len(expected_pages)}"
)


if deleted_pages:

    print(
        "Pagine eliminate:"
    )

    for page in deleted_pages:

        print(
            f" - {page}"
        )

else:

    print(
        "Nessuna pagina da eliminare."
    )
