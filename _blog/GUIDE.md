# Fadak AI blog: how a weekly post gets written

This folder is not deployed (see `.vercelignore`). It holds the post sources, the build script and this guide.

## Cadence
- One post a week, dated the Tuesday it is published (Toronto date).
- Author is always **Ali**.

## Picking the topic
- Take the first unchecked topic in `TOPICS.md`. Skip one only if fresh research shows it can't be written honestly with public sources; note why next to it.
- After publishing, tick it and add the date and slug.
- If the list runs low (fewer than 3 unchecked), add new ideas at the bottom that fit the themes below.

## Themes
Underground development and the blast cycle; measuring rounds (pull, overbreak, oversize); fragmentation and its downstream cost; the Canadian mining labour gap; practical physical AI and automation in mines; Northern Ontario and the Sudbury mining cluster; what Fadak AI is learning while it builds.

## Voice and format
- Plain, direct, written for mine engineers, blasters, shift supervisors and development contractors. No hype words, no AI-startup clichés.
- 500–900 words. Short paragraphs, `<h2>` sections, at most one `<blockquote>` pull line and at most one `<div class="stat">` block with three numbers.
- Write in "we" for Fadak AI. Keep to what the homepage says the products are: **Round Check** (per-round grade for pull, overbreak and oversize) and **GrainSight** (fragmentation from images).
- End with a `<div class="sources">` list in the same format as earlier posts.

## Honesty rules (non-negotiable)
- Fadak AI is **pre-pilot**, preparing underground tests at the NORCAT Underground Centre in Sudbury. Never claim customers, pilots, partnerships, results, accuracy figures or deployments that don't exist.
- Do not mention OVIN or any funding.
- Every number needs a public source found in the run, named in the text and linked in Sources. If a figure can't be verified, leave it out.
- Industry benchmarks are described as industry figures, never as Fadak's results.
- Competitors can be described by category; only name a company when stating a public fact about it, neutrally.
- Quotes from sources: under 15 words, at most one per source. Paraphrase everything else.

## Mechanics
1. Add `_blog/posts/NN-<slug>.html` (next number) with the JSON header: slug, title, summary (1–2 sentences), date (YYYY-MM-DD), author "Ali", tag (Company, Explainer, Industry, Field notes or Engineering).
2. Run `python3 _blog/build.py` from the repo root.
3. Check the built page renders and internal links resolve; commit and push to `main`. Vercel deploys from `main` to www.fadakai.com.
