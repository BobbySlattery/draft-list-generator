# GitHub Pages Deployment — Setup Guide

End state: every 15 minutes, a GitHub Action authenticates against Toast, regenerates the PDF + HTML, and publishes them to a live URL like `https://fiftywest-brewing.github.io/draft-list/deerfield/draft_list.html` (or whatever you name your repo). The TV opens that URL in kiosk mode. WordPress embeds the same URL via iframe.

Total setup time: ~30 minutes the first time. Zero maintenance after.

## Prerequisites

- A GitHub account ([sign up free](https://github.com/signup) if you don't have one — use a Fifty West email if you want it tied to the brewery)
- Git installed on your Mac. To check: open Terminal and run `git --version`. If you get "command not found", install with `xcode-select --install` (takes ~5 min).

## Step 1 — Create the repository

1. Go to https://github.com/new
2. **Repository name**: `draft-list` (or whatever — this becomes part of the URL)
3. **Description**: "Fifty West live draft list — pulled from Toast POS"
4. **Public** vs **Private** — pick one:
   - **Public** (recommended): free GitHub Actions minutes are unlimited; site URL works without paying for GitHub Pro. Source code is visible to anyone, but Toast credentials stay in encrypted secrets so they're never exposed. The brand fonts in the repo are visible — make sure your font licenses allow this. Brandon Grotesque and Goudy Heavyface usually allow web embedding under typical desktop licenses, but check your specific license terms if unsure.
   - **Private**: requires GitHub Pro ($4/month) for GitHub Pages to work. Source code stays private, including the fonts.
5. **Don't** check "Add a README", "Add .gitignore", or "Choose a license" — we have those already.
6. Click **Create repository**.

GitHub will show you a page with setup commands. Keep that page open — we'll use them.

## Step 2 — Push the code

In Terminal, navigate to the project folder and push:

```bash
cd "/Users/maxfram/Library/Application Support/Claude/local-agent-mode-sessions/b420bed1-be31-4e30-b9fc-b9f733f68930/a5fc5c72-6e03-493d-9f84-29726eb44b64/local_ac487c74-be6b-494b-b7a6-12faffa22452/outputs/draft-list-tool"

git init
git add .
git commit -m "Initial commit: Fifty West draft list generator"

# Replace YOUR-USERNAME and YOUR-REPO-NAME below with what you used
git remote add origin https://github.com/YOUR-USERNAME/draft-list.git
git branch -M main
git push -u origin main
```

If git asks for a username and password, the password isn't your GitHub password — it's a "Personal Access Token". Generate one at https://github.com/settings/tokens (click "Generate new token (classic)", give it the `repo` scope, and use the token as the password).

> The `.gitignore` I included will keep your `.env` file (with Toast credentials) **out** of the repo. You can verify by running `git status` — `.env` should not appear in the list of files to commit.

## Step 3 — Add Toast credentials as encrypted secrets

These never appear in the code, only injected into the workflow at runtime.

1. Go to your repo on GitHub: `https://github.com/YOUR-USERNAME/draft-list`
2. Click **Settings** → **Secrets and variables** → **Actions** (left sidebar)
3. Click **New repository secret** and add these three secrets, one at a time:

| Name | Value |
|---|---|
| `TOAST_CLIENT_ID` | Your Toast client ID |
| `TOAST_CLIENT_SECRET` | Your Toast client secret (the rotated one, not the one you pasted in chat) |
| `DEERFIELD_GUID` | `75d6444e-6353-4864-aac4-50949e88b6f9` |

Optional (when you add Wooster Pike later):

| Name | Value |
|---|---|
| `WOOSTER_PIKE_GUID` | `98f61e78-56f2-4108-beb0-d7128007567e` |

## Step 4 — Enable GitHub Pages

1. In your repo, go to **Settings** → **Pages** (left sidebar)
2. Under "Build and deployment", set **Source** to **GitHub Actions**
3. That's it — no other settings to change.

## Step 5 — Trigger the first run

Two ways:

- Push any tiny change (e.g., edit the README and commit), or
- Go to the **Actions** tab → click "Update Draft List" workflow → click **Run workflow** → confirm

The workflow takes ~1 minute to complete. You'll see a green checkmark when it succeeds. If it fails, click into the run for the error log.

After it succeeds, the live URL will be:

```
https://YOUR-USERNAME.github.io/draft-list/deerfield/draft_list.html
```

(Replace `YOUR-USERNAME` and adjust if you named the repo differently.)

There's also a landing index at `https://YOUR-USERNAME.github.io/draft-list/` that links to both locations.

## Step 6 — Wire it up

**TV (Deerfield)**: open the URL in Chrome kiosk mode. On a Mac mini:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --kiosk --noerrdialogs --disable-infobars \
  https://YOUR-USERNAME.github.io/draft-list/deerfield/draft_list.html
```

On a Raspberry Pi: drop the equivalent into `/etc/xdg/lxsession/LXDE-pi/autostart`.

**WordPress**: add an iframe to whichever page should show the tap list:

```html
<iframe src="https://YOUR-USERNAME.github.io/draft-list/deerfield/draft_list.html"
        style="width:100%; height:90vh; border:0;"
        loading="lazy"
        title="On tap right now"></iframe>
```

Plus a download button for the PDF if you want one:

```html
<a href="https://YOUR-USERNAME.github.io/draft-list/deerfield/draft_list.pdf"
   target="_blank" rel="noopener">Download today's tap list (PDF)</a>
```

## How updates flow once it's live

1. Manager taps a new keg → updates the Toast item (name + description) → hits **Publish** in Toast Web
2. Within 15 minutes, the GitHub Action runs on schedule
3. Action authenticates against Toast → pulls the menu → renders new PDF + HTML → publishes to GitHub Pages
4. The TV refreshes itself every 5 minutes (built into the HTML), so it picks up the change within ~20 minutes total
5. WordPress iframe also auto-refreshes since it's pulling the same live HTML

If the manager wants the change to appear immediately (e.g., for a special event), they can manually trigger the workflow from the Actions tab — runs in ~1 minute.

## Adding Wooster Pike

Once Deerfield is live and you're ready to add the second location:

1. Add `WOOSTER_PIKE_GUID` to your GitHub secrets (Step 3 above)
2. Open `.github/workflows/update-draft-list.yml` and uncomment the "Wooster Pike" step (delete the `#` characters at the start of each line)
3. Also uncomment the corresponding line in the index page generation
4. Commit and push:
   ```bash
   git add .github/workflows/update-draft-list.yml
   git commit -m "Add Wooster Pike location"
   git push
   ```
5. Wooster Pike URL will be: `https://YOUR-USERNAME.github.io/draft-list/wooster-pike/draft_list.html`

## Troubleshooting

- **Workflow fails at "Generate Deerfield draft list"** — usually a Toast credentials issue. Check the secrets are set correctly. Click into the failed run, expand that step, look at the error.
- **Workflow succeeds but Pages URL shows 404** — go to Settings → Pages and confirm Source is set to "GitHub Actions". The first deploy can take a couple extra minutes to propagate.
- **Cron isn't firing on time** — GitHub Actions cron is best-effort. During high-load periods it can be delayed by 10–30 min. The `workflow_dispatch` button gives you an immediate trigger if you need it.
- **Your repo went 60 days without activity** — GitHub auto-disables scheduled workflows after 60 days of inactivity. Just push any tiny commit and it re-enables. Adding any tap update through the workflow_dispatch trigger also resets the timer.
