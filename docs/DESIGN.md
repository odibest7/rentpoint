# RentPoint: Design Plan

This document explains the visual and structural design decisions behind
the front end, so future changes stay consistent with the original intent
rather than drifting toward generic defaults.

---

## 1. Starting point

The brief was explicit: the site should look like a real, professional
product, not a generic AI-generated template. The starting question was
"what does this platform actually sell, to whom, and where?" (not "what
does a rental SaaS landing page usually look like?").

RentPoint serves people renting chairs, canopies, cooking pots, shop space,
and event wear in Nsukka Urban, a Nigerian university town. The design is
built outward from that fact, not from a generic "marketplace startup"
template.

## 2. Colour

| Token | Hex | Used for |
|---|---|---|
| `--color-bg` | `#F8FAFC` | Page background: clean paper, not stark white |
| `--color-ink` | `#0A2342` | Body text, headings |
| `--color-primary` | `#00A896` | Buttons, links, brand mark: a deep teal, evoking market canopy fabric and modern energy |
| `--color-accent` | `#D97706` | Sparingly used warm amber for highlights and notices |
| `--color-border` | `#E2E8F0` | Subtle hairline borders, dividers |

Teal was chosen as the dominant brand colour, with amber kept as a minor accent rather than a co-equal color.

## 3. Typography

- **Outfit / Plus Jakarta Sans**: For headings and running UI text, chosen for clarity, balance, and modern readability across devices.
- **JetBrains Mono**: For anything that is a piece of data rather than prose:
  prices, transaction references, receipt line items. This is a deliberate
  signal to the user ("this number is a fact, not a description") and is
  used consistently across item cards, the checkout page, and receipts.

## 4. The signature element: the receipt stub

The central concern is transparency of transaction records between
customers and item owners. Rather than treating the receipt as an
afterthought, it is given a distinct physical metaphor: an
official electronic ledger receipt rendered with monospace details,
verification badges, and clean tabular layout. It looks and feels like
something you would keep.

## 5. Hero section

The homepage hero connects users directly with verified local equipment,
transparent rates, and live escrow guarantees, backed by real statistics.

## 6. Layout and componentry

- **Item cards** (`_item_card.html` + `.item-card` styles) are the single
  reusable unit for showing a listing, used on the homepage, the catalogue,
  and the "related items" section of the item detail page (one component,
  three contexts, no duplicated markup).
- **Dashboard shell** (`.dashboard-shell`, `_owner_nav.html`) gives item
  owners one consistent sidebar across listings, transactions, and
  earnings, so the dashboard reads as one connected area of the site.
- **Auth pages** use a two-column split (brand statement on one side, form
  on the other) instead of a centered card floating on the page background.

## 7. Responsiveness

Every layout is built with CSS Grid and Flexbox that collapse
smoothly across desktop, tablet, and mobile viewports. The navigation
features an accessible mobile drawer in `static/js/main.js` without any external
frameworks.

## 8. What was intentionally left out

- No third-party UI kit (Bootstrap, Tailwind, or otherwise): the design
  system in `main.css` is hand-written and scoped to exactly what the site
  needs, avoiding heavy third-party dependencies.
- No stock photography or AI-generated imagery: item photos are owner-uploaded
  content (`ItemImage` model).
- No heavy animation library: transitions are native, performant CSS transitions.
