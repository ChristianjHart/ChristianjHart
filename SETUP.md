# Setup

This turns your GitHub profile README into a self-updating page: a daily
GitHub Action redraws your contribution graph, streaks, and language stats
as custom SVGs (not GitHub's stock widgets), and an on-demand action turns a
photo into an ASCII portrait in the same style. Nothing is embedded from a
third-party server, so nothing here can rate-limit or go dark.

## 1. Create the special repo

Create a new **public** repository named exactly your GitHub username
(e.g. if you're `octocat`, the repo must be named `octocat`). GitHub
auto-detects this and shows its README on your profile page.

Push everything in this folder to that repo.

## 2. Generate the fonts (one-time)

The graphics inline a subset of JetBrains Mono so they render identically
for every viewer, regardless of what monospace fonts they have installed.

1. Go to the repo's **Actions** tab.
2. Run **"prepare fonts"** manually (workflow_dispatch).
3. It downloads JetBrains Mono, subsets it with fonttools, and commits
   `scripts/fonts/*.woff2`. You only need to do this once.

(This step needs internet access to github.com/JetBrains, which is why it
runs in Actions rather than needing you to have fonttools installed locally.)

## 3. Add your photo and generate the portrait

Locally (this step does need Pillow on your own machine, since there's no
scheduled workflow for it):

```
pip install pillow
python3 scripts/generate_ascii.py assets/your-photo.jpg -o ascii.svg
git add ascii.svg assets/your-photo.jpg
git commit -m "portrait: add ascii.svg"
git push
```

Re-run this any time you want to swap the photo. Tune `--cols` (default 140)
if the grid looks too dense or too sparse for your image.

## 4. Turn on the daily stats job

The `stats.yml` workflow already targets `${{ github.repository_owner }}`,
so it automatically summarizes whoever owns the repo — no edits needed.
It runs once a day and only commits if something actually changed. You can
also trigger it manually from the Actions tab to see it work immediately.

## 5. Fill in README.md

Replace the placeholders in `README.md`: your name (alt text on the
portrait), your links, your bio, your stack, and your project list. The
stat graphics (`stats.svg`, `streak.svg`, `langs.svg`, `year.svg`,
`hd-*.svg`) don't need editing — the workflow keeps them current.

## How it fits together

| File | What it is | How it's produced |
|---|---|---|
| `ascii.svg` | Your photo, as ramp characters | run locally, on demand |
| `stats.svg` | Hero contribution count + weekly sparkline | daily Action |
| `streak.svg` | Current / longest streak | daily Action |
| `langs.svg` | Top languages, by bytes and by repo | daily Action |
| `year.svg` | The year as a character map | daily Action |
| `hd-*.svg` | Section heading images (custom typeface) | daily Action |
| `scripts/fonts/*.woff2` | JetBrains Mono, subset + base64-inlined | one-time Action |

Everything shares the same ink color, monospace face, and left-to-right
"typing" reveal animation (SMIL, since GitHub strips `<script>` from
READMEs) — that's what makes it read as one page instead of a pile of
separate badges.
