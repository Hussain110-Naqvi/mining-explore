#!/usr/bin/env python3
"""Build the Fadak AI blog as static pages.

Posts live in _blog/posts/*.html. Each file starts with a JSON header in an
HTML comment, followed by the post body as HTML:

    <!--
    {"slug": "my-post", "title": "...", "summary": "...", "date": "2026-11-15",
     "author": "Ali", "tag": "Field notes"}
    -->
    <p>Body...</p>

Run from the repo root:  python3 _blog/build.py
It writes blog/index.html, blog/<slug>/index.html and sitemap.xml.
The _blog folder is excluded from deploys by .vercelignore.
"""
import datetime as dt
import html
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_blog" / "posts"
OUT = ROOT / "blog"
SITE = "https://www.fadakai.com"

HEAD_COMMON = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#171614">
<script>
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
</script>
<script defer src="/_vercel/insights/script.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="alternate" type="application/rss+xml" title="Fadak AI blog" href="/blog/feed.xml">"""

CSS = """<style>
:root{--bg:#171614;--panel:#1E1D1A;--line:#34322E;--text:#F2F0EB;--soft:#C9C5BE;--muted:#9A9690;--rust:#D9622B}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,system-ui,sans-serif;line-height:1.6}
a{color:var(--text)}a:hover{color:var(--rust)}
.mono{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.wrap{max-width:1200px;margin:0 auto}
header.site{padding:20px 5%;border-bottom:1px solid var(--line)}
header.site .wrap{display:flex;justify-content:space-between;align-items:center;gap:16px 32px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;font-family:'Space Grotesk',system-ui,sans-serif;font-weight:700;font-size:22px;letter-spacing:-.01em}
nav.main{display:flex;align-items:center;gap:8px 28px;flex-wrap:wrap;font-size:15px}
nav.main a{text-decoration:none;padding:12px 0}
nav.main a[aria-current]{color:var(--rust)}
nav.main a.cta{background:var(--rust);color:var(--bg);font-weight:600;padding:12px 20px;border-radius:2px}
.hero{padding:72px 5% 48px;border-bottom:1px solid var(--line);background:radial-gradient(ellipse at 78% 40%,#2A2622 0%,var(--bg) 62%)}
.hero h1{margin:16px 0 12px;font-family:'Space Grotesk',system-ui,sans-serif;font-weight:600;font-size:clamp(40px,5vw,64px);line-height:1.04;letter-spacing:-.03em}
.hero p{margin:0;font-size:19px;color:var(--soft);max-width:36em}
.list{padding:48px 5% 96px}
.list .wrap{display:grid;gap:0}
.card{display:grid;grid-template-columns:minmax(150px,200px) 1fr;gap:12px 40px;padding:32px 0;border-bottom:1px solid var(--line);text-decoration:none}
.card:first-child{border-top:1px solid var(--line)}
.card h2{margin:0 0 10px;font-family:'Space Grotesk',system-ui,sans-serif;font-weight:600;font-size:clamp(24px,2.6vw,32px);line-height:1.15;letter-spacing:-.02em}
.card:hover h2{color:var(--rust)}
.card p{margin:0;color:var(--soft);max-width:44em}
.card .by{margin-top:14px}
@media (max-width:640px){.card{grid-template-columns:1fr}}
article{padding:64px 5% 32px}
article .col{max-width:700px;margin:0 auto}
.crumb{text-decoration:none}
article h1{margin:18px 0 18px;font-family:'Space Grotesk',system-ui,sans-serif;font-weight:600;font-size:clamp(36px,4.6vw,56px);line-height:1.06;letter-spacing:-.03em}
.dek{font-size:20px;color:var(--soft);margin:0 0 28px}
.meta{display:flex;gap:10px 18px;flex-wrap:wrap;padding:16px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin-bottom:40px}
.meta span{color:var(--soft)}
.body{font-size:18px;color:#E4E1DA}
.body p{margin:0 0 22px}
.body h2{margin:44px 0 14px;font-family:'Space Grotesk',system-ui,sans-serif;font-weight:600;font-size:28px;line-height:1.2;letter-spacing:-.02em;color:var(--text)}
.body ul,.body ol{margin:0 0 22px;padding-left:22px}
.body li{margin:0 0 10px}
.body strong{color:var(--text)}
.body blockquote{margin:30px 0;padding:4px 0 4px 22px;border-left:3px solid var(--rust);font-family:'Space Grotesk',system-ui,sans-serif;font-size:24px;line-height:1.3;color:var(--text)}
.body .stat{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(180px,100%),1fr));border:1px solid var(--line);background:var(--panel);margin:30px 0}
.body .stat div{padding:18px 20px;border-right:1px solid var(--line);display:flex;flex-direction:column;gap:4px}
.body .stat div:last-child{border-right:0}
.body .stat b{font-family:'IBM Plex Mono',ui-monospace,monospace;font-weight:500;font-size:26px;color:var(--text)}
.body .stat em{font-style:normal;font-size:14px;color:var(--muted);line-height:1.4}
.sources{margin-top:48px;padding-top:24px;border-top:1px solid var(--line);font-size:14px;color:var(--muted)}
.sources ol{padding-left:20px;margin:12px 0 0}
.sources li{margin-bottom:8px}
.sources a{color:var(--soft)}
.ask{margin:56px 0 0;padding:28px;background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--rust)}
.ask h2{margin:0 0 8px;font-family:'Space Grotesk',system-ui,sans-serif;font-weight:600;font-size:24px}
.ask p{margin:0 0 18px;color:var(--soft)}
.btn{display:inline-block;text-decoration:none;background:var(--rust);color:var(--bg);font-weight:600;padding:13px 22px;border-radius:2px}
.btn:hover{color:var(--bg);filter:brightness(1.08)}
.more{padding:24px 5% 96px}
.more .col{max-width:700px;margin:0 auto}
.more a{display:block;padding:18px 0;border-bottom:1px solid var(--line);text-decoration:none;font-family:'Space Grotesk',system-ui,sans-serif;font-size:20px;font-weight:500}
footer.site{padding:56px 5% 40px;border-top:1px solid var(--line)}
footer.site .wrap{display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap;font-size:14px;color:var(--muted)}
footer.site nav{display:flex;gap:20px;flex-wrap:wrap}
footer.site a{text-decoration:none}
</style>"""

