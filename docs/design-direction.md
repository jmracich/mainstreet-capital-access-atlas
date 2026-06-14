# Design Direction

Main Street Capital Access Atlas is a high-trust civic-finance intelligence product. This document defines how the site should feel, read, and behave when templates, copy, CSS, maps, briefs, or visual patterns change.

This is source documentation for contributors. It does not change scoring methodology, source handling, generated data, templates, or public interfaces.

## Product Positioning

The atlas helps local partners decide where small-business support conversations should start. It turns public county-level data into readable Main Street Opportunity Briefs for local verification, partnership development, capital-navigation support, and community conversation.

The product is:

- Civic-finance intelligence, not generic SaaS analytics.
- A public-data starting point, not a verdict.
- A briefing tool, not a credit model or underwriting tool.
- Evidence-based and reproducible, not promotional.
- Warm enough for community use, serious enough for public-sector and financial-sector review.

The product should feel closer to Opportunity Atlas, a public-interest data lab, Bloomberg CityLab, or a Federal Reserve research note than to a startup landing page, nonprofit campaign page, or bank marketing site.

## Target Users

Design for people who need to ask better local questions before acting:

- CDFIs and mission-driven lenders.
- Chambers of commerce and small-business support teams.
- Local governments and economic-development staff.
- Libraries, universities, extension programs, and student volunteers.
- Nonprofits and community development organizations.
- Banks doing community engagement or capital-access work.
- Philanthropy and regional funders.
- Researchers, journalists, and public-interest technologists.
- Local partners who know context the data cannot show.

These users are often scanning under time pressure. They need a credible starting point, clear caveats, and a next step they can explain to someone else.

## Core User Jobs

Every page, section, component, and interaction should help answer at least one of these jobs:

1. Where should I start looking?
2. Why does this county need follow-up?
3. Can I trust this data?
4. What should I verify locally?
5. What should I do next?

If a section does not answer one of these questions, simplify it, merge it, or remove it.

## Homepage Narrative

The homepage should not begin as a wall of controls. It should stage the product from public-interest purpose to practical exploration.

Use this hierarchy:

1. Editorial hero: explain what the atlas helps people decide. Lead with the decision, not the score.
2. Trust strip: state that the site uses public data, is reproducible, county-level, and not credit or underwriting.
3. Main map workbench: show the county map, county search, and selected-county explanation as the primary instrument.
4. How to read the signal: explain that the 0-100 signal is a follow-up prompt, not a grade or ranking of community worth.
5. Example county use cases: show a few real contexts that demonstrate how different counties should be interpreted.
6. Methodology and sources CTA: give skeptical users a clear path to scoring logic, limitations, data quality, and source vintage.

The strongest homepage story is:

> Use public data to find counties worth a closer look. Open a readable brief. See why the signal appears. Check data quality. Bring specific questions to local partners.

Avoid making the homepage feel like a data product proving it has many widgets. It should feel like a public briefing that happens to include a working map.

## County Brief Narrative

County pages should read like public-data briefs, not generated metric dumps.

Use this hierarchy:

1. Top answer panel: county name, support signal, data quality, strongest drivers, and recommended next step.
2. Why this county needs follow-up: summarize the most important public-data signals in plain language.
3. What to verify locally: make local partner questions prominent near the top of the brief.
4. Driver groups: organize evidence by human meaning:
   - Main Street business base.
   - Capital-access visibility.
   - Community stress and housing pressure.
   - Support ecosystem gap.
5. Data quality and limitations: keep them visible, but do not let them overpower the reader's first path.
6. Source trust path: provide source vintage, missingness, and methodology links for users who need to audit the brief.

Do not give every metric equal weight. Population, establishment count, branch count, source coverage, poverty, CRA/SBA signals, and CDFI counts are not the same kind of decision evidence. The design should make that hierarchy obvious.

## Visual Language

The visual style should be restrained, premium, civic, and evidence-based:

- Warm neutral page backgrounds.
- Deep ink text.
- Civic teal for primary action and map emphasis.
- Amber for caution, interpretation, or secondary emphasis.
- Soft data-map colors that support scanning without alarmism.
- Calm tables, restrained borders, and clear hierarchy.
- More whitespace and editorial pacing.
- Fewer boxed cards.

Use contrast, scale, spacing, typography, and rhythm before decoration. The map and county briefs are working instruments. They should not feel like decorative dashboard panels.

The site should look credible when shown to a CDFI director, city economic-development staff member, local banker, chamber leader, or public-interest researcher.

## Typography Principles

Typography should create editorial hierarchy and improve scan speed:

- Use larger editorial headings for major page claims and section transitions.
- Keep body copy plain, careful, and specific.
- Use short labels for data fields and longer explanatory text only where interpretation is needed.
- Avoid oversized type inside compact cards, tables, sidebars, or metric groups.
- Avoid generic slogan language.
- Do not use negative letter spacing.
- Do not scale font size directly with viewport width.
- Use tabular numbers for numeric comparisons where appropriate.

Copy should be cautious without becoming repetitive. The site must preserve the "not credit / not underwriting" framing, but the same disclaimer should not appear in the same form across every nearby section.

