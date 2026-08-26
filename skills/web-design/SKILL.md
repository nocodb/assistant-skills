---
name: web-design
description: A methodology pass for making a web artifact look deliberately designed instead of like a generic AI-generated template — picking a palette, a type scale, and one distinct visual idea before writing markup, then checking contrast and accessibility before shipping. Use before scaffold_web_artifact/publish_web_artifact writes any markup for something the user will actually look at — a landing page, a dashboard, a tool with a real UI. Do NOT use for an artifact that's pure logic with minimal UI (a converter, a JSON formatter) — default styling is fine there; spend the budget where the user will look.
---

# Web design

A page that works is not the same as a page that looks made on purpose. The
gap between them is a handful of decisions made before any markup, not more
code after.

## How to use this skill

### 1. Name the one thing this page is

Before a palette or a font, decide what a visitor should feel or do in the
first second. "A trustworthy financial tool" and "a playful weekend project"
produce different pages from the same feature list. Ground it in the actual
subject, not a generic template — a distinctive choice comes from what's
specific about *this* thing, not from "make it look professional." If you
can't say the one sentence, you'll land on the default: a centered white card,
a blue button, done.

### 2. Pick tokens once, use them everywhere

Decide these before writing a single rule, then never improvise a color or
size ad hoc while coding. Two tiers, and components should only ever touch the
second:

- **Primitives** — the raw values: `--blue-500: #2952cc`, `--space-4: 16px`.
- **Semantics** — what they're *for*, referencing the primitives:
  `--color-text-secondary: var(--gray-500)`, `--space-section-gap:
  var(--space-8)`.

| Token | Decide | Rule of thumb |
|---|---|---|
| Palette | 1 neutral ramp + 1 accent, plus a status ramp only for states you actually show (success/error/warning) | 4–6 named hex values total. One color, one meaning — anything within ~15° hue reads as "the same color" |
| Type scale | 2 fonts max, often 1; a fixed set of sizes (e.g. 14/16/20/28/40) | Ad hoc `font-size` values are what make a page feel improvised |
| Spacing scale | One base unit and its multiples (8/16/24/32/48) | Gap *between* groups should be ≥2× the gap *within* a group — that's what makes related things read as related |
| Radius + shadow | One corner radius, one shadow depth, reused everywhere | Mixing sharp and rounded, or three shadow strengths, reads as unfinished |

A ramp (not a single color) should have roughly even perceived-lightness
steps, constant hue, and vividness peaking mid-ramp — don't hand-pick five
unrelated shades and call it a palette.

### 3. Avoid the templates everyone lands on

Three color/type combinations show up so often in AI-generated pages that
landing on one *is* the tell — pick a direction that isn't one of these:

1. Warm cream background (`#F4F1EA`-ish) + high-contrast serif + terracotta
   accent
2. Near-black background + a single acid-green or vermilion accent
3. Broadsheet hairline rules, zero border-radius, newspaper-style columns

Same for layout defaults — not banned individually, but landing on several
together with nothing else going on is what reads as generic:

- Purple-to-blue gradient hero
- Centered card, generic sans-serif, everything `border-radius: 8px`
- A hero that just restates the h1 in smaller gray text underneath
- Icon-in-a-circle feature grid, three even columns, identical weight
- Drop shadows on everything, or glassmorphism as the entire visual idea

The fix isn't avoiding all of these forever — it's picking **one thing that's
actually a choice** and following it through consistently: an asymmetric or
editorial layout instead of three even columns, a typographic personality (a
distinctive display face for headings against a plain body font), a
restrained and specific palette instead of default blue, real motion instead
of a static page. Spend your boldness in one place, not five timid ones.

### 4. Make the hero say something

The top of the page is the thesis, not a banner. If the h1 is generic enough
to sit on any product ("Welcome to X" / "The best way to Y"), it hasn't done
its job — say the specific thing this page is for. Numbered structure (01/02/03,
step markers) only when the content is genuinely sequential; a decorative
number is another generic-template tell.

### 5. Build with the tokens, then check it

Write CSS/components against the palette and scale from step 2. Before
publishing, check two things a build can't catch for you:

**Contrast** — fix by moving lightness, never hue:

| Text role | WCAG 2 minimum | Better |
|---|---|---|
| Body text | 4.5:1 | 7:1 |
| Large text (≥24px, or ≥18.5px bold) | 3:1 | 4.5:1 |
| UI components / icons | 3:1 | — |

**Accessibility floor:**

- Native elements first — `<button>`/`<a href>` over a `<div>` with a click
  handler; you get focus, keyboard activation, and semantics for free.
- `:focus-visible` with a visible ≥2px outline on every interactive element —
  never `outline: none` without a real replacement.
- Hit targets ≥24×24px minimum, 44×44px for anything primary — pad via a
  pseudo-element around a visually smaller control rather than inflating it.
- Wrap non-essential motion in `@media (prefers-reduced-motion: no-preference)`
  — under reduced-motion, kill autoplay/parallax and swap slide/scale
  transitions for a plain opacity crossfade. Keep functional feedback (loading
  spinners, instant state changes) either way.
- Labels always — `<label for>`, never a placeholder standing in as the only
  label.

Look at the result the way a visitor would: does the hero read in one glance,
is spacing consistent, is there exactly one thing that makes this page
distinct rather than zero or five.

## Polish details worth the extra few minutes

These are optional but cheap on a small artifact — apply what fits rather than
none of it:

- **Press feedback**: `scale(0.96)` on `:active`, as a CSS `transition`
  (interruptible), never a keyframe animation.
- **Icon stroke width** tracks adjacent text weight: ~1.5px next to regular
  (400) body text, ~2px next to medium/semibold (500–600), ~2.5px next to
  bold (700). One outline icon set with `currentColor`, not separate assets
  per state.
- **High-frequency interactions** (hover, toggle) get instant feedback or a
  transition ≤150ms on a *named* property (`transition: background-color
  120ms ease-out`, never `transition: all`) — motion should never be the only
  feedback channel.
- **Concentric radii**: an inner element's corner radius plus its padding
  should roughly equal the outer container's radius, so nested rounded shapes
  look intentional rather than arbitrary.
- Reserve borders for real structural dividers (table cells, separators); use
  a soft shadow for elevation instead of a border where you want a surface to
  read as "raised," not "outlined."

## Guidelines

- **Self-contained still applies.** A system font stack
  (`-apple-system, "Segoe UI", sans-serif`, etc.) renders instantly and always
  works; an external webfont is a dependency you haven't verified survives the
  sandboxed iframe. Prefer a strong system stack with real size/weight
  contrast over risking one.
- **Don't over-invest in a converter or a pure-logic tool.** A JSON formatter
  or unit converter earns clean, consistent spacing and type — not a hero
  section or a mood. Spend the design budget where the user actually looks.
- **Consistency beats novelty.** A page using the same 4 tokens everywhere
  looks more designed than one with more "creative" per-element choices.
- **Typography basics**: rarely more than 2–3 fonts; below 18px stay at weight
  400+ (thin weights disappear at text size); line-height ~1.1 for headings,
  1.5–1.6 for body; cap line length at 60–75 characters; use
  `font-variant-numeric: tabular-nums` on any value that changes in place
  (timers, live counters, prices).
- **Dark mode is optional, contrast isn't.** If you don't have time to design
  both themes, ship one properly rather than a light theme with dark-only
  contrast ratios or vice versa.
