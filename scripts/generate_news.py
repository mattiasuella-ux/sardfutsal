from pathlib import Path
import re
import html
from datetime import datetime

ROOT = Path(".")
NEWS_DIR = ROOT / "content" / "news"
NEWS_FILE = ROOT / "news.html"
ARTICLES_DIR = ROOT / "news"


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

        return date.strftime(
            "%B %Y"
        ).upper()

    except:
        return date_string


def slugify(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9àèéìòù]+",
        "-",
        text
    )

    return text.strip("-")


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


news_items = []


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


news_items.sort(
    key=lambda x: x["date"],
    reverse=True
)


# ============================================================
# CREA LA CARTELLA DELLE PAGINE ARTICOLO
# ============================================================

ARTICLES_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# GENERA LE PAGINE DEI SINGOLI ARTICOLI
# ============================================================

for news in news_items:

    slug = news["slug"]

    article_file = (
        ARTICLES_DIR /
        f"{slug}.html"
    )

    title = html.escape(
        news["title"]
    )

    category = html.escape(
        news["category"]
    )

    date = format_date(
        news["date"]
    )

    excerpt = html.escape(
        news["excerpt"]
    )

    image_html = ""

    if news["image"]:

        image_url = html.escape(
            news["image"],
            quote=True
        )

        image_html = f"""
        <div class="article-image">
          <img
            src="../{image_url}"
            alt="{title}"
          >
        </div>
        """

    paragraphs_html = "\n".join(

        f"""
        <p>{paragraph}</p>
        """

        for paragraph in news["paragraphs"]

    )

    if not paragraphs_html:

        paragraphs_html = f"""
        <p>{excerpt}</p>
        """


    article_html = f"""<!DOCTYPE html>
<html lang="it">

<head>

  <meta charset="UTF-8">

  <meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
  >

  <meta
    name="description"
    content="{excerpt}"
  >

  <title>
    {title} | Sard Futsal
  </title>

  <link
    rel="icon"
    type="image/png"
    href="../favicon.png"
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

      <span>
        SARD FUTSAL
      </span>

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

  <section class="news-article">

    <div class="container">

      <div class="news-article-header">

        <div class="news-story-meta">
          {category} · {date}
        </div>

        <h1>
          {title}
        </h1>

        <p class="news-excerpt">
          {excerpt}
        </p>

      </div>


      {image_html}


      <article class="news-article-content">

        {paragraphs_html}

      </article>


      <div class="news-back">

        <a
          class="btn btn-primary"
          href="../news.html"
        >
          ← Torna alle news
        </a>

      </div>

    </div>

  </section>

</main>


<footer class="site-footer">

  <div class="container">

    <div class="footer-bottom">

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


    article_file.write_text(
        article_html,
        encoding="utf-8"
    )


# ============================================================
# GENERA LE NEWS NELLA PAGINA NEWS
# ============================================================

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

        image_url = html.escape(
            news["image"],
            quote=True
        )

        image_html = f"""
            <div class="news-story-image">

              <img
                src="{image_url}"
                alt="{html.escape(news['title'], quote=True)}"
                loading="lazy"
              >

            </div>
"""


    article_url = (
        f"news/{news['slug']}.html"
    )


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


              <a
                class="news-link"
                href="{article_url}"
              >
                Leggi la notizia →
              </a>

            </div>

          </article>"""

    )


generated_news = "\n\n".join(
    cards
)


# ============================================================
# AGGIORNA NEWS.HTML
# ============================================================

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


print(
    f"News generate: {len(news_items)}"
)

print(
    f"Pagine articoli generate: {len(news_items)}"
)
