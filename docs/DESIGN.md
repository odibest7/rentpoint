# RentPoint — Design plan

This document explains the visual and structural design decisions behind
the front end, so future changes stay consistent with the original intent
rather than drifting toward generic defaults.

---

## 1. Starting point

The brief was explicit: the site should look like a real, professional
product, not a generic AI-generated template. The starting question was
"what does this platform actually sell, to whom, and where?" — not "what
does a rental SaaS landing page usually look like?"

RentPoint serves people renting chairs, canopies, cooking pots, shop space,
and event wear in Nsukka Urban, a Nigerian university town. The design is
built outward from that fact, not from a generic "marketplace startup"
template.

## 2. Colour

| Token | Hex | Used for |
|---|---|---|
| `--color-bg` | `#F7F6F2` | Page background — warm paper, not stark white |
| `--color-ink` | `#17242B` | Body text, headings |
| `--color-primary` | `#1F5D56` | Buttons, links, brand mark — a deep teal, evoking market canopy fabric and agbada cloth |
| `--color-accent` | `#E0A63E` | Sparingly used marigold gold — Ankara/event-fabric warmth, for highlights and the secondary CTA |
| `--color-brick` | `#8C4A31` | Reserved for status accents, used sparingly |
| `--color-line` | `#E4E0D6` | Hairline borders, dividers |

Deliberately **not** used: the cream-background-plus-terracotta-orange
combination that has become a visual shorthand for "AI-generated startup
site." Teal was chosen as the dominant brand colour instead of orange for
that reason, with gold kept as a minor accent rather than a co-equal color.

## 3. Typography

- **Fraunces** (display serif) for all headings and the brand wordmark. It
  has warmth and character that a generic sans-serif does not, without
  reading as a "creative agency" font.
- **Inter** (body sans-serif) for all running text, form labels, and UI
  chrome — chosen for legibility at small sizes across devices.
- **IBM Plex Mono** for anything that is a piece of data rather than prose:
  prices, transaction references, receipt line items. This is a deliberate
  signal to the user — "this number is a fact, not a description" — and is
  used consistently across item cards, the checkout page, and receipts.

## 4. The signature element: the receipt stub

The report's central concern is transparency of transaction records between
customers and item owners. Rather than treating the receipt as an
afterthought, it is the one page given a distinct physical metaphor: a
paper receipt with a dashed tear-line and a jagged/perforated bottom edge
(`.receipt`, `.receipt-jag` in `main.css`), rendered in the monospace face
for all data rows. It is meant to look and feel like something you would
keep, not like a generic "success" toast.

## 5. Hero section

Instead of a generic gradient block with abstract stats, the homepage hero
shows an actual listing card (a canopy-and-chairs rental) styled exactly
like the real item cards used throughout the catalogue. The product is the
hero image, not a stock illustration.

## 6. Layout and componentry

- **Item cards** (`_item_card.html` + `.item-card` styles) are the single
  reusable unit for showing a listing, used on the homepage, the catalogue,
  and the "related items" section of the item detail page — one component,
  three contexts, no duplicated markup.
- **Dashboard shell** (`.dashboard-shell`, `_owner_nav.html`) gives item
  owners one consistent sidebar across "My listings," "Transactions," and
  "Earnings," so the dashboard reads as one connected area of the site
  rather than three disconnected pages.
- **Auth pages** use a two-column split (brand statement on one side, form
  on the other) instead of a centred card floating on the page background,
  which is the layout most template-generated auth pages default to.

## 7. Responsiveness

Every layout is built with CSS Grid using `auto`/`fr` tracks that collapse
at two breakpoints (960px and 680px): multi-column grids drop to one or two
columns, the dashboard sidebar moves above the content, and the desktop nav
links collapse behind a hamburger toggle handled by a few lines of vanilla
JavaScript in `static/js/main.js` (no framework, no build step). This was
verified by resizing the rendered pages, not assumed from the CSS alone.

## 8. What was intentionally left out

- No third-party UI kit (Bootstrap, Tailwind, or otherwise) — the design
  system in `main.css` is hand-written and scoped to exactly what the site
  needs, per the brief's instruction to avoid heavy third-party
  dependencies.
- No stock photography or AI-generated imagery — item photos are left as
  owner-uploaded content (`ItemImage` model); until an owner uploads a
  photo, the card shows the brand-teal placeholder rather than a fake
  product photo.
- No animation library — the few transitions used (card hover lift, button
  press) are plain CSS transitions.