LOGO = '<svg aria-hidden="true" width="26" height="26" viewBox="0 0 26 26"><path d="M3 24 L3 12 Q3 3 13 3 Q23 3 23 12 L23 24" fill="none" stroke="#D9622B" stroke-width="3"></path><rect x="10" y="14" width="6" height="10" fill="#F2F0EB"></rect></svg>'


def header():
    return f"""<header class="site"><div class="wrap">
<a class="brand" href="/">{LOGO}<span>Fadak AI</span></a>
<nav class="main" aria-label="Main">
<a href="/#problem">Problem</a>
<a href="/#build">What we build</a>
<a href="/#technology">Technology</a>
<a href="/blog/" aria-current="page">Blog</a>
<a class="cta" href="/#contact">Talk to us</a>
</nav>
</div></header>"""


def footer():
    return f"""<footer class="site"><div class="wrap">
<span>© {dt.date.today().year} Fadak AI · Toronto, Ontario</span>
<nav aria-label="Footer"><a href="/">Home</a><a href="/blog/">Blog</a><a href="/blog/feed.xml">RSS</a><a href="mailto:ali@fadakai.com">ali@fadakai.com</a></nav>
</div></footer>"""


def nice_date(d):
    return d.strftime("%B %-d, %Y")


def read_minutes(body):
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    return max(1, math.ceil(words / 230))


def load_posts():
    posts = []
    for f in sorted(SRC.glob("*.html")):
        raw = f.read_text()
        m = re.match(r"\s*<!--(.*?)-->(.*)", raw, re.S)
        if not m:
            raise SystemExit(f"{f.name}: missing JSON header comment")
        meta = json.loads(m.group(1))
        meta["body"] = m.group(2).strip()
        meta["date_obj"] = dt.date.fromisoformat(meta["date"])
        meta["minutes"] = read_minutes(meta["body"])
        meta.setdefault("author", "Ali")
        meta.setdefault("tag", "Field notes")
        posts.append(meta)
    posts.sort(key=lambda p: (p["date_obj"], p.get("order", 0)), reverse=True)
    return posts


def page(title, desc, url, inner, extra_head="", og_type="website"):
    t, d = html.escape(title), html.escape(desc)
    return f"""<!doctype html>
<html lang="en">
<head>
{HEAD_COMMON}
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="Fadak AI">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
{extra_head}{CSS}
</head>
<body>
{inner}
</body>
</html>
"""


