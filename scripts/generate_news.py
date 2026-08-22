from pathlib import Path
import re
import html
from datetime import datetime

ROOT = Path(".")
NEWS_DIR = ROOT / "content" / "news"
NEWS_FILE = ROOT / "news.html"

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
                    data[key.strip()] = value.strip().strip('"').strip("'")

    return data, body


def format_date(date_string):
    try:
        date = datetime.strptime(date_string, "%Y-%m-%d")
        return date.strftime("%B %Y").upper()
    except:
        return date_string


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9àèéìòù]+", "-", text)
    return text.strip("-")


def extract_paragraphs(body):
    paragraphs = []

    for paragraph in re.split(r"\n\s*\n", body.strip()):
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        paragraph = re.sub(r"^#+\s*", "", paragraph)
        paragraph = paragraph.replace("\n", " ")

        paragraphs.append(html.escape(paragraph))

    return paragraphs


news_items = []

for file in NEWS_DIR.glob("*.md"):
    text = file.read_text(encoding="utf-8")
    data, body = parse_frontmatter(text)

    title = data.get("title", file.stem)
    category = data.get("category", "NEWS")
    date = data.get("date", "")
    excerpt = data.get("excerpt", "")

    paragraphs = extract_paragraphs(body)

    news_items.append({
        "title": title,
        "category": category,
        "date": date,
        "excerpt": excerpt,
        "paragraphs": paragraphs,
        "slug": slugify(title)
    })


news_items.sort(
    key=lambda x: x["date"],
    reverse=True
)


cards = []

for news in news_items:

    paragraphs_html = "\n".join(
        f"              <p>{paragraph}</p>"
        for paragraph in news["paragraphs"]
    )

    if not paragraphs_html:
        paragraphs_html = f"              <p>{html.escape(news['excerpt'])}</p>"

    cards.append(f"""          <article class="news-story" id="{news['slug']}">
            <div class="news-story-meta">
              {html.escape(news['category'])} · {format_date(news['date'])}
            </div>

            <div>
              <h2>{html.escape(news['title'])}</h2>

              <p class="news-excerpt">
                {html.escape(news['excerpt'])}
              </p>

{paragraphs_html}
            </div>
          </article>""")

generated_news = "\n\n".join(cards)


html_content = NEWS_FILE.read_text(encoding="utf-8")

start_marker = "<!-- NEWS_AUTO_START -->"
end_marker = "<!-- NEWS_AUTO_END -->"

if start_marker not in html_content or end_marker not in html_content:
    raise SystemExit(
        "ERRORE: marcatori NEWS_AUTO_START / NEWS_AUTO_END non trovati in news.html"
    )

pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)

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

NEWS_FILE.write_text(new_html, encoding="utf-8")

print(f"News generate: {len(news_items)}")
