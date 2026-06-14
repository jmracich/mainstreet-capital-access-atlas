# Main Street Capital Access Atlas — Codex Instructions

## Product identity

This is not a generic SaaS dashboard. This is a high-trust civic-finance intelligence product for local partners who want to understand where small-business support conversations should start.

Design reference mood:
- Opportunity Atlas / public-interest data lab
- Bloomberg CityLab / policy briefing
- Federal Reserve research note
- Editorial civic technology
- Serious, warm, usable, evidence-based

Do not make the site look like:
- AI-generated startup landing page
- Neon gradient SaaS template
- Crypto dashboard
- Generic “empower communities” nonprofit page
- Banking sales page
- Dribbble shot with fake polish but poor usability

## Core user jobs

Every page should help users answer one of these:

1. Where should I start looking?
2. Why does this county need follow-up?
3. Can I trust this data?
4. What should I verify locally?
5. What should I do next?

If a section does not answer one of those questions, simplify or remove it.

## Visual direction

Use a restrained, premium civic-data style:
- More whitespace and stronger hierarchy.
- Fewer boxed cards.
- Larger editorial headings.
- Muted warm background, deep ink text, civic teal, amber, and soft data-map colors.
- Use contrast, scale, spacing, and rhythm instead of decorative gradients.
- Data visualizations should feel calm and authoritative.
- Avoid emoji, fake illustrations, stock photos, vague abstract blobs, and glassmorphism.

## Homepage strategy

The homepage should not start as a wall of controls.

Preferred structure:
1. Editorial hero: what the atlas helps people decide.
2. Trust strip: public data, reproducible, county-level, not credit/underwriting.
3. Main map workbench: map + county search + selected county explanation.
4. “How to read the signal” as a compact explanatory module.
5. Example county cards that show real use cases.
6. Methodology/sources CTA for skeptical users.

## County brief strategy

County pages should feel like readable public-data briefs, not generated metric dumps.

Preferred structure:
1. Top answer panel: signal, data quality, strongest drivers, recommended next step.
2. Driver cards grouped by human meaning:
   - Main Street business base
   - Capital-access visibility
   - Community stress / housing pressure
   - Support ecosystem gap
3. “Questions to verify locally” should be prominent.
4. Data quality and limitations should be visible but not visually dominant.
5. Avoid overloading users with every metric at equal weight.

## Files likely involved

Primary frontend files:
- `site/templates/base.html`
- `site/templates/index.html`
- `site/templates/county.html`
- `site/templates/illinois.html`
- `site/templates/partials/county_card.html`
- `site/static/css/styles.css`
- `site/static/js/app.js`

Do not change scoring methodology, data calculations, source manifests, or generated data unless the task explicitly asks for it.

## Engineering constraints

This is a Python/Jinja static site generated for GitHub Pages.
The package uses Python 3.11+, Jinja2, pandas, pydantic, pyshp, requests, pytest, and ruff.
Prefer no new production dependencies unless explicitly approved.

Validation commands:
- `make all`
- `make test`
- `make serve`

If `make` is unavailable:
- `python -m mainstreet_atlas.cli all`
- `python -m http.server 8000 -d site/dist`

## Design acceptance criteria

Before finishing a frontend task, verify:

- The homepage works at 375px, 768px, and 1280px widths.
- The map/search flow is still usable without confusing the user.
- Keyboard focus states remain visible.
- Color contrast remains accessible.
- The site still makes clear that this is not a credit model or underwriting tool.
- No generic AI filler copy was added.
- No made-up claims, statistics, logos, partner names, or testimonials were added.
- The final result feels like a credible civic-finance product, not an AI template.

## Review behavior

When asked to improve design:
1. First diagnose the current user experience.
2. Propose a design direction.
3. Make one focused change at a time.
4. Run available checks.
5. Summarize what changed and what still needs visual review.

If feedback says “this feels AI-generated,” treat that as a product/design critique, not a request for more decoration.