def build_post(p, posts):
    url = f"{SITE}/blog/{p['slug']}/"
    ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": p["title"],
        "description": p["summary"],
        "datePublished": p["date"],
        "dateModified": p.get("updated", p["date"]),
        "author": {"@type": "Person", "name": p["author"], "worksFor": {"@type": "Organization", "name": "Fadak AI"}},
        "publisher": {"@type": "Organization", "name": "Fadak AI", "logo": {"@type": "ImageObject", "url": f"{SITE}/icon-512.png"}},
        "image": f"{SITE}/og-image.png",
        "mainEntityOfPage": url,
    }
    extra = (f'<meta property="article:published_time" content="{p["date"]}">\n'
             f'<meta name="author" content="{html.escape(p["author"])}">\n'
             f'<script type="application/ld+json">{json.dumps(ld)}</script>\n')
    others = [o for o in posts if o["slug"] != p["slug"]][:3]
    more = "".join(f'<a href="/blog/{o["slug"]}/">{html.escape(o["title"])}</a>' for o in others)
    inner = f"""{header()}
<main>
<article>
<div class="col">
<a class="crumb mono" href="/blog/">← All posts</a>
<h1>{html.escape(p['title'])}</h1>
<p class="dek">{html.escape(p['summary'])}</p>
<div class="meta mono"><span>By {html.escape(p['author'])}</span><span>{nice_date(p['date_obj'])}</span><span>{p['minutes']} min read</span><span>{html.escape(p['tag'])}</span></div>
<div class="body">
{p['body']}
</div>
<aside class="ask">
<h2>How do you check a round today?</h2>
<p>We are preparing underground tests and want to hear from people who run development headings, blast, or supervise crews.</p>
<a class="btn" href="/#contact">Talk to us</a>
</aside>
</div>
</article>
{('<section class="more" aria-label="More posts"><div class="col"><div class="mono" style="margin-bottom:8px">More from the blog</div>' + more + '</div></section>') if more else ''}
</main>
{footer()}"""
    title = f"{p['title']} | Fadak AI"
    return page(title, p["summary"], url, inner, extra, og_type="article")


def build_index(posts):
    url = f"{SITE}/blog/"
    cards = "".join(f"""<a class="card" href="/blog/{p['slug']}/">
<div class="mono">{nice_date(p['date_obj'])}<br>{p['minutes']} min read</div>
<div><h2>{html.escape(p['title'])}</h2><p>{html.escape(p['summary'])}</p><div class="by mono">By {html.escape(p['author'])} · {html.escape(p['tag'])}</div></div>
</a>""" for p in posts)
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": "Fadak AI blog", "url": url,
          "publisher": {"@type": "Organization", "name": "Fadak AI", "logo": {"@type": "ImageObject", "url": f"{SITE}/icon-512.png"}},
          "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}/", "datePublished": p["date"], "author": {"@type": "Person", "name": p["author"]}} for p in posts]}
    inner = f"""{header()}
<main>
<section class="hero"><div class="wrap">
<div class="mono" style="color:var(--rust)">Fadak AI blog</div>
<h1>Notes from the face.</h1>
<p>What we are learning about underground development, measuring every round, and the labour gap in Canadian mining.</p>
</div></section>
<section class="list"><div class="wrap">{cards}</div></section>
</main>
{footer()}"""
    return page("Blog | Fadak AI", "Notes on underground development, per-round measurement, fragmentation and the mining labour gap, from the Fadak AI team.", url, inner,
                f'<script type="application/ld+json">{json.dumps(ld)}</script>\n')


def build_feed(posts):
    items = "".join(f"""<item><title>{html.escape(p['title'])}</title><link>{SITE}/blog/{p['slug']}/</link><guid>{SITE}/blog/{p['slug']}/</guid><pubDate>{dt.datetime.combine(p['date_obj'], dt.time(12)).strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate><author>ali@fadakai.com ({html.escape(p['author'])})</author><description>{html.escape(p['summary'])}</description></item>""" for p in posts)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Fadak AI blog</title><link>{SITE}/blog/</link><description>Notes from the face: underground development, per-round measurement and the mining labour gap.</description><language>en-ca</language>{items}</channel></rss>
"""


def build_sitemap(posts):
    newest = max(p["date"] for p in posts)
    urls = [(f"{SITE}/", newest), (f"{SITE}/blog/", newest)] + [(f"{SITE}/blog/{p['slug']}/", p.get("updated", p["date"])) for p in posts]
    body = "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n'


def main():
    posts = load_posts()
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(build_index(posts))
    (OUT / "feed.xml").write_text(build_feed(posts))
    for p in posts:
        d = OUT / p["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(build_post(p, posts))
    (ROOT / "sitemap.xml").write_text(build_sitemap(posts))
    print(f"built {len(posts)} posts")


if __name__ == "__main__":
    main()