## Color Principles

Color should support trust and interpretation:

- Primary background: muted warm off-white or light civic neutral.
- Primary text: deep ink, not pure black.
- Primary accent: civic teal.
- Secondary accent: amber or muted gold.
- Data colors: calm sequential ramps with accessible contrast.
- Error or unavailable states: quiet warning colors, not aggressive red unless the user must act.

Do not rely on color alone to communicate meaning. Signal bands, grades, source status, and selected states need text labels or structural cues.

Avoid one-note palettes. The site should not become dominated by purple, neon blue, beige, brown, orange, or dark slate. Gradients should be rare and never carry the product identity.

## Component Principles

Components should clarify decisions, not merely display available fields.

Use components this way:

- Hero: state the core decision the atlas supports.
- Trust strip: establish source, reproducibility, and limitations quickly.
- Map workbench: support exploration, search, selection, and brief opening.
- Selected-county panel: explain whether the county deserves follow-up and why.
- Score explainer: define score meaning and misuse boundaries.
- County cards: show a real use case or comparison, not just repeated metrics.
- Tables: serve fallback, audit, and comparison workflows.
- Driver groups: explain evidence by human meaning, not by raw source table shape.
- Data quality panels: help users decide how much confidence to place in a brief.
- CTAs: move users to methodology, sources, limitations, or a county brief.

Avoid nested cards, card-heavy page sections, decorative panels, and equal-weight metric grids when an answer panel, table, or narrative grouping would be clearer.

Map popups should be brief. They should help the user decide whether to open a county brief, not duplicate the full brief.

## Forbidden AI-Generated Patterns

Do not use:

- Neon gradients, purple-blue gradient themes, or glossy SaaS backgrounds.
- Glassmorphism.
- Abstract blobs, bokeh, floating orbs, and decorative SVG waves.
- Fake civic illustrations or generic stock photos.
- Vague "empower communities" copy.
- Invented claims, statistics, partner names, testimonials, or logos.
- Crypto-dashboard styling.
- Banking sales language.
- Dribbble-style polish that reduces usability.
- Repeated cards that differ only by metric labels.
- Metric dumps where every field receives equal visual priority.
- Chatty AI filler, motivational slogans, or exaggerated transformation language.
- Icons or decorative marks that imply official sponsorship or institutional endorsement.

If a design starts to look impressive before it looks trustworthy, reduce decoration and strengthen hierarchy.

## Accessibility Requirements

Accessibility is part of the design bar:

- Preserve semantic HTML landmarks, headings, lists, tables, and links.
- Keep keyboard focus visible for links, buttons, inputs, map-adjacent controls, and mobile navigation.
- Keep non-map alternatives available, including search, tables, generated county briefs, downloadable data, and `noscript` fallback content.
- Check responsive behavior at 375px, 768px, and 1280px before accepting frontend changes.
- Avoid horizontal overflow.
- Maintain readable touch targets on mobile.
- Keep color contrast accessible for text, controls, labels, badges, and map-adjacent interpretation.
- Do not rely on color alone for score bands, source status, selected counties, or grades.
- Keep limitations and source context visible without forcing users through the interactive map.
- Do not add accounts, tracking scripts, private data collection, or paid-service dependencies for core access.

Any design change that affects map interaction, search, navigation, tables, or county briefs needs manual keyboard and viewport checks in addition to automated tests.

## Before And After Visual Review Checklist

Use this checklist before accepting a visual change.

Before:

- Identify which user job the change improves.
- Confirm the change does not alter scoring methodology, source manifests, generated data, or public calculations unless explicitly intended.
- Confirm the page still says or clearly implies that the atlas is not a credit model or underwriting tool.
- Identify whether any existing useful section is being removed, merged, or de-emphasized.
- Check whether the proposed design relies on decoration instead of hierarchy.

After:

- The homepage has a clear editorial opening before dense controls.
- The map/search flow remains usable and understandable.
- County brief pages provide a top answer before detailed metric groups.
- Local verification questions are prominent where the reader needs them.
- Data quality and limitations are visible but not visually dominant.
- Tables support comparison or audit workflows rather than competing with the main narrative.
- Repeated cards have been reduced or given distinct reader value.
- Copy is specific to public data, county briefs, local verification, and small-business support.
- No generic AI filler, invented claims, fake testimonials, logos, or partner names were added.
- Color contrast, keyboard focus, and non-map alternatives remain intact.
- The result feels like a credible civic-finance product, not an AI template.

## Repo Surfaces This Applies To

Primary frontend surfaces:

- `site/templates/base.html`
- `site/templates/index.html`
- `site/templates/county.html`
- `site/templates/illinois.html`
- `site/templates/partials/county_card.html`
- `site/static/css/styles.css`
- `site/static/js/app.js`

Documentation and release review should stay consistent with:

- `README.md`
- `docs/accessibility.md`
- `docs/methodology.md`
- `docs/limitations.md`
- `docs/release_checklist.md`

Future frontend work should use this document as the design-system reference before changing templates or CSS.
