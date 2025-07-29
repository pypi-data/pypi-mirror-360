#!/usr/bin/env python3

import re, glob, json, hashlib, datetime, sys, argparse
from pathlib import Path
from io import StringIO
import yaml, markdown
from jinja2 import Template

ENCODE = "utf-8"
EXTENSIONS = ["tables", "fenced_code"]

RSS_ITEM_TEMPLATE = """
<item>
    <title>{title}</title>
    <link>https://shizukani-cp.github.io/blog/articles/{date}</link>
    <description>{description}</description>
    <pubDate>{datetime}</pubDate>
    <guid>{hash}</guid>
</item>
"""

def get_articles(top):
    files = glob.glob(f"{top}/articles/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]")
    file_dates = [int(fname[-8:]) for fname in files]
    file_dates.sort()
    return [f"{top}/articles/{date}/index.md" for date in file_dates]

class Article:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self._split_config_content()
        self.md = markdown.Markdown(extensions=EXTENSIONS)

    def _split_config_content(self):
        self.mdstr = ""
        config_str = ""
        n = 0
        with open(self.filepath, "r", encoding=ENCODE) as f:
            for line in f.readlines():
                if re.fullmatch("^---+[\r\n]+", line):
                    n += 1
                    continue
                if n == 1:
                    config_str += line
                else:
                    self.mdstr += line

        with StringIO() as st:
            st.write(config_str)
            st.seek(0)
            self.config =  yaml.safe_load(st)

    def _to_html_with_template(self, template: Template) -> str :
        return template.render(
                               content=self.md.convert(self.mdstr),
                               config=self.config)

    def _get_html_file_name(self) -> Path :
        return Path(str(self.filepath.parent / self.filepath.stem) + ".html")

    def html_save(self, template: Template):
        print("saving", str(self.filepath))
        with open(self._get_html_file_name(), "w", encoding=ENCODE) as f:
            f.write(self._to_html_with_template(template))

    def get_rss(self):
        return RSS_ITEM_TEMPLATE.format(
            title=self.config["title"],
            date=self.config["date"],
            description=self.config["description"],
            datetime=datetime.datetime(
                int(str(self.config["date"])[:4]),
                int(str(self.config["date"])[4:6]),
                int(str(self.config["date"])[6:])
            ),
            hash=hashlib.sha256(self.config["title"].encode()).hexdigest()
        )

def load_template(templatefile):
    return Template(templatefile.read())

RSS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>静カニのブログ</title>
  <link>https://shizukani-cp.github.io/blog/</link>
  <language>ja-jp</language>
  <description>静カニのブログ</description>
  {items}
</channel>
</rss>
"""

def execute(arg):

    if arg.template is None:
        arg.template = open(Path(arg.top_dir) / "template.html", "r", encoding=ENCODE)

    template = load_template(arg.template)

    articles = [Article(Path(fname)) for fname in get_articles(arg.top_dir)]

    if len(articles) == 0:
        sys.exit("記事がありません")

    configs = []
    for article in articles:
        article.html_save(template)
        configs.append(article.config)

    with open(Path(arg.top_dir) / "scripts" / "articles.json.js", "w", encoding=ENCODE) as f:
        f.write(f"window.articles = JSON.parse('{json.dumps(configs, ensure_ascii=False)}');")

    with open(Path(arg.top_dir) / "rss.xml", "w", encoding=ENCODE) as f:
        f.write(RSS_TEMPLATE.format(items="\n".join([article.get_rss() for article in articles])))

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("top_dir", default=".")
    parser.add_argument("--template", "-t", type=argparse.FileType("r", encoding=ENCODE))

    args = parser.parse_args()

    execute(args)
