# Draft List Generator

Pulls the current draft beer list from Toast POS and produces:
- `draft_list.pdf` — landscape, ready to upload to your WordPress site
- `draft_list.html` — self-contained, auto-refreshing page for the bar TV

The whole thing is a single Python script. No database, no server required to test it. Schedule it on a cron and you're done.

## Files in this folder

| File | What it is |
|---|---|
| `01_TOAST_ACCESS_REQUEST.md` | Step-by-step for getting Toast API credentials, plus the description-field convention the manager will use |
| `generate_draft_list.py` | The generator |
| `sample_menu.json` | Realistic Toast menu response — used when you run with `--sample` |
| `.env.example` | Copy to `.env` and fill in your Toast credentials |
| `requirements.txt` | Python dependencies |
| `draft_list.pdf` / `draft_list.html` | Sample outputs (regenerate any time) |

## Try it right now (no Toast access required)

```bash
pip install -r requirements.txt
python generate_draft_list.py --sample
```

That generates `draft_list.pdf` and `draft_list.html` from the bundled sample menu. Open them — that's exactly what your live outputs will look like, just with your real beers.

## Going live

1. Get Toast API credentials — see `01_TOAST_ACCESS_REQUEST.md` for the exact ask to send Toast support.
2. `cp .env.example .env` and paste in your `TOAST_CLIENT_ID`, `TOAST_CLIENT_SECRET`, and `TOAST_RESTAURANT_GUID`.
3. Make sure the manager has moved your drafts into a Toast menu group named `Draft Beer` (or set `DRAFT_GROUP_NAME` in `.env` to whatever you call it).
4. Make sure beer details follow the description format described in `01_TOAST_ACCESS_REQUEST.md`:
   ```
   Style: West Coast IPA | ABV: 6.5% | Tap: 3
   ```
   (Tasting notes can go before the style: `Crisp finish. Style: Pilsner | ABV: 5.0% | Tap: 4`)
5. Run it:
   ```bash
   python generate_draft_list.py
   ```

## Running it for both facilities

Toast scopes everything to a single restaurant GUID, so each of your two facilities (the 24-tap and the 16-tap) is a separate Toast restaurant from the API's perspective. The cleanest setup is a `.env` file per location:

```
draft-list/
  generate_draft_list.py
  westside/
    .env             # TOAST_RESTAURANT_GUID for the 24-tap, BAR_NAME=On Tap — Westside
    draft_list.pdf
    draft_list.html
  eastside/
    .env             # TOAST_RESTAURANT_GUID for the 16-tap, BAR_NAME=On Tap — Eastside
    draft_list.pdf
    draft_list.html
```

Run with `--output-dir` to keep them separate, sourcing the per-location `.env`:

```bash
( set -a; . westside/.env; set +a; python generate_draft_list.py --output-dir westside )
( set -a; . eastside/.env; set +a; python generate_draft_list.py --output-dir eastside )
```

Both facilities run on the same cron tick. The layout auto-adjusts: 24 taps gets two dense columns, 16 taps gets two roomier columns with extra breathing room.

## Schedule it

The script is designed to be re-run on a schedule. Toast's rate limit is 1000 requests/min per location — you're nowhere near that.

**Cron, every 5 minutes:**
```cron
*/5 * * * * cd /opt/draft-list && /usr/bin/python3 generate_draft_list.py >> /var/log/draft-list.log 2>&1
```

**systemd timer:** create `draft-list.timer` with `OnCalendar=*:0/5` if your distro prefers it.

**GitHub Actions:** if you'd rather not run a server, a workflow on a 5-minute `schedule:` trigger can run the script and commit the outputs to a `gh-pages` branch — that gives you free hosting at `https://<you>.github.io/<repo>/draft_list.html`. Stash your Toast credentials in repository secrets.

## Hosting the outputs

You need these two files reachable at stable URLs. A few easy options:

| Where | Setup time | Notes |
|---|---|---|
| WordPress media library | 5 min | Manual: upload `draft_list.pdf` after each generation. Skip if you want zero-touch. |
| GitHub Pages | 30 min | Free, automated via GitHub Actions. The TV loads `https://<you>.github.io/<repo>/draft_list.html`. WordPress links to the same domain for the PDF. |
| Cloudflare R2 / S3 + Cloudflare | 30 min | Cron uploads both files after each run via `aws s3 cp`. Custom domain. Works great. |
| Self-hosted (Pi at the bar) | 1 hr | Run `python -m http.server` on a Raspberry Pi behind your router. The TV loads `http://192.168.x.x:8000/draft_list.html`. Cheapest, no internet required for the TV. |

## Wiring up WordPress

Two patterns:

**Pattern A — link to the PDF (matches your current workflow).**
Add a button on your beer page: `<a href="/wp-content/uploads/draft_list.pdf" target="_blank">Download today's draft list (PDF)</a>`. After each cron run, copy/upload the PDF to the media library. Or, if you host on GitHub Pages / S3, just link to the public URL — no upload step needed.

**Pattern B — embed the live HTML page.**
Use an `<iframe>` so the menu page on your site updates instantly when the kegs change:

```html
<iframe src="https://<your-host>/draft_list.html"
        style="width:100%; height:90vh; border:0;"
        loading="lazy"
        title="On tap right now"></iframe>
```

Pattern B beats Pattern A long-term because the website matches the TV exactly with no upload step.

## Pointing the TV at the live page

Whatever device drives the TV (Pi, Mac mini, Fire TV stick, smart TV browser), open the HTML URL in fullscreen kiosk mode.

**Raspberry Pi (most common at bars):**
```bash
chromium-browser --kiosk --noerrdialogs --disable-infobars \
  --check-for-update-interval=31536000 \
  https://<your-host>/draft_list.html
```
Drop that into `/etc/xdg/lxsession/LXDE-pi/autostart` and the TV comes back up automatically after a power cycle.

**Mac mini:** open the URL in Chrome and press ⌘+Shift+F for fullscreen.

The page already has `<meta http-equiv="refresh" content="300">` baked in — the browser auto-reloads every 5 minutes, so the TV picks up the next cron-generated update on its own.

## Troubleshooting

- **"Found 0 beer(s) in 'Draft Beer' group."** — The group name in Toast doesn't match `DRAFT_GROUP_NAME`. Either rename the group in Toast or update `.env`.
- **"Missing required env vars"** — You haven't filled in `.env` (or you're running outside the script directory). Use `--sample` to generate from sample data instead.
- **Brewery/style fields are blank in the output** — Check the item description in Toast. The format is strict: `Brewery: X | Style: Y | ABV: Z%`. Run `python -c "from generate_draft_list import parse_description; print(parse_description('your description here'))"` to debug.
- **Toast API returns 401** — Your client secret is wrong, or the account doesn't have the `menus:read` scope. Re-check what Toast support sent.
- **Toast API returns 403** — The `Toast-Restaurant-External-ID` header doesn't match a restaurant your client has access to. Confirm the restaurant GUID with Toast support.

## What this tool deliberately does *not* do

- **Write back to Toast.** Read-only. The manager still updates Toast as the source of truth.
- **Track inventory / kegs remaining.** Toast can do that separately; not in scope here.
- **Style the website itself.** The HTML is intentionally drop-in via iframe. If you want it to inherit your WordPress theme, swap the `<style>` block for something matching your site or build it as a WordPress shortcode.
