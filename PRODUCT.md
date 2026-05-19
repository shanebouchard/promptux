---
register: brand
---

# PromptUX

A small strategic design consultancy. Principal-led, AI-native, no layers between client and senior practitioners. The website is a marketing site — design is the product.

## Users

Founders, operators, and product leaders at funded startups and scaleups who are building something they care about and need an outside design partner who can think strategically, execute fast, and use AI operationally rather than as a talking point. They've worked with agencies before and know what cohort they're in: people for whom "we'd assign a senior" is a euphemism for "you'll get a junior with a senior on a status call." PromptUX inverts that. The website's job is to make this credible at a glance — that the people on the page are the people doing the work.

## Product purpose

Convert qualified prospects into a Sprint or Partnership engagement. The Sprint is a 3-week mapping engagement at $15K–$25K; the Partnership is ongoing embedded leadership at $20K–$40K/mo. The site has to do three things in order: prove credibility (selected work, named partners, real outcomes), articulate a point of view (senior thinking, AI speed, no layers), and get the prospect to a contact action.

The current homepage already has the structure: hero, work (4 case studies — Lace AI Pro, SharpSpring, Pickers, PL Remote), how-we-work principles, two engagement formats, the team, and a contact CTA. The case studies open in a slide-in panel for depth without leaving the page. The job of design here is to dress this same content in a register that lands with each prospect's instincts about what "premium" looks like.

## Voice

Confident, terse, founder-direct. Not chatty. Not modest. Not corporate. The tagline "Because how you direct AI is itself a design decision" is the register. Short sentences. Specifics over slogans (74.8% adoption beats "drove growth"). The principles are written in commands: *Start with the opportunity, not the deliverable. Use AI operationally, not as a talking point. Embed, don't deliver and disappear. We share what we actually think.* That cadence is the brand.

Words to avoid: synergy, partner-up, leverage as a verb, ecosystem, unlock, journey, holistic. Em dashes (use commas / periods / semicolons). Em-dash-shaped writing in general — long parenthetical asides that trail off. Stop earlier.

## Brand positioning

- **Principal-led**: the founders do the work; there's nobody to escalate to because there's no layer between client and partner.
- **AI-native**: they use AI in their actual practice, not as a service offering. The output is faster and better; the prospect benefits, the methodology is invisible.
- **No layers**: no juniors, no account managers, no presentation theater. The team is small on purpose.

## Anti-references

- **Generic SaaS landing pages**: gradient hero, three feature cards, blue CTA, customer logo strip. Wrong cohort.
- **AI-startup aesthetic**: neon green / lime accent on near-black, monospace, terminal vibes. PromptUX uses lime in the current default theme — that is the *one* thing the new themes need to leave behind.
- **Trendy maximalism**: blurry blob gradients, overlapping rotated cards, "playful" type. Reads as cheap.
- **Big agency websites**: Sapient/Huge-style — generic case study grids, dark hero video, "we do everything" services pages. Reads as corporate.
- **Cliché trust signals**: "Trusted by 1000+ companies" with logo wall. Replace with one sharp sentence and let the work do the work.

## Content & messaging system

These are the brand's content rules. They override any guidance above when there's a conflict.

### Hierarchy of comprehension

The reader should understand the takeaway before they read the paragraph. Every section follows this order:

1. **Header** communicates the takeaway, in 1–5 words.
2. **Subtext** makes the takeaway unambiguous and ties it to business or user value.
3. **Visuals** emotionally reinforce and prove the takeaway.
4. **Supporting copy** completes the thought.

If the header needs the paragraph to make sense, the header is wrong.

### Headlines

1–5 words. Sharp. Editorial. Match the cadence of Apple, Linear, Vercel — not consulting framework labels.

Good shape: `AI Speed.` / `Move faster.` / `Less waiting.` / `Smaller teams. Bigger output.` / `Cut the drag.` / `More shots on goal.` / `Faster by design.`

Bad shape (avoid): `AI-enabled capabilities`, `AI-native workflows`, `Operational acceleration systems`, `Integrated delivery frameworks`, `Workflow orchestration`, `End-to-end execution models`. These read internally-focused, process-heavy, emotionally flat, and harder to scan.

### Subtext

Subtext clarifies the headline. It does NOT introduce a new concept. If a paragraph asks the reader to learn something new before they can react to the headline, the headline failed.

### Visuals and diagrams

Visuals reinforce and prove the takeaway. They do not introduce competing conceptual systems.

Diagrams: simple lifecycle, clean loops, clear relationships, minimal labels, high emotional clarity. Not workflow maps, not framework charts, not consulting process wheels. The brand's diagrams compress understanding; they don't require it.

### Sections

Each section has ONE strategic purpose. The reader should immediately know why the section exists. Don't blend capability + philosophy + proof in one block; if you find yourself doing that, split or cut.

### What this site is

A persuasion and positioning tool. It is NOT:

- a methodology deck
- an operational playbook
- an AI education course
- a consulting framework presentation

Goal: perceived capability, clarity, confidence, excitement. Not complete operational transparency.

### AI storytelling

AI positioning focuses on: leverage, acceleration, momentum, iteration, operational compression, output quality, reduced drag.

NOT: workflow ideology, AI philosophy, process theory, technical decomposition. The AI story is simple, powerful, clear, exciting — never a seminar.

### Final feel

The user should leave the site thinking: *"These people move fast, think clearly, and produce high-quality work."* Without needing it explained.

## Constraints

- Single-file HTML (`promptux-homepage.html`). No build step. One stylesheet, one script — both inline.
- Theme system: `[data-theme]` on `<html>`, switched by a fixed pill at bottom-right (`#theme-selector`). Themes are layout transformations, not just color/font swaps.
- Three themes share the same content: Athletic (default), Swiss (OUTFIT-style monochrome editorial), Editorial (this task — premium consulting firm).
- Existing fonts loaded: Big Shoulders Display, DM Sans, Inter, Playfair Display, Source Serif 4. Adding fonts is fine if there's a real reason.
- Case study panel is a slide-in overlay shared across themes (`#cs-panel`). Theme styling cascades into it via CSS variables and `data-theme` selectors.

## Success criteria

When a prospect lands on the Editorial theme, they should feel that they're looking at a *firm* that has been doing this for a long time. Quiet confidence. The work speaks; the navigation chrome doesn't compete. The aesthetic should be illegible to anyone trying to date it: not 2020-modernist, not 2024-glassy, not 2010-corporate. Editorial neutrality with a strong point of view.
