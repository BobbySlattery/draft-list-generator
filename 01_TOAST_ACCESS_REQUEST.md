# Getting Toast API Access — Action Packet

You can't pull from Toast until you have API credentials. Toast doesn't expose a self-serve API key in the admin UI — restaurants get credentials through a program called **Standard API Access**. Here's the whole path.

## Prerequisites (check these first)

You (or whoever requests it) need all of the following:

1. An active **Toast Restaurant Management Suite (RMS) Essentials** subscription or higher. If you're on a lower tier, you need to upgrade — Toast Shop sells RMS directly.
2. The **Manage Integrations** permission on your Toast Web account. The owner can grant this in **Toast Web → Employees → Roles**.
3. You must be an **active employee** of the location you're requesting credentials for.

## Step 1 — Submit the request

Open a Toast Support ticket at https://central.toasttab.com (or email your assigned Toast rep). Use the message below as a starting point — fill in the bracketed fields.

---

**Subject:** Standard API Access request — [Your Bar Name] — Internal menu/draft list integration

Hi Toast team,

We'd like to request Standard API Access credentials for our location. We're building an internal tool that pulls our current draft beer menu from Toast and generates a printable list for our website plus a live display for the TV monitor at the bar. This eliminates double-entry between Toast and our existing PDF.

**Restaurant details**
- Business name: [Your Bar Name]
- Restaurant GUID: [find in Toast Web → bottom of any page, or ask support]
- Primary contact: [Your name, email, phone]
- Toast subscription tier: [RMS Essentials / Plus / etc.]

**Integration scope**
- First-party / internal use only (not a reseller integration)
- Read-only — no writes back to Toast
- Single location to start
- Expected request volume: ~1 call every 5 minutes (well under rate limit)

**Scopes we need**
- `menus:read` (to pull the Draft Beer menu group and item details)
- `restaurants:read` (to validate the location GUID at startup)

**Endpoints we'll call**
- `GET /menus/v2/menus` — pull the full menu, filter client-side to the Draft Beer group

Could you create a Standard API Access client for our **production** environment and send the client ID, client secret, and our restaurant GUID? Happy to provide any additional context.

Thanks,
[Your Name]

---

## Step 2 — While you wait

Toast typically takes 3–10 business days. Use that time to do two things:

### A. Create the Draft Beer menu group in Toast (if you don't have one)

Toast Web → **Menus** → create a Menu Group called exactly **"Draft Beer"** (or whatever name you choose — just remember it for the config). Move all current draft items into it. The generator filters by group name, so consistency matters.

### B. Standardize beer metadata in the item description field

Today the style / ABV / tap# only live in the editable PDF. Move them into Toast as part of the item description, using a simple pipe-separated key:value format the generator can parse:

```
Style: West Coast IPA | ABV: 6.5% | Tap: 3
```

Rules:
- Keys are case-insensitive but must match these names exactly: `Style`, `ABV`, `Tap`.
- Order doesn't matter.
- Missing keys are fine — the generator will leave that column blank.
- Anything before the first key (or in its own pipe-separated chunk) is treated as a free-text tasting note that appears next to the style under the beer name.

Example with a tasting note:
```
Crisp, dry, light citrus finish. Style: Belgian Wit | ABV: 5.2% | Tap: 7
```

This is the **only** discipline change for the manager: when they add a new keg, they update Toast (which they already do for POS) and they include the structured description. No second system to touch.

> Note: the parser also still accepts `Brewery:` and `Glass:` fields if you ever want to bring them back — they're parsed silently but not displayed.

## Step 3 — When credentials arrive

Drop them into the `.env` file shipped with the generator (see the README) and you're live.

## What if we never get Standard API Access?

A few fallback paths if Toast says no or it drags on:

- **OptiSigns** — third-party digital signage with a built-in Toast connector. Solves the TV side but not the WordPress PDF.
- **Manual JSON export** — Toast Web supports exporting menu data as JSON; the generator can run against that file as a backstop. Adds a manual export step but still removes the editable-PDF maintenance burden.

Useful Toast docs:
- [Standard API Access overview](https://support.toasttab.com/en/article/Standard-API-Access)
- [Standard API access requirements](https://doc.toasttab.com/doc/devguide/devApiAccessRequirements.html)
- [Menus API overview](https://doc.toasttab.com/doc/devguide/apiGettingMenuInformationFromTheMenusAPI.html)
- [Toast developer portal](https://doc.toasttab.com/doc/devguide/apiDeveloperPortal.html)
